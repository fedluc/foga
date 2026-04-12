"""Configuration loading and validation for devkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError

WORKFLOW_KINDS = ("native", "python")
WORKFLOW_SELECTIONS = (*WORKFLOW_KINDS, "all")


@dataclass(frozen=True)
class HookConfig:
    """Pre- and post-command hooks for a workflow step.

    Attributes:
        pre: Commands executed before the main workflow command.
        post: Commands executed after the main workflow command.
    """

    pre: list[list[str]] = field(default_factory=list)
    post: list[list[str]] = field(default_factory=list)


@dataclass(frozen=True)
class NativeBuildConfig:
    """Configuration for a native CMake build workflow.

    Attributes:
        backend: Native build backend identifier.
        source_dir: Source directory passed to CMake.
        build_dir: Build directory passed to CMake.
        generator: Optional generator name for CMake.
        configure_args: Extra arguments passed to ``cmake -S``.
        build_args: Extra arguments passed to ``cmake --build``.
        targets: Default native targets to build when none are requested.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around native build steps.
    """

    backend: str
    source_dir: str
    build_dir: str
    generator: str | None = None
    configure_args: list[str] = field(default_factory=list)
    build_args: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class PythonBuildConfig:
    """Configuration for a Python package build workflow.

    Attributes:
        backend: Python build backend identifier.
        command: Base command used to build the package.
        args: Extra arguments passed to the build command.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around Python build steps.
    """

    backend: str
    command: list[str] = field(default_factory=lambda: ["python3", "-m", "build"])
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class BuildConfig:
    """Aggregate build configuration for configured build workflows.

    Attributes:
        default: Default build kind selection used when the CLI does not
            request an explicit build mode.
        entries: Build workflow configuration keyed by section name under
            ``build``.
        native: Optional native build configuration.
        python: Optional Python build configuration.
    """

    default: str | None = None
    entries: dict[str, NativeBuildConfig | PythonBuildConfig] = field(
        default_factory=dict
    )
    native: NativeBuildConfig | None = None
    python: PythonBuildConfig | None = None

    def configured_backends(
        self, selection: str | None = None
    ) -> list[NativeBuildConfig | PythonBuildConfig]:
        """Return configured build backends in execution order.

        Args:
            selection: Optional explicit build kind for the current invocation.

        Returns:
            Configured build backends filtered to the selected kind.
        """

        active_kinds = set(self.selected_kinds(selection))

        if self.entries:
            return [
                config
                for config in self.entries.values()
                if build_kind(config) in active_kinds
            ]

        backends: list[NativeBuildConfig | PythonBuildConfig] = []
        if self.native is not None and "native" in active_kinds:
            backends.append(self.native)
        if self.python is not None and "python" in active_kinds:
            backends.append(self.python)
        return backends

    def available_kinds(self) -> list[str]:
        """Return the configured build kinds in stable execution order.

        Returns:
            Ordered build kinds present in the current configuration.
        """

        if self.entries:
            return _ordered_unique(
                build_kind(config) for config in self.entries.values()
            )

        kinds: list[str] = []
        if self.native is not None:
            kinds.append("native")
        if self.python is not None:
            kinds.append("python")
        return kinds

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active build kinds for an invocation.

        Args:
            selection: Optional explicit build kind from the CLI.

        Returns:
            Ordered build kinds that should run for the invocation.
        """

        selected = selection or self.default or "all"
        if selected == "all":
            return self.available_kinds()
        return [selected]


