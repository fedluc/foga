"""Format backend contracts and command planning."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from ..config.constants import FORMAT_SECTION
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
    specs = pre_hooks + [
        CommandSpec(
            command=[*command_prefix, *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=description_template.format(name=config.name),
        )
    ]
    specs.extend(post_hooks)
    return specs


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
