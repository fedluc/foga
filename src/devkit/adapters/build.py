"""Build backend contracts and command planning."""

from __future__ import annotations

from ..config import BuildConfig, NativeBuildConfig, PythonBuildConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, BuildRequest, WorkflowPlan

BuildBackendConfig = NativeBuildConfig | PythonBuildConfig
PYTHON_BUILD_COMMAND = ["python3", "-m", "build"]


def plan_build(
    config: BuildConfig,
    selection: str | None = None,
    targets: list[str] | None = None,
) -> WorkflowPlan:
    """Build a workflow plan for all configured build backends.

    Args:
        config: Parsed build configuration for the current project.
        selection: Optional explicit build kind requested by the CLI.
        targets: Optional explicit native build targets that override the
            configured defaults.

    Returns:
        Prepared command specs for each configured build backend.
    """

    specs: list[CommandSpec] = []
    for build_config in config.configured_backends(selection):
        validate_build_backend(build_config)
        contract = _build_contract(build_config.backend)
        specs.extend(
            contract.plan(
                build_config,
                BuildRequest(targets=targets),
            )
        )
    return WorkflowPlan(specs=specs)


def supported_build_backends() -> set[str]:
    """Return the registered build backend names.

    Returns:
        Set of backend names accepted under the build configuration.
    """

    return set(BUILD_BACKENDS)


def _build_contract(backend: str) -> BackendContract[BuildBackendConfig, BuildRequest]:
    """Resolve a registered build backend contract.

    Args:
        backend: Configured build backend name.

    Returns:
        Registered backend contract for the requested backend.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return BUILD_BACKENDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(BUILD_BACKENDS))
        raise ConfigError(
            f"Unsupported build backend: {backend}",
            hint=f"Choose one of the supported build backends: {supported}.",
        ) from exc


def validate_build_backend(config: BuildBackendConfig) -> None:
    """Validate a configured build backend through the registry contract.

    Args:
        config: Parsed build backend configuration.

    Raises:
        ConfigError: If the configuration does not match the backend contract.
    """

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


def _python_build_plan(
    config: PythonBuildConfig, _request: BuildRequest
) -> list[CommandSpec]:
    """Build commands for the Python package build backend.

    Args:
        config: Parsed Python build configuration.
        _request: Unused build planning options required by the backend
            contract.

    Returns:
        Command specs for the Python build workflow.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, "python build")
    specs = pre_hooks + [
        CommandSpec(
            command=PYTHON_BUILD_COMMAND + config.args,
            env=config.env,
            description="python package build",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_native_build(config: BuildBackendConfig) -> None:
    """Validate the native build contract input.

    Args:
        config: Parsed build backend configuration.

    Raises:
        ConfigError: If the config is not a native build configuration.
    """

    if not isinstance(config, NativeBuildConfig):
        raise ConfigError("The `cmake` backend requires a native build configuration")


def _validate_python_build(config: BuildBackendConfig) -> None:
    """Validate the Python build contract input.

    Args:
        config: Parsed build backend configuration.

    Raises:
        ConfigError: If the config is not a Python build configuration.
    """

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