@dataclass(frozen=True)
class TestConfig:
    """Aggregate test configuration for configured test workflows.

    Attributes:
        default: Default test kind selection used when the CLI does not request
            an explicit test mode.
        runners: Parsed test runners keyed by runner name.
    """

    default: str | None = None
    runners: dict[str, TestRunnerConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured test kinds in stable execution order.

        Returns:
            Ordered test kinds present in the configured runners.
        """

        return _ordered_unique(runner.kind for runner in self.runners.values())

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active test kinds for an invocation.

        Args:
            selection: Optional explicit test kind from the CLI.

        Returns:
            Ordered test kinds that should run for the invocation.
        """

        selected = selection or self.default or "all"
        if selected == "all":
            return self.available_kinds()
        return [selected]

    def select_runners(
        self, selection: str | None = None
    ) -> dict[str, TestRunnerConfig]:
        """Return runners matching the active test kind selection.

        Args:
            selection: Optional explicit test kind from the CLI.

        Returns:
            Runner mapping filtered to the active test kinds.
        """

        active_kinds = set(self.selected_kinds(selection))
        return {
            name: runner
            for name, runner in self.runners.items()
            if runner.kind in active_kinds
        }


@dataclass(frozen=True)
class TestRunnerConfig:
    """Configuration for an individual test runner.

    Attributes:
        name: Runner name from the configuration file.
        kind: Logical test kind used for CLI selection.
        backend: Test backend identifier.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around test steps.
        path: Pytest path to execute.
        marker: Optional pytest marker expression.
        tox_env: Optional tox environment name.
        build_dir: Build directory used by ctest.
        source_dir: Source directory used when ctest needs a configure step.
        generator: Optional CMake generator for ctest preparation.
        configure_args: Extra CMake configure arguments for ctest.
        build_args: Extra CMake build arguments for ctest.
        target: Optional build target for ctest preparation.
    """

    name: str
    kind: str
    backend: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)
    path: str | None = None
    marker: str | None = None
    tox_env: str | None = None
    build_dir: str | None = None
    source_dir: str | None = None
    generator: str | None = None
    configure_args: list[str] = field(default_factory=list)
    build_args: list[str] = field(default_factory=list)
    target: str | None = None


@dataclass(frozen=True)
class DeployTargetConfig:
    """Configuration for an individual deploy target.

    Attributes:
        name: Deploy target name from the configuration file.
        backend: Deploy backend identifier.
        artifacts: Glob patterns used to resolve artifacts for upload.
        repository: Optional named repository understood by the backend.
        repository_url: Optional explicit repository URL.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around deploy steps.
    """

    name: str
    backend: str
    artifacts: list[str]
    repository: str | None = None
    repository_url: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class CleanConfig:
    """Configuration for removable build artifact paths.

    Attributes:
        paths: Relative paths removed by ``devkit clean``.
    """

    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectConfig:
    """Project metadata required by devkit.

    Attributes:
        name: Project name displayed in user-facing output.
    """

    name: str


@dataclass(frozen=True)
class DevkitConfig:
    """Fully parsed devkit configuration.

    Attributes:
        project_root: Directory containing the resolved configuration file.
        project: Parsed project metadata.
        build: Parsed build configuration.
        tests: Parsed test runner configuration and defaults.
        deploy: Parsed deploy configuration keyed by target name.
        clean: Parsed clean configuration.
        raw: Raw merged configuration mapping after profile application.
    """

    project_root: Path
    project: ProjectConfig
    build: BuildConfig
    tests: TestConfig
    deploy: dict[str, DeployTargetConfig]
    clean: CleanConfig
    raw: dict[str, Any] = field(repr=False)


def load_config(
    config_path: str | Path = "devkit.yml", profile: str | None = None
) -> DevkitConfig:
    """Load, merge, and validate a devkit configuration file.

    Args:
        config_path: Path to the ``devkit.yml`` file.
        profile: Optional profile to merge into the base configuration.

    Returns:
        Parsed configuration object.

    Raises:
        ConfigError: If the configuration file is missing or malformed.
    """
    path = Path(config_path).resolve()
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a mapping")

    merged = apply_profile(data, profile)
    return parse_config(merged, path.parent)


