"""Build backend contracts and command planning."""

from __future__ import annotations

from collections.abc import Callable

from ..config.constants import BUILD_SECTION, CPP_WORKFLOW_KIND
from ..config.models import (
    BuildConfig,
    CppBuildConfig,
    MesonBuildConfig,
    PythonBuildConfig,
)
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import prepend_launcher, split_hooks
from .contracts import (
    BackendContract,
    BuildRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import BUILD_CMAKE, BUILD_MESON, BUILD_PYTHON

BuildBackendConfig = CppBuildConfig | MesonBuildConfig | PythonBuildConfig
CppLikeBuildConfig = CppBuildConfig | MesonBuildConfig
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
            BUILD_SECTION, build_config.backend, BUILD_BACKENDS
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
    command = ["cmake", "-S", config.source_dir, "-B", config.build_dir]
    if config.generator:
        command.extend(["-G", config.generator])
    command.extend(config.configure_args)
    build_command = ["cmake", "--build", config.build_dir, "--parallel"]
    build_command.extend(config.build_args)
    return _plan_cpp_build_workflow(
        config=config,
        request=request,
        setup_command=command,
        setup_description="cmake configure",
        build_command=build_command,
        build_description="cmake build",
        target_command=lambda target: build_command + ["--target", target],
        target_description=lambda target: f"cmake build target `{target}`",
    )


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
            command=prepend_launcher(
                PYTHON_BUILD_COMMAND + config.args, config.launcher
            ),
            env=config.env,
            description="python package build",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _meson_plan(config: MesonBuildConfig, request: BuildRequest) -> list[CommandSpec]:
    """Build Meson setup and compile commands for a C++ workflow.

    Args:
        config: Parsed Meson build configuration.
        request: Build planning options.

    Returns:
        Command specs for the setup step and one or more compile steps.
    """
    setup_command = [
        *config.command,
        "setup",
        config.build_dir,
        config.source_dir,
        *config.setup_args,
    ]
    compile_command = [
        *config.command,
        "compile",
        "-C",
        config.build_dir,
        *config.compile_args,
    ]
    return _plan_cpp_build_workflow(
        config=config,
        request=request,
        setup_command=setup_command,
        setup_description="meson setup",
        build_command=compile_command,
        build_description="meson compile",
        target_command=lambda target: compile_command + [target],
        target_description=lambda target: f"meson compile target `{target}`",
    )


def _plan_cpp_build_workflow(
    *,
    config: CppLikeBuildConfig,
    request: BuildRequest,
    setup_command: list[str],
    setup_description: str,
    build_command: list[str],
    build_description: str,
    target_command: Callable[[str], list[str]],
    target_description: Callable[[str], str],
) -> list[CommandSpec]:
    """Build command specs for C++ backends with setup and build phases."""

    pre_hooks, post_hooks = split_hooks(config.hooks, CPP_WORKFLOW_KIND)
    specs = pre_hooks + [
        CommandSpec(
            command=prepend_launcher(setup_command, config.launcher),
            env=config.env,
            description=setup_description,
        )
    ]

    active_targets = request.targets if request.targets else config.targets
    if active_targets:
        for target in active_targets:
            specs.append(
                CommandSpec(
                    command=prepend_launcher(
                        target_command(target),
                        config.launcher,
                    ),
                    env=config.env,
                    description=target_description(target),
                )
            )
    else:
        specs.append(
            CommandSpec(
                command=prepend_launcher(build_command, config.launcher),
                env=config.env,
                description=build_description,
            )
        )

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


def _validate_meson_build(config: BuildBackendConfig) -> None:
    """Validate the Meson build contract input.

    Args:
        config: Parsed build backend configuration.

    Raises:
        ConfigError: If the config is not a Meson build configuration.
    """

    if not isinstance(config, MesonBuildConfig):
        raise ConfigError("The `meson` backend requires a Meson build configuration")


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
    BUILD_MESON: BackendContract(
        name=BUILD_MESON,
        validate=_validate_meson_build,
        plan=_meson_plan,
    ),
    BUILD_PYTHON: BackendContract(
        name=BUILD_PYTHON,
        validate=_validate_python_build,
        plan=_python_build_plan,
    ),
}
