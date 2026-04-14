"""Lint backend contracts and command planning."""

from __future__ import annotations

from ..config.models import LintTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, ToolRequest, WorkflowPlan


def plan_lint(project_root, targets: list[LintTargetConfig]) -> WorkflowPlan:
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
        contract = _lint_contract(target.backend)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def supported_lint_backends() -> set[str]:
    """Return the registered lint backend names.

    Returns:
        Set of supported lint backend identifiers.
    """

    return set(LINT_BACKENDS)


def validate_lint_backend(config: LintTargetConfig) -> None:
    """Validate a configured lint backend through the registry contract.

    Args:
        config: Parsed lint target configuration.
    """

    _lint_contract(config.backend).validate(config)


def _lint_contract(
    backend: str,
) -> BackendContract[LintTargetConfig, ToolRequest]:
    """Resolve a registered lint backend contract.

    Args:
        backend: Requested lint backend identifier.

    Returns:
        Backend contract for the requested linter.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return LINT_BACKENDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(LINT_BACKENDS))
        raise ConfigError(
            f"Unsupported lint backend: {backend}",
            hint=f"Choose one of the supported lint backends: {supported}.",
        ) from exc


def _ruff_check_plan(
    config: LintTargetConfig, request: ToolRequest
) -> list[CommandSpec]:
    """Build the ``ruff check`` command for a lint target.

    Args:
        config: Parsed lint target configuration.
        request: Shared tool execution request context.

    Returns:
        Command specs for the configured ``ruff-check`` target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=["ruff", "check", *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=f"ruff linter `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _clang_tidy_plan(
    config: LintTargetConfig, request: ToolRequest
) -> list[CommandSpec]:
    """Build the ``clang-tidy`` command for a lint target.

    Args:
        config: Parsed lint target configuration.
        request: Shared tool execution request context.

    Returns:
        Command specs for the configured ``clang-tidy`` target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=["clang-tidy", *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=f"clang-tidy target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_paths(config: LintTargetConfig) -> None:
    """Validate path-based linter configuration.

    Args:
        config: Parsed lint target configuration.

    Raises:
        ConfigError: If no paths are configured.
    """

    if not config.paths:
        raise ConfigError(f"`lint.targets.{config.name}.paths` must not be empty")


def _validate_ruff_check(config: LintTargetConfig) -> None:
    """Validate ``ruff-check`` target configuration.

    Args:
        config: Parsed lint target configuration.
    """

    _validate_paths(config)


def _validate_clang_tidy(config: LintTargetConfig) -> None:
    """Validate ``clang-tidy`` target configuration.

    Args:
        config: Parsed lint target configuration.
    """

    _validate_paths(config)


LINT_BACKENDS: dict[str, BackendContract[LintTargetConfig, ToolRequest]] = {
    "ruff-check": BackendContract(
        name="ruff-check",
        validate=_validate_ruff_check,
        plan=_ruff_check_plan,
    ),
    "clang-tidy": BackendContract(
        name="clang-tidy",
        validate=_validate_clang_tidy,
        plan=_clang_tidy_plan,
    ),
}