def apply_profile(data: dict[str, Any], profile: str | None) -> dict[str, Any]:
    """Merge an optional named profile into the base configuration.

    Args:
        data: Raw configuration mapping.
        profile: Optional profile name to apply.

    Returns:
        Configuration mapping after profile application.

    Raises:
        ConfigError: If the profile configuration is malformed or missing.
    """
    base = deep_copy_mapping(data)
    profiles = base.pop("profiles", {})
    if profiles and not isinstance(profiles, dict):
        raise ConfigError("`profiles` must be a mapping")

    active_profile = profile
    if active_profile is None and isinstance(profiles, dict) and "default" in profiles:
        active_profile = "default"

    if active_profile is None:
        return base
    if active_profile not in profiles:
        raise ConfigError(f"Unknown profile: {active_profile}")
    profile_data = profiles[active_profile]
    if not isinstance(profile_data, dict):
        raise ConfigError(f"Profile `{active_profile}` must be a mapping")
    _validate_profile_override(base, profile_data, f"profiles.{active_profile}")
    return deep_merge(base, profile_data)


def parse_config(data: dict[str, Any], project_root: Path) -> DevkitConfig:
    """Parse raw configuration data into typed config objects.

    Args:
        data: Raw merged configuration mapping.
        project_root: Directory containing the configuration file.

    Returns:
        Parsed configuration object.

    Raises:
        ConfigError: If required configuration values are missing or invalid.
    """
    project = data.get("project") or {}
    if not isinstance(project, dict) or not project.get("name"):
        raise ConfigError("`project.name` is required")

    build = _parse_build(data.get("build") or {})
    tests = _parse_tests(data.get("test") or {})
    deploy = _parse_deploy(data.get("deploy") or {})
    clean = _parse_clean(data.get("clean") or {})

    return DevkitConfig(
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
        ConfigError: If the build configuration is malformed or unsupported.
    """
    if not isinstance(data, dict):
        raise ConfigError("`build` must be a mapping")

    entries: dict[str, NativeBuildConfig | PythonBuildConfig] = {}
    native = None
    python_build = None
    default = _parse_workflow_selection(data.get("default"), "build.default")

    for name, build_data in data.items():
        if name == "default":
            continue
        if not isinstance(build_data, dict):
            raise ConfigError(f"`build.{name}` must be a mapping")
        backend = _required_str(build_data, "backend", f"build.{name}.backend")
        if backend not in _supported_build_backends():
            raise ConfigError(
                _unsupported_backend_message(
                    "build", backend, _supported_build_backends()
                )
            )

        config = _parse_build_backend(name, build_data, backend)
        _validate_build_backend(config)
        if name == "native" and not isinstance(config, NativeBuildConfig):
            raise ConfigError(
                "The `build.native` section requires a native build backend"
            )
        if name == "python" and not isinstance(config, PythonBuildConfig):
            raise ConfigError(
                "The `build.python` section requires a Python build backend"
            )
        entries[name] = config
        if name == "native" and isinstance(config, NativeBuildConfig):
            native = config
        if name == "python" and isinstance(config, PythonBuildConfig):
            python_build = config

    build_config = BuildConfig(
        default=default, entries=entries, native=native, python=python_build
    )
    _validate_selected_kinds(
        build_config.available_kinds(), build_config.default, "build.default", "build"
    )
    return build_config


def _parse_build_backend(
    name: str, data: dict[str, Any], backend: str
) -> NativeBuildConfig | PythonBuildConfig:
    """Parse a configured build backend by backend type.

    Args:
        name: Build entry name under ``build``.
        data: Raw build entry mapping.
        backend: Registered backend identifier for the entry.

    Returns:
        Parsed native or Python build configuration.

    Raises:
        ConfigError: If the backend identifier is unsupported.
    """

    path = f"build.{name}"
    if backend == "cmake":
        return NativeBuildConfig(
            backend=backend,
            source_dir=_required_str(data, "source_dir", f"{path}.source_dir"),
            build_dir=_required_str(data, "build_dir", f"{path}.build_dir"),
            generator=_optional_str(data, "generator"),
            configure_args=_string_list(
                data.get("configure_args"), f"{path}.configure_args"
            ),
            build_args=_string_list(data.get("build_args"), f"{path}.build_args"),
            targets=_string_list(data.get("targets"), f"{path}.targets"),
            env=_string_mapping(data.get("env"), f"{path}.env"),
            hooks=_parse_hooks(data.get("hooks"), f"{path}.hooks"),
        )
    if backend == "python-build":
        command = data.get("command", ["python3", "-m", "build"])
        return PythonBuildConfig(
            backend=backend,
            command=_command_list(command, f"{path}.command"),
            args=_string_list(data.get("args"), f"{path}.args"),
            env=_string_mapping(data.get("env"), f"{path}.env"),
            hooks=_parse_hooks(data.get("hooks"), f"{path}.hooks"),
        )
    raise ConfigError(f"Unsupported build backend: {backend}")


def _parse_tests(data: dict[str, Any]) -> TestConfig:
    """Parse test runner configuration.

    Args:
        data: Raw test configuration mapping.

    Returns:
        Parsed test runners keyed by runner name.

    Raises:
        ConfigError: If the test configuration is malformed or unsupported.
    """
    if not isinstance(data, dict):
        raise ConfigError("`test` must be a mapping")
    runners_data = data.get("runners") or {}
    if not isinstance(runners_data, dict):
        raise ConfigError("`test.runners` must be a mapping")
    default = _parse_workflow_selection(data.get("default"), "test.default")

    runners: dict[str, TestRunnerConfig] = {}
    for name, runner_data in runners_data.items():
        if not isinstance(runner_data, dict):
            raise ConfigError(f"`test.runners.{name}` must be a mapping")
        backend = _required_str(runner_data, "backend", f"test.runners.{name}.backend")
        if backend not in _supported_test_backends():
            raise ConfigError(
                _unsupported_backend_message(
                    "test", backend, _supported_test_backends()
                )
            )
        runners[name] = TestRunnerConfig(
            name=name,
            kind=_parse_test_kind(runner_data, name, backend),
            backend=backend,
            args=_string_list(runner_data.get("args"), f"test.runners.{name}.args"),
            env=_string_mapping(runner_data.get("env"), f"test.runners.{name}.env"),
            hooks=_parse_hooks(runner_data.get("hooks"), f"test.runners.{name}.hooks"),
            path=_optional_str(runner_data, "path"),
            marker=_optional_str(runner_data, "marker"),
            tox_env=_optional_str(runner_data, "tox_env"),
            build_dir=_optional_str(runner_data, "build_dir"),
            source_dir=_optional_str(runner_data, "source_dir"),
            generator=_optional_str(runner_data, "generator"),
            configure_args=_string_list(
                runner_data.get("configure_args"), f"test.runners.{name}.configure_args"
            ),
            build_args=_string_list(
                runner_data.get("build_args"), f"test.runners.{name}.build_args"
            ),
            target=_optional_str(runner_data, "target"),
        )
        _validate_test_runner(runners[name])
    test_config = TestConfig(default=default, runners=runners)
    _validate_selected_kinds(
        test_config.available_kinds(), test_config.default, "test.default", "test"
    )
    return test_config


def _parse_deploy(data: dict[str, Any]) -> dict[str, DeployTargetConfig]:
    """Parse deploy target configuration.

    Args:
        data: Raw deploy configuration mapping.

    Returns:
        Parsed deploy targets keyed by target name.

    Raises:
        ConfigError: If the deploy configuration is malformed or unsupported.
    """
    if not isinstance(data, dict):
        raise ConfigError("`deploy` must be a mapping")
    targets_data = data.get("targets") or {}
    if not isinstance(targets_data, dict):
        raise ConfigError("`deploy.targets` must be a mapping")

    targets: dict[str, DeployTargetConfig] = {}
    for name, target_data in targets_data.items():
        if not isinstance(target_data, dict):
            raise ConfigError(f"`deploy.targets.{name}` must be a mapping")
        backend = _required_str(
            target_data, "backend", f"deploy.targets.{name}.backend"
        )
        if backend not in _supported_deploy_backends():
            raise ConfigError(
                _unsupported_backend_message(
                    "deploy", backend, _supported_deploy_backends()
                )
            )
        targets[name] = DeployTargetConfig(
            name=name,
            backend=backend,
            artifacts=_string_list(
                target_data.get("artifacts"), f"deploy.targets.{name}.artifacts"
            ),
            repository=_optional_str(target_data, "repository"),
            repository_url=_optional_str(target_data, "repository_url"),
            args=_string_list(target_data.get("args"), f"deploy.targets.{name}.args"),
            env=_string_mapping(target_data.get("env"), f"deploy.targets.{name}.env"),
            hooks=_parse_hooks(
                target_data.get("hooks"), f"deploy.targets.{name}.hooks"
            ),
        )
        _validate_deploy_backend(targets[name])
    return targets


def _parse_clean(data: dict[str, Any]) -> CleanConfig:
    """Parse clean-path configuration.

    Args:
        data: Raw clean configuration mapping.

    Returns:
        Parsed clean configuration.

    Raises:
        ConfigError: If the clean configuration is malformed.
    """
    if not isinstance(data, dict):
        raise ConfigError("`clean` must be a mapping")
    return CleanConfig(paths=_string_list(data.get("paths"), "clean.paths"))


def _validate_test_runner(config: TestRunnerConfig) -> None:
    """Validate backend-specific requirements for a test runner.

    Args:
        config: Test runner configuration to validate.

    Raises:
        ConfigError: If required fields for the selected backend are missing.
    """
    from .adapters.testing import validate_test_backend

    validate_test_backend(config)


def _validate_build_backend(config: NativeBuildConfig | PythonBuildConfig) -> None:
    """Validate backend-specific build configuration.

    Args:
        config: Build configuration to validate.

    Raises:
        ConfigError: If required fields for the selected backend are missing.
    """

    from .adapters.build import validate_build_backend

    validate_build_backend(config)


def _validate_deploy_backend(config: DeployTargetConfig) -> None:
    """Validate backend-specific deploy configuration."""

    from .adapters.deploy import validate_deploy_backend

    validate_deploy_backend(config)


def _supported_build_backends() -> set[str]:
    """Return the registered build backend names.

    Returns:
        Registered build backend identifiers.
    """

    from .adapters.build import supported_build_backends

    return supported_build_backends()


def _unsupported_backend_message(
    workflow: str, backend: str, supported_backends: set[str]
) -> str:
    """Build a stable error for unsupported backend names.

    Args:
        workflow: Workflow family containing the invalid backend.
        backend: Unsupported backend name from the configuration.
        supported_backends: Registered backend names for the workflow.

    Returns:
        User-facing validation error with the supported backend list.
    """
    supported = ", ".join(sorted(supported_backends))
    return f"Unsupported {workflow} backend: {backend}. Supported backends: {supported}"


def _supported_test_backends() -> set[str]:
    """Return the registered test backend names.

    Returns:
        Registered test backend identifiers.
    """

    from .adapters.testing import supported_test_backends

    return supported_test_backends()


def _supported_deploy_backends() -> set[str]:
    """Return the registered deploy backend names.

    Returns:
        Registered deploy backend identifiers.
    """

    from .adapters.deploy import supported_deploy_backends

    return supported_deploy_backends()


def _parse_hooks(data: Any, path: str) -> HookConfig:
    """Parse hook configuration from an optional mapping.

    Args:
        data: Raw hook configuration value.
        path: Configuration path used in validation errors.

    Returns:
        Parsed hook configuration.

    Raises:
        ConfigError: If the hook configuration is malformed.
    """
    if data is None:
        return HookConfig()
    if not isinstance(data, dict):
        raise ConfigError(f"`{path}` must be a mapping")
    return HookConfig(
        pre=_command_matrix(data.get("pre"), f"{path}.pre"),
        post=_command_matrix(data.get("post"), f"{path}.post"),
    )


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge one mapping into another.

    Args:
        base: Base mapping to copy.
        override: Mapping whose values override the base mapping.

    Returns:
        Deeply merged mapping.
    """
    result = deep_copy_mapping(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deep_copy(value)
    return result


def _validate_profile_override(
    base: dict[str, Any], override: dict[str, Any], path: str
) -> None:
    """Validate that a profile override is compatible with the base config.

    Args:
        base: Base configuration mapping before profile application.
        override: Profile override mapping at the current path.
        path: Configuration path for field-level diagnostics.

    Raises:
        ConfigError: If the override changes container shape or swaps an
            existing backend identifier.
    """
    for key, value in override.items():
        current_path = f"{path}.{key}"
        if key not in base:
            continue

        base_value = base[key]
        if isinstance(base_value, dict):
            _validate_mapping_override(base_value, value, current_path)
            continue

        if isinstance(base_value, list):
            _validate_list_override(value, current_path)
            continue

        _validate_scalar_override(key, base_value, value, current_path)


def _validate_mapping_override(
    base_value: dict[str, Any], value: Any, path: str
) -> None:
    """Validate an override for an existing mapping-valued config field.

    Args:
        base_value: Existing mapping from the base configuration.
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a mapping with a non-mapping.
    """
    if not isinstance(value, dict):
        raise ConfigError(f"`{path}` must remain a mapping in profile overrides")
    _validate_profile_override(base_value, value, path)


def _validate_list_override(value: Any, path: str) -> None:
    """Validate an override for an existing list-valued config field.

    Args:
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a list with a different shape.
    """
    if isinstance(value, dict):
        raise ConfigError(f"`{path}` cannot replace a scalar or list with a mapping")
    if not isinstance(value, list):
        raise ConfigError(f"`{path}` must remain a list in profile overrides")


def _validate_scalar_override(key: str, base_value: Any, value: Any, path: str) -> None:
    """Validate an override for an existing scalar-valued config field.

    Args:
        key: Field name from the configuration mapping.
        base_value: Existing scalar from the base configuration.
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a scalar with a mapping or swaps
            an existing backend identifier.
    """
    if isinstance(value, dict):
        raise ConfigError(f"`{path}` cannot replace a scalar or list with a mapping")
    if key == "backend" and base_value != value:
        raise ConfigError(
            f"`{path}` cannot change backend from `{base_value}` to `{value}` "
            "in profile overrides"
        )


def deep_copy_mapping(value: dict[str, Any]) -> dict[str, Any]:
    """Create a deep copy of a mapping.

    Args:
        value: Mapping to copy.

    Returns:
        Deep copy of ``value``.
    """
    return {key: deep_copy(item) for key, item in value.items()}


def deep_copy(value: Any) -> Any:
    """Create a deep copy of nested mappings and lists.

    Args:
        value: Value to copy.

    Returns:
        Deep copy of ``value``.
    """
    if isinstance(value, dict):
        return deep_copy_mapping(value)
    if isinstance(value, list):
        return [deep_copy(item) for item in value]
    return value


def _required_str(data: dict[str, Any], key: str, path: str) -> str:
    """Read a required non-empty string field.

    Args:
        data: Source mapping.
        key: Mapping key to read.
        path: Full configuration path used in validation errors.

    Returns:
        Non-empty string value.

    Raises:
        ConfigError: If the value is missing, empty, or not a string.
    """
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"`{path}` is required")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    """Read an optional string field.

    Args:
        data: Source mapping.
        key: Mapping key to read.

    Returns:
        String value when present, otherwise ``None``.

    Raises:
        ConfigError: If the value is present but not a string.
    """
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"`{key}` must be a string")
    return value


