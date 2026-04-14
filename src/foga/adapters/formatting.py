"""Format backend contracts and command planning."""

from __future__ import annotations

from ..config.models import FormatTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, ToolRequest, WorkflowPlan


def plan_format(project_root, targets: list[FormatTargetConfig]) -> WorkflowPlan:
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
        contract = _format_contract(target.backend)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def supported_format_backends() -> set[str]:
    """Return the registered format backend names.

    Returns:
        Set of supported format backend identifiers.
    """

    return set(FORMAT_BACKENDS)


def validate_format_backend(config: FormatTargetConfig) -> None:
    """Validate a configured format backend through the registry contract.

    Args:
        config: Parsed format target configuration.
    """

    _format_contract(config.backend).validate(config)


def _format_contract(
    backend: str,
) -> BackendContract[FormatTargetConfig, ToolRequest]:
    """Resolve a registered format backend contract.

    Args:
        backend: Requested format backend identifier.

    Returns:
        Backend contract for the requested formatter.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return FORMAT_BACKENDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(FORMAT_BACKENDS))
        raise ConfigError(
            f"Unsupported format backend: {backend}",
            hint=f"Choose one of the supported format backends: {supported}.",
        ) from exc


def _black_plan(config: FormatTargetConfig, request: ToolRequest) -> list[CommandSpec]:
    """Build the black command for a format target.

    Args:
        config: Parsed format target configuration.
        request: Shared tool execution request context.

    Returns:
        Command specs for the configured ``black`` target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=["black", *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=f"black formatter `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _ruff_format_plan(
    config: FormatTargetConfig, request: ToolRequest
) -> list[CommandSpec]:
    """Build the ``ruff format`` command for a format target.

    Args:
        config: Parsed format target configuration.
        request: Shared tool execution request context.

    Returns:
        Command specs for the configured ``ruff-format`` target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=["ruff", "format", *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=f"ruff formatter `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _clang_format_plan(
    config: FormatTargetConfig, request: ToolRequest
) -> list[CommandSpec]:
    """Build the ``clang-format`` command for a format target.

    Args:
        config: Parsed format target configuration.
        request: Shared tool execution request context.

    Returns:
        Command specs for the configured ``clang-format`` target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=["clang-format", "-i", *config.args, *config.paths],
            cwd=request.project_root,
            env=config.env,
            description=f"clang-format target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_paths(config: FormatTargetConfig, workflow: str) -> None:
    """Validate path-based formatter configuration.

    Args:
        config: Parsed format target configuration.
        workflow: Workflow section name used in error messages.

    Raises:
        ConfigError: If no paths are configured.
    """

    if not config.paths:
        raise ConfigError(f"`{workflow}.targets.{config.name}.paths` must not be empty")


def _validate_black(config: FormatTargetConfig) -> None:
    """Validate ``black`` format target configuration.

    Args:
        config: Parsed format target configuration.
    """

    _validate_paths(config, "format")


def _validate_ruff_format(config: FormatTargetConfig) -> None:
    """Validate ``ruff-format`` target configuration.

    Args:
        config: Parsed format target configuration.
    """

    _validate_paths(config, "format")


def _validate_clang_format(config: FormatTargetConfig) -> None:
    """Validate ``clang-format`` target configuration.

    Args:
        config: Parsed format target configuration.
    """

    _validate_paths(config, "format")


FORMAT_BACKENDS: dict[str, BackendContract[FormatTargetConfig, ToolRequest]] = {
    "black": BackendContract(
        name="black",
        validate=_validate_black,
        plan=_black_plan,
    ),
    "ruff-format": BackendContract(
        name="ruff-format",
        validate=_validate_ruff_format,
        plan=_ruff_format_plan,
    ),
    "clang-format": BackendContract(
        name="clang-format",
        validate=_validate_clang_format,
        plan=_clang_format_plan,
    ),
}
