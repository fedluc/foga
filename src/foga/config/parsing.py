"""Structured parsing for foga configuration sections."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

from ..adapters.build import BUILD_BACKENDS
from ..adapters.contracts import registered_backends, require_backend_contract
from ..adapters.deploy import DEPLOY_BACKENDS
from ..adapters.formatting import FORMAT_BACKENDS
from ..adapters.kinds import BUILD_CMAKE, BUILD_PYTHON
from ..adapters.linting import LINT_BACKENDS
from ..adapters.testing import TEST_BACKENDS
from ..errors import ConfigError
from .constants import CPP_WORKFLOW_KIND, PYTHON_WORKFLOW_KIND, WORKFLOW_KINDS
from .models import (
    BuildConfig,
    CleanConfig,
    CppBuildConfig,
    DeployTargetConfig,
    FogaConfig,
    FormatConfig,
    FormatTargetConfig,
    LintConfig,
    LintTargetConfig,
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

WorkflowTargetT = TypeVar("WorkflowTargetT")
WorkflowConfigT = TypeVar("WorkflowConfigT")


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
    formatters = _parse_format(data.get("format") or {})
    linters = _parse_lint(data.get("lint") or {})
    deploy = _parse_deploy(data.get("deploy") or {})
    clean = _parse_clean(data.get("clean") or {})

    return FogaConfig(
        project_root=project_root,
        project=ProjectConfig(name=str(project["name"])),
        build=build,
        tests=tests,
        formatters=formatters,
        linters=linters,
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

    entries: dict[str, CppBuildConfig | PythonBuildConfig] = {}
    cpp_build = None
    python_build = None
    default = parse_workflow_selection(data.get("default"), "build.default")

    for name, build_data in data.items():
        if name == "default":
            continue
        if name not in WORKFLOW_KINDS:
            raise ConfigError(
                f"`build.{name}` is not a supported build entry",
                hint=(
                    "Use `build.cpp` and/or `build.python` for "
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
        require_backend_contract("build", config.backend, BUILD_BACKENDS).validate(
            config
        )
        entries[name] = config
        if name == CPP_WORKFLOW_KIND and isinstance(config, CppBuildConfig):
            cpp_build = config
        if name == PYTHON_WORKFLOW_KIND and isinstance(config, PythonBuildConfig):
            python_build = config

    return BuildConfig(
        default=default, entries=entries, cpp=cpp_build, python=python_build
    )


def _parse_build_backend(
    name: str, data: dict[str, Any], backend: str
) -> CppBuildConfig | PythonBuildConfig:
    """Parse a configured build backend by backend type.

    Args:
        name: Build entry name from the config.
        data: Raw build entry mapping.
        backend: Validated backend identifier.

    Returns:
        Parsed C++ or Python build config.

    Raises:
        ConfigError: If the backend-specific configuration is invalid.
    """

    path = f"build.{name}"
    if backend == BUILD_CMAKE:
        return CppBuildConfig(
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

    if backend == BUILD_PYTHON:
        if "command" in data:
            raise ConfigError(
                f"`{path}.command` is not supported for the `{BUILD_PYTHON}` backend; "
                "use `args` to pass extra flags"
            )
        return PythonBuildConfig(
            backend=backend,
            args=string_list(data.get("args"), f"{path}.args"),
            env=string_mapping(data.get("env"), f"{path}.env"),
            hooks=parse_hooks(data.get("hooks"), f"{path}.hooks"),
        )

    raise ConfigError(f"Unsupported build backend: {backend}")


def _parse_named_workflow_config(
    data: dict[str, Any],
    *,
    section: str,
    entries_key: str,
    registry: dict[str, Any],
    build_target: Callable[[str, dict[str, Any], str, str], WorkflowTargetT],
    build_config: Callable[[str | None, dict[str, WorkflowTargetT]], WorkflowConfigT],
) -> WorkflowConfigT:
    """Parse workflow sections that map names to backend-configured targets."""

    if not isinstance(data, dict):
        raise ConfigError(f"`{section}` must be a mapping")

    reject_unknown_keys(data, section, {"default", entries_key})
    entries_data = data.get(entries_key) or {}
    if not isinstance(entries_data, dict):
        raise ConfigError(f"`{section}.{entries_key}` must be a mapping")

    default = parse_workflow_selection(data.get("default"), f"{section}.default")
    supported_backends = registered_backends(registry)
    targets: dict[str, WorkflowTargetT] = {}

    for name, target_data in entries_data.items():
        if not isinstance(target_data, dict):
            raise ConfigError(f"`{section}.{entries_key}.{name}` must be a mapping")

        backend_path = f"{section}.{entries_key}.{name}.backend"
        backend = optional_str(target_data, "backend", backend_path)
        if backend is None:
            continue
        if backend not in supported_backends:
            raise ConfigError(
                unsupported_backend_message(section, backend, supported_backends)
            )

        target = build_target(
            name, target_data, backend, f"{section}.{entries_key}.{name}"
        )
        require_backend_contract(section, backend, registry).validate(target)
        targets[name] = target

    return build_config(default, targets)


def _parse_path_target(
    target_type: Callable[..., WorkflowTargetT],
    name: str,
    data: dict[str, Any],
    backend: str,
    path: str,
) -> WorkflowTargetT:
    """Parse a path-based format or lint target."""

    return target_type(
        name=name,
        backend=backend,
        paths=string_list(data.get("paths"), f"{path}.paths"),
        args=string_list(data.get("args"), f"{path}.args"),
        env=string_mapping(data.get("env"), f"{path}.env"),
        hooks=parse_hooks(data.get("hooks"), f"{path}.hooks"),
    )


def _parse_test_runner(
    name: str,
    data: dict[str, Any],
    backend: str,
    path: str,
) -> TestRunnerConfig:
    """Parse a named test runner configuration."""

    return TestRunnerConfig(
        name=name,
        backend=backend,
        args=string_list(data.get("args"), f"{path}.args"),
        env=string_mapping(data.get("env"), f"{path}.env"),
        hooks=parse_hooks(data.get("hooks"), f"{path}.hooks"),
        path=optional_str(data, "path", f"{path}.path"),
        marker=optional_str(data, "marker", f"{path}.marker"),
        tox_env=optional_str(data, "tox_env", f"{path}.tox_env"),
        build_dir=optional_str(data, "build_dir", f"{path}.build_dir"),
        source_dir=optional_str(data, "source_dir", f"{path}.source_dir"),
        generator=optional_str(data, "generator", f"{path}.generator"),
        configure_args=string_list(
            data.get("configure_args"), f"{path}.configure_args"
        ),
        build_args=string_list(data.get("build_args"), f"{path}.build_args"),
        target=optional_str(data, "target", f"{path}.target"),
    )


def _parse_tests(data: dict[str, Any]) -> TestConfig:
    """Parse test runner configuration.

    Args:
        data: Raw test configuration mapping.

    Returns:
        Parsed test configuration.

    Raises:
        ConfigError: If the test section is malformed.
    """

    return _parse_named_workflow_config(
        data,
        section="test",
        entries_key="runners",
        registry=TEST_BACKENDS,
        build_target=_parse_test_runner,
        build_config=lambda default, runners: TestConfig(
            default=default,
            runners=runners,
        ),
    )


def _parse_format(data: dict[str, Any]) -> FormatConfig:
    """Parse format target configuration.

    Args:
        data: Raw ``format`` section mapping.

    Returns:
        Parsed format configuration.

    Raises:
        ConfigError: If the format section is malformed.
    """

    return _parse_named_workflow_config(
        data,
        section="format",
        entries_key="targets",
        registry=FORMAT_BACKENDS,
        build_target=lambda name, target_data, backend, path: _parse_path_target(
            FormatTargetConfig, name, target_data, backend, path
        ),
        build_config=lambda default, targets: FormatConfig(
            default=default,
            targets=targets,
        ),
    )


def _parse_lint(data: dict[str, Any]) -> LintConfig:
    """Parse lint target configuration.

    Args:
        data: Raw ``lint`` section mapping.

    Returns:
        Parsed lint configuration.

    Raises:
        ConfigError: If the lint section is malformed.
    """

    return _parse_named_workflow_config(
        data,
        section="lint",
        entries_key="targets",
        registry=LINT_BACKENDS,
        build_target=lambda name, target_data, backend, path: _parse_path_target(
            LintTargetConfig, name, target_data, backend, path
        ),
        build_config=lambda default, targets: LintConfig(
            default=default,
            targets=targets,
        ),
    )


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

    supported_backends = registered_backends(DEPLOY_BACKENDS)
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
        require_backend_contract("deploy", target.backend, DEPLOY_BACKENDS).validate(
            target
        )
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

    if name == CPP_WORKFLOW_KIND:
        return {BUILD_CMAKE}
    if name == PYTHON_WORKFLOW_KIND:
        return {BUILD_PYTHON}
    raise ConfigError(f"`build.{name}` is not a supported build entry")