def _parse_workflow_selection(value: Any, path: str) -> str | None:
    """Parse a workflow kind selector.

    Args:
        value: Raw selector value from configuration.
        path: Configuration path used in validation errors.

    Returns:
        Parsed workflow kind or ``None`` when the field is unset.

    Raises:
        ConfigError: If the selector is not one of the supported values.
    """

    if value is None:
        return None
    if not isinstance(value, str) or value not in WORKFLOW_SELECTIONS:
        expected = ", ".join(WORKFLOW_SELECTIONS)
        raise ConfigError(f"`{path}` must be one of: {expected}")
    return value


def _parse_test_kind(data: dict[str, Any], name: str, backend: str) -> str:
    """Parse or infer the logical kind for a configured test runner.

    Args:
        data: Raw runner configuration mapping.
        name: Runner name from ``test.runners``.
        backend: Registered backend identifier for the runner.

    Returns:
        Logical runner kind used for CLI selection.

    Raises:
        ConfigError: If the configured kind uses an unsupported value.
    """

    path = f"test.runners.{name}.kind"
    kind = _parse_workflow_selection(data.get("kind"), path)
    if kind == "all":
        raise ConfigError(f"`{path}` must be one of: native, python")
    if kind is not None:
        return kind
    return _default_test_kind(backend)


