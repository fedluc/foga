"""Structured parsing for foga configuration sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..adapters.build import validate_build_backend
from ..adapters.deploy import supported_deploy_backends, validate_deploy_backend
from ..adapters.testing import supported_test_backends, validate_test_backend
from ..errors import ConfigError
from .constants import NATIVE_WORKFLOW_KIND, PYTHON_WORKFLOW_KIND, WORKFLOW_KINDS
from .models import (
    BuildConfig,
    CleanConfig,
    DeployTargetConfig,
    FogaConfig,
    NativeBuildConfig,
    ProjectConfig,
    PythonBuildConfig,
    TestConfig,
    TestRunnerConfig,
)
from .values import (
    optional_str,
    parse_hooks,
    parse_workflow_selection,
    reject_unknown_keys,
    required_str,
    string_list,
    string_mapping,
    unsupported_backend_message,
)


def _parse_config(data: dict[str, Any], project_root: Path) -> FogaConfig:
    """Parse raw configuration data into typed config objects.

    Args:
        data: Raw merged configuration mapping.
        project_root: Directory containing the resolved config file.

    Returns:
        Fully parsed configuration object.

    Raises:
        ConfigError: If any top-level configuration section is malformed.
    """

    project = data.get("project") or {}
    if not isinstance(project, dict) or not project.get("name"):
        raise ConfigError("`project.name` is required")

    build = _parse_build(data.get("build") or {})
    tests = _parse_tests(data.get("test") or {})
    deploy = _parse_deploy(data.get("deploy") or {})
    clean = _parse_clean(data.get("clean") or {})

    return FogaConfig(
        project_root=project_root,
        project=ProjectConfig(name=str(project["name"])),
        build=build,
        tests=tests,
        deploy=deploy,
        clean=clean,
        raw=data,
    )


def _parse_build(data: dict[str, Any]) -> BuildConfig:
    """Parse build configuration for supported backends.

    Args:
        data: Raw build configuration mapping.

    Returns:
        Parsed build configuration.

    Raises:
        ConfigError: If the build section is malformed.
    """

    if not isinstance(data, dict):
        raise ConfigError("`build` must be a mapping")

    entries: dict[str, NativeBuildConfig | PythonBuildConfig] = {}
    native = None
    python_build = None
    default = parse_workflow_selection(data.get("default"), "build.default")

    for name, build_data in data.items():
        if name == "default":
            continue
        if name not in WORKFLOW_KINDS:
            raise ConfigError(
                f"`build.{name}` is not a supported build entry",
                hint=(
                    "Use `build.native` and/or `build.python` for "
                    "configured build workflows."
                ),
            )
        if not isinstance(build_data, dict):
            raise ConfigError(f"`build.{name}` must be a mapping")

        backend = optional_str(build_data, "backend", f"build.{name}.backend")
        if backend is None:
            continue

        supported_backends = _build_backends_for_entry(name)
        if backend not in supported_backends:
            raise ConfigError(
                unsupported_backend_message("build", backend, supported_backends)
            )

        config = _parse_build_backend(name, build_data, backend)
        validate_build_backend(config)
        entries[name] = config
        if name == NATIVE_WORKFLOW_KIND and isinstance(config, NativeBuildConfig):
            native = config
        if name == PYTHON_WORKFLOW_KIND and isinstance(config, PythonBuildConfig):
            python_build = config

    return BuildConfig(
        default=default, entries=entries, native=native, python=python_build
    )


def _parse_build_backend(
    name: str, data: dict[str, Any], backend: str
) -> NativeBuildConfig | PythonBuildConfig:
    """Parse a configured build backend by backend type.

    Args:
        name: Build entry name from the config.
        data: Raw build entry mapping.
        backend: Validated backend identifier.

    Returns:
        Parsed native or Python build config.

    Raises:
        ConfigError: If the backend-specific configuration is invalid.
    """

    path = f"build.{name}"
    if backend == "cmake":
        return NativeBuildConfig(
            backend=backend,
            source_dir=required_str(data, "source_dir", f"{path}.source_dir"),
            build_dir=required_str(data, "build_dir", f"{path}.build_dir"),
            generator=optional_str(data, "generator", f"{path}.generator"),
            configure_args=string_list(
                data.get("configure_args"), f"{path}.configure_args"
            ),
            build_args=string_list(data.get("build_args"), f"{path}.build_args"),
            targets=string_list(data.get("targets"), f"{path}.targets"),
            env=string_mapping(data.get("env"), f"{path}.env"),
            hooks=parse_hooks(data.get("hooks"), f"{path}.hooks"),
        )

    if backend == "python-build":
        if "command" in data:
            raise ConfigError(
                f"`{path}.command` is not supported for the `python-build` backend; "
                "use `args` to pass extra flags"
            )
        return PythonBuildConfig(
            backend=backend,
            args=string_list(data.get("args"), f"{path}.args"),
            env=string_mapping(data.get("env"), f"{path}.env"),
            hooks=parse_hooks(data.get("hooks"), f"{path}.hooks"),
        )

    raise ConfigError(f"Unsupported build backend: {backend}")


def _parse_tests(data: dict[str, Any]) -> TestConfig:
    """Parse test runner configuration.

    Args:
        data: Raw test configuration mapping.

    Returns:
        Parsed test configuration.

    Raises:
        ConfigError: If the test section is malformed.
    """

    if not isinstance(data, dict):
        raise ConfigError("`test` must be a mapping")

    reject_unknown_keys(data, "test", {"default", "runners"})
    runners_data = data.get("runners") or {}
    if not isinstance(runners_data, dict):
        raise ConfigError("`test.runners` must be a mapping")

    default = parse_workflow_selection(data.get("default"), "test.default")
    supported_backends = supported_test_backends()
    runners: dict[str, TestRunnerConfig] = {}

    for name, runner_data in runners_data.items():
        if not isinstance(runner_data, dict):
            raise ConfigError(f"`test.runners.{name}` must be a mapping")

        backend = optional_str(runner_data, "backend", f"test.runners.{name}.backend")
        if backend is None:
            continue
        if backend not in supported_backends:
            raise ConfigError(
                unsupported_backend_message("test", backend, supported_backends)
            )

        runner = TestRunnerConfig(
            name=name,
            backend=backend,
            args=string_list(runner_data.get("args"), f"test.runners.{name}.args"),
            env=string_mapping(runner_data.get("env"), f"test.runners.{name}.env"),
            hooks=parse_hooks(runner_data.get("hooks"), f"test.runners.{name}.hooks"),
            path=optional_str(runner_data, "path", f"test.runners.{name}.path"),
            marker=optional_str(runner_data, "marker", f"test.runners.{name}.marker"),
            tox_env=optional_str(
                runner_data, "tox_env", f"test.runners.{name}.tox_env"
            ),
            build_dir=optional_str(
                runner_data, "build_dir", f"test.runners.{name}.build_dir"
            ),
            source_dir=optional_str(
                runner_data, "source_dir", f"test.runners.{name}.source_dir"
            ),
            generator=optional_str(
                runner_data, "generator", f"test.runners.{name}.generator"
            ),
            configure_args=string_list(
                runner_data.get("configure_args"),
                f"test.runners.{name}.configure_args",
            ),
            build_args=string_list(
                runner_data.get("build_args"), f"test.runners.{name}.build_args"
            ),
            target=optional_str(runner_data, "target", f"test.runners.{name}.target"),
        )
        validate_test_backend(runner)
        runners[name] = runner

    return TestConfig(default=default, runners=runners)


def _parse_deploy(data: dict[str, Any]) -> dict[str, DeployTargetConfig]:
    """Parse deploy target configuration.

    Args:
        data: Raw deploy configuration mapping.

    Returns:
        Parsed deploy targets keyed by target name.

    Raises:
        ConfigError: If the deploy section is malformed.
    """

    if not isinstance(data, dict):
        raise ConfigError("`deploy` must be a mapping")

    reject_unknown_keys(data, "deploy", {"targets"})
    targets_data = data.get("targets") or {}
    if not isinstance(targets_data, dict):
        raise ConfigError("`deploy.targets` must be a mapping")

    supported_backends = supported_deploy_backends()
    targets: dict[str, DeployTargetConfig] = {}
    for name, target_data in targets_data.items():
        if not isinstance(target_data, dict):
            raise ConfigError(f"`deploy.targets.{name}` must be a mapping")

        backend = required_str(target_data, "backend", f"deploy.targets.{name}.backend")
        if backend not in supported_backends:
            raise ConfigError(
                unsupported_backend_message("deploy", backend, supported_backends)
            )

        target = DeployTargetConfig(
            name=name,
            backend=backend,
            artifacts=string_list(
                target_data.get("artifacts"), f"deploy.targets.{name}.artifacts"
            ),
            repository=optional_str(
                target_data, "repository", f"deploy.targets.{name}.repository"
            ),
            repository_url=optional_str(
                target_data,
                "repository_url",
                f"deploy.targets.{name}.repository_url",
            ),
            args=string_list(target_data.get("args"), f"deploy.targets.{name}.args"),
            env=string_mapping(target_data.get("env"), f"deploy.targets.{name}.env"),
            hooks=parse_hooks(target_data.get("hooks"), f"deploy.targets.{name}.hooks"),
        )
        validate_deploy_backend(target)
        targets[name] = target

    return targets


def _parse_clean(data: dict[str, Any]) -> CleanConfig:
    """Parse clean-path configuration.

    Args:
        data: Raw clean configuration mapping.

    Returns:
        Parsed clean configuration.

    Raises:
        ConfigError: If the clean section is malformed.
    """

    if not isinstance(data, dict):
        raise ConfigError("`clean` must be a mapping")
    return CleanConfig(paths=string_list(data.get("paths"), "clean.paths"))


def _build_backends_for_entry(name: str) -> set[str]:
    """Return the supported build backends for a specific build entry.

    Args:
        name: Build entry name from the config.

    Returns:
        Set of supported backend identifiers for the entry.

    Raises:
        ConfigError: If the build entry name is unsupported.
    """

    if name == NATIVE_WORKFLOW_KIND:
        return {"cmake"}
    if name == PYTHON_WORKFLOW_KIND:
        return {"python-build"}
    raise ConfigError(f"`build.{name}` is not a supported build entry")
