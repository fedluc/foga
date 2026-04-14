"""Format backend contracts and command planning."""

from __future__ import annotations

from functools import partial
from glob import has_magic
from pathlib import Path

from ..config.constants import FORMAT_SECTION, TARGETS_KEY
from ..config.models import FormatTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import (
    BackendContract,
    ToolRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import FORMAT_BLACK, FORMAT_CLANG, FORMAT_RUFF


def plan_format(project_root: Path, targets: list[FormatTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured format targets.

    Args:
        project_root: Project root used as the command working directory.
        targets: Parsed format targets selected for execution.

    Returns:
        Planned command specs for all selected format targets.
    """

    specs: list[CommandSpec] = []
    request = ToolRequest(project_root=project_root)
    for target in targets:
        contract = require_backend_contract(
            FORMAT_SECTION, target.backend, FORMAT_BACKENDS
        )
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def _plan_path_target(
    config: FormatTargetConfig,
    request: ToolRequest,
    *,
    command_prefix: tuple[str, ...],
    description_template: str,
) -> list[CommandSpec]:
    """Build a formatter command for backends that accept path lists.

    Args:
        config: Parsed formatter target configuration.
        request: Shared tool request with the project root.
        command_prefix: Base formatter command inserted before args and paths.
        description_template: User-facing step description template.

    Returns:
        Command specs for the selected formatter target, including hooks.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    resolved_paths = _resolve_format_paths(request.project_root, config)
    specs = pre_hooks + [
        CommandSpec(
            command=[*command_prefix, *config.args, *resolved_paths],
            cwd=request.project_root,
            env=config.env,
            description=description_template.format(name=config.name),
        )
    ]
    specs.extend(post_hooks)
    return specs


def _resolve_format_paths(project_root: Path, config: FormatTargetConfig) -> list[str]:
    """Resolve configured format paths, expanding glob patterns when present.

    Args:
        project_root: Project root used to resolve glob patterns.
        config: Parsed formatter target configuration.

    Returns:
        Ordered formatter paths with glob matches expanded.

    Raises:
        ConfigError: If a configured glob pattern matches no filesystem paths.
    """

    resolved_paths: list[str] = []
    seen_paths: set[str] = set()

    for pattern in config.paths:
        expanded_paths = _expand_path_pattern(project_root, config.name, pattern)
        for path in expanded_paths:
            if path in seen_paths:
                continue
            resolved_paths.append(path)
            seen_paths.add(path)

    return resolved_paths


def _expand_path_pattern(
    project_root: Path, target_name: str, pattern: str
) -> list[str]:
    """Expand one configured formatter path or glob pattern.

    Args:
        project_root: Project root used to resolve glob patterns.
        target_name: Formatter target name used in validation errors.
        pattern: Configured path or glob pattern.

    Returns:
        Literal path when no glob syntax is present, otherwise sorted glob
        matches rendered relative to the project root when possible.

    Raises:
        ConfigError: If a glob pattern matches no filesystem paths.
    """

    if not has_magic(pattern):
        return [pattern]

    matches = sorted(project_root.glob(pattern))
    if not matches:
        raise ConfigError(
            "No format paths matched the configured glob pattern",
            details={"Pattern": pattern},
            hint=(
                f"Adjust `{FORMAT_SECTION}.{TARGETS_KEY}.{target_name}.paths` "
                "or ensure matching files exist."
            ),
        )

    return [_display_path(project_root, match) for match in matches]


def _display_path(project_root: Path, path: Path) -> str:
    """Render a resolved formatter path for command-line use.

    Args:
        project_root: Project root used as the command working directory.
        path: Resolved filesystem path.

    Returns:
        Path relative to the project root when possible, otherwise the absolute
        path string.
    """

    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def _validate_paths(config: FormatTargetConfig, *, workflow: str) -> None:
    """Validate path-based formatter configuration.

    Args:
        config: Parsed formatter target configuration.
        workflow: Workflow section name used in validation errors.

    Raises:
        ConfigError: If no formatter paths are configured.
    """

    if not config.paths:
        raise ConfigError(f"`{workflow}.targets.{config.name}.paths` must not be empty")


FORMAT_BACKENDS: dict[str, BackendContract[FormatTargetConfig, ToolRequest]] = {
    FORMAT_BLACK: BackendContract(
        name=FORMAT_BLACK,
        validate=partial(_validate_paths, workflow=FORMAT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=(FORMAT_BLACK,),
            description_template="black formatter `{name}`",
        ),
    ),
    FORMAT_RUFF: BackendContract(
        name=FORMAT_RUFF,
        validate=partial(_validate_paths, workflow=FORMAT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=("ruff", "format"),
            description_template="ruff formatter `{name}`",
        ),
    ),
    FORMAT_CLANG: BackendContract(
        name=FORMAT_CLANG,
        validate=partial(_validate_paths, workflow=FORMAT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=(FORMAT_CLANG, "-i"),
            description_template="clang-format target `{name}`",
        ),
    ),
}
