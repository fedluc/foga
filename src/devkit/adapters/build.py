"""Build backend contracts and command planning."""

from __future__ import annotations

from ..config import BuildConfig, NativeBuildConfig, PythonBuildConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, BuildRequest, WorkflowPlan

BuildBackendConfig = NativeBuildConfig | PythonBuildConfig


def plan_build(config: BuildConfig, targets: list[str] | None = None) -> WorkflowPlan:
    """Build a workflow plan for all configured build backends."""

    specs: list[CommandSpec] = []
    for build_config in config.configured_backends():
        validate_build_backend(build_config)
        contract = _build_contract(build_config.backend)
        specs.extend(contract.plan(build_config, BuildRequest(targets=targets)))
    return WorkflowPlan(specs=specs)


def build_specs(
    config: BuildConfig, targets: list[str] | None = None
) -> list[CommandSpec]:
    """Build command specs for configured build workflows.

    Args:
        config: Parsed build configuration.
        targets: Optional explicit native build targets.

    Returns:
        Command specs for the configured build workflow.
    """
    return plan_build(config, targets=targets).specs


def supported_build_backends() -> set[str]:
    """Return the registered build backend names."""

    return set(BUILD_BACKENDS)


def _build_contract(backend: str) -> BackendContract[BuildBackendConfig, BuildRequest]:
    """Resolve a registered build backend contract."""

    try:
        return BUILD_BACKENDS[backend]
    except KeyError as exc:
        raise ConfigError(f"Unsupported build backend: {backend}") from exc


def validate_build_backend(config: BuildBackendConfig) -> None:
    """Validate a configured build backend through the registry contract."""

    _build_contract(config.backend).validate(config)


def _cmake_plan(config: NativeBuildConfig, request: BuildRequest) -> list[CommandSpec]:
    """Build CMake configure and build commands for a native workflow.

    Args:
        config: Parsed native build configuration.
        request: Build planning options.

    Returns:
        Command specs for the configure step and one or more build steps.
    """
    pre_hooks, post_hooks = split_hooks(config.hooks, "native")
    command = [
        "cmake",
        "-S",
        config.source_dir,
        "-B",
        config.build_dir,
    ]
    if config.generator:
        command.extend(["-G", config.generator])
    command.extend(config.configure_args)

    specs = pre_hooks + [
        CommandSpec(command=command, env=config.env, description="cmake configure")
    ]

    active_targets = request.targets if request.targets else config.targets
    build_command = [
        "cmake",
        "--build",
        config.build_dir,
        "--parallel",
    ]
    build_command.extend(config.build_args)
    if active_targets:
        for target in active_targets:
            specs.append(
                CommandSpec(
                    command=build_command + ["--target", target],
                    env=config.env,
                    description=f"cmake build target `{target}`",
                )
            )
    else:
        specs.append(
            CommandSpec(
                command=build_command, env=config.env, description="cmake build"
            )
        )
    specs.extend(post_hooks)
    return specs


def _python_build_plan(config: PythonBuildConfig, _: BuildRequest) -> list[CommandSpec]:
    """Build commands for the Python package build backend."""

    pre_hooks, post_hooks = split_hooks(config.hooks, "python build")
    specs = pre_hooks + [
        CommandSpec(
            command=config.command + config.args,
            env=config.env,
            description="python package build",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_native_build(config: BuildBackendConfig) -> None:
    """Validate the native build contract input."""

    if not isinstance(config, NativeBuildConfig):
        raise ConfigError("The `cmake` backend requires a native build configuration")


def _validate_python_build(config: BuildBackendConfig) -> None:
    """Validate the Python build contract input."""

    if not isinstance(config, PythonBuildConfig):
        raise ConfigError(
            "The `python-build` backend requires a Python build configuration"
        )


BUILD_BACKENDS: dict[str, BackendContract[BuildBackendConfig, BuildRequest]] = {
    "cmake": BackendContract(
        name="cmake",
        validate=_validate_native_build,
        plan=_cmake_plan,
    ),
    "python-build": BackendContract(
        name="python-build",
        validate=_validate_python_build,
        plan=_python_build_plan,
    ),
}