def _default_test_kind(backend: str) -> str:
    """Infer a default test kind from the configured backend.

    Args:
        backend: Registered test backend identifier.

    Returns:
        Default logical kind implied by the backend.
    """

    if backend == "ctest":
        return "native"
    return "python"


def _validate_selected_kinds(
    available_kinds: list[str], selected: str | None, path: str, workflow: str
) -> None:
    """Validate that a configured default selection matches configured kinds.

    Args:
        available_kinds: Workflow kinds present in the active configuration.
        selected: Configured default workflow kind.
        path: Configuration path used in validation errors.
        workflow: Human-readable workflow name for diagnostics.

    Raises:
        ConfigError: If the configured default references missing workflow kinds.
    """

    if selected is None:
        return
    if selected == "all":
        if not available_kinds:
            return
        missing = [kind for kind in WORKFLOW_KINDS if kind not in available_kinds]
        if missing:
            missing_str = ", ".join(missing)
            raise ConfigError(
                f"`{path}` cannot be `all` when {workflow} only configures: "
                f"{', '.join(available_kinds)}. Missing: {missing_str}"
            )
        return
    if selected not in available_kinds:
        raise ConfigError(
            f"`{path}` selects `{selected}` but no {selected} {workflow} workflows "
            "are configured"
        )


