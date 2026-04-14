"""Build backend contracts and command planning."""

from __future__ import annotations

from ..config.constants import CPP_WORKFLOW_KIND
from ..config.models import BuildConfig, CppBuildConfig, PythonBuildConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import (
    BackendContract,
    BuildRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import BUILD_CMAKE, BUILD_PYTHON

BuildBackendConfig = CppBuildConfig | PythonBuildConfig
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
        targets: Optional explicit C++ build targets that override the
            configured defaults.

    Returns:
        Prepared command specs for each configured build backend.
    """

    specs: list[CommandSpec] = []
    for build_config in config.configured_backends(selection):
        contract = require_backend_contract(
            "build", build_config.backend, BUILD_BACKENDS
        )
        contract.validate(build_config)
        specs.extend(
            contract.plan(
                build_config,
                BuildRequest(targets=targets),
            )
        )
    return WorkflowPlan(specs=specs)


def _cmake_plan(config: CppBuildConfig, request: BuildRequest) -> list[CommandSpec]:
    """Build CMake configure and build commands for a C++ workflow.

    Args:
        config: Parsed C++ build configuration.
        request: Build planning options.

    Returns:
        Command specs for the configure step and one or more build steps.
    """
    pre_hooks, post_hooks = split_hooks(config.hooks, CPP_WORKFLOW_KIND)
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


def _validate_cpp_build(config: BuildBackendConfig) -> None:
    """Validate the C++ build contract input.

    Args:
        config: Parsed build backend configuration.

    Raises:
        ConfigError: If the config is not a C++ build configuration.
    """

    if not isinstance(config, CppBuildConfig):
        raise ConfigError("The `cmake` backend requires a C++ build configuration")


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
    BUILD_CMAKE: BackendContract(
        name=BUILD_CMAKE,
        validate=_validate_cpp_build,
        plan=_cmake_plan,
    ),
    BUILD_PYTHON: BackendContract(
        name=BUILD_PYTHON,
        validate=_validate_python_build,
        plan=_python_build_plan,
    ),
}
