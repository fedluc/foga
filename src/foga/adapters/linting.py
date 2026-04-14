"""Lint backend contracts and command planning."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from ..config.constants import LINT_SECTION
from ..config.models import LintTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import prepend_launcher, split_hooks
from .contracts import (
    BackendContract,
    ToolRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import LINT_CLANG, LINT_PYLINT, LINT_RUFF


def plan_lint(project_root: Path, targets: list[LintTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured lint targets.

    Args:
        project_root: Project root used as the command working directory.
        targets: Parsed lint targets selected for execution.

    Returns:
        Planned command specs for all selected lint targets.
    """

    specs: list[CommandSpec] = []
    request = ToolRequest(project_root=project_root)
    for target in targets:
        contract = require_backend_contract(LINT_SECTION, target.backend, LINT_BACKENDS)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def _plan_path_target(
    config: LintTargetConfig,
    request: ToolRequest,
    *,
    command_prefix: tuple[str, ...],
    description_template: str,
) -> list[CommandSpec]:
    """Build a linter command for backends that accept path lists.

    Args:
        config: Parsed linter target configuration.
        request: Shared tool request with the project root.
        command_prefix: Base linter command inserted before args and paths.
        description_template: User-facing step description template.

    Returns:
        Command specs for the selected lint target, including hooks.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=prepend_launcher(
                [*command_prefix, *config.args, *config.paths],
                config.launcher,
            ),
            cwd=request.project_root,
            env=config.env,
            description=description_template.format(name=config.name),
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_paths(config: LintTargetConfig, *, workflow: str) -> None:
    """Validate path-based linter configuration.

    Args:
        config: Parsed linter target configuration.
        workflow: Workflow section name used in validation errors.

    Raises:
        ConfigError: If no lint paths are configured.
    """

    if not config.paths:
        raise ConfigError(f"`{workflow}.targets.{config.name}.paths` must not be empty")


LINT_BACKENDS: dict[str, BackendContract[LintTargetConfig, ToolRequest]] = {
    LINT_RUFF: BackendContract(
        name=LINT_RUFF,
        validate=partial(_validate_paths, workflow=LINT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=("ruff", "check"),
            description_template="ruff linter `{name}`",
        ),
    ),
    LINT_PYLINT: BackendContract(
        name=LINT_PYLINT,
        validate=partial(_validate_paths, workflow=LINT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=(LINT_PYLINT,),
            description_template="pylint target `{name}`",
        ),
    ),
    LINT_CLANG: BackendContract(
        name=LINT_CLANG,
        validate=partial(_validate_paths, workflow=LINT_SECTION),
        plan=partial(
            _plan_path_target,
            command_prefix=(LINT_CLANG,),
            description_template="clang-tidy target `{name}`",
        ),
    ),
}