def build_kind(config: NativeBuildConfig | PythonBuildConfig) -> str:
    """Return the logical kind for a parsed build backend config.

    Args:
        config: Parsed build backend configuration.

    Returns:
        Logical build kind associated with the backend config.
    """

    if isinstance(config, NativeBuildConfig):
        return "native"
    return "python"


def _ordered_unique(values: Any) -> list[str]:
    """Return values in input order without duplicates.

    Args:
        values: Iterable of values that may contain duplicates.

    Returns:
        Ordered unique string values.
    """

    ordered: list[str] = []
    for value in values:
        if value not in ordered:
            ordered.append(value)
    return ordered


def _string_list(value: Any, path: str) -> list[str]:
    """Validate a list of strings and return a shallow copy.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        List of strings, or an empty list when ``value`` is ``None``.

    Raises:
        ConfigError: If the value is not a list of strings.
    """
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"`{path}` must be a list of strings")
    return list(value)


def _string_mapping(value: Any, path: str) -> dict[str, str]:
    """Validate a mapping of string keys and values.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        Mapping of strings, or an empty mapping when ``value`` is ``None``.

    Raises:
        ConfigError: If the value is not a mapping of strings.
    """
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"`{path}` must be a mapping")
    mapping: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ConfigError(f"`{path}` must map strings to strings")
        mapping[key] = item
    return mapping


def _command_list(value: Any, path: str) -> list[str]:
    """Validate a non-empty command array.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        Validated command list.

    Raises:
        ConfigError: If the command is empty or malformed.
    """
    command = _string_list(value, path)
    if not command:
        raise ConfigError(f"`{path}` must not be empty")
    return command


def _command_matrix(value: Any, path: str) -> list[list[str]]:
    """Validate a list of non-empty command arrays.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        Validated command matrix.

    Raises:
        ConfigError: If the value is not a list of non-empty command arrays.
    """
    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError(f"`{path}` must be a list of command arrays")
    commands: list[list[str]] = []
    for index, item in enumerate(value):
        if (
            not isinstance(item, list)
            or not all(isinstance(part, str) for part in item)
            or not item
        ):
            raise ConfigError(f"`{path}[{index}]` must be a non-empty list of strings")
        commands.append(list(item))
    return commands
