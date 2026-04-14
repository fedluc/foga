"""Format backend contracts and command planning."""

from __future__ import annotations

from ..config.models import FormatTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, ToolRequest, WorkflowPlan


def plan_format(project_root, targets: list[FormatTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured format targets."""

    specs: list[CommandSpec] = []
    request = ToolRequest(project_root=project_root)
    for target in targets:
        contract = _format_contract(target.backend)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def supported_format_backends() -> set[str]:
    """Return the registered format backend names."""

    return set(FORMAT_BACKENDS)


def validate_format_backend(config: FormatTargetConfig) -> None:
    """Validate a configured format backend through the registry contract."""

    _format_contract(config.backend).validate(config)


def _format_contract(
    backend: str,
) -> BackendContract[FormatTargetConfig, ToolRequest]:
    """Resolve a registered format backend contract."""

    try:
        return FORMAT_BACKENDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(FORMAT_BACKENDS))
        raise ConfigError(
            f"Unsupported format backend: {backend}",
            hint=f"Choose one of the supported format backends: {supported}.",
        ) from exc


def _black_plan(config: FormatTargetConfig, request: ToolRequest) -> list[CommandSpec]:
    """Build the black command for a format target."""

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
    """Build the ruff format command for a format target."""

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
    """Build the clang-format command for a format target."""

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
    """Validate path-based formatter configuration."""

    if not config.paths:
        raise ConfigError(f"`{workflow}.targets.{config.name}.paths` must not be empty")


def _validate_black(config: FormatTargetConfig) -> None:
    """Validate black format target configuration."""

    _validate_paths(config, "format")


def _validate_ruff_format(config: FormatTargetConfig) -> None:
    """Validate ruff format target configuration."""

    _validate_paths(config, "format")


def _validate_clang_format(config: FormatTargetConfig) -> None:
    """Validate clang-format target configuration."""

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
