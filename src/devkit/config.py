"""Configuration loading and validation for devkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .errors import ConfigError

SUPPORTED_BUILD_BACKENDS = {"cmake", "python-build"}
SUPPORTED_TEST_BACKENDS = {"pytest", "tox", "ctest"}
SUPPORTED_DEPLOY_BACKENDS = {"twine"}


@dataclass(frozen=True)
class HookConfig:
    """Pre- and post-command hooks for a workflow step."""

    pre: list[list[str]] = field(default_factory=list)
    post: list[list[str]] = field(default_factory=list)


@dataclass(frozen=True)
class NativeBuildConfig:
    """Configuration for a native CMake build workflow."""

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
    """Configuration for a Python package build workflow."""

    backend: str
    command: list[str] = field(default_factory=lambda: ["python3", "-m", "build"])
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class BuildConfig:
    """Aggregate build configuration for supported build backends."""

    native: NativeBuildConfig | None = None
    python: PythonBuildConfig | None = None


@dataclass(frozen=True)
class TestRunnerConfig:
    """Configuration for an individual test runner."""

    name: str
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
    """Configuration for an individual deploy target."""

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
    """Configuration for removable build artifact paths."""

    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectConfig:
    """Project metadata required by devkit."""

    name: str


@dataclass(frozen=True)
class DevkitConfig:
    """Fully parsed devkit configuration."""

    project_root: Path
    project: ProjectConfig
    build: BuildConfig
    tests: dict[str, TestRunnerConfig]
    deploy: dict[str, DeployTargetConfig]
    clean: CleanConfig
    raw: dict[str, Any] = field(repr=False)


def load_config(
    config_path: str | Path = "devkit.yml", profile: str | None = None
) -> DevkitConfig:
    """Load, merge, and validate a devkit configuration file."""
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
    """Merge an optional named profile into the base configuration."""
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
    return deep_merge(base, profile_data)


def parse_config(data: dict[str, Any], project_root: Path) -> DevkitConfig:
    """Parse validated raw configuration data into typed config objects."""
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
    """Parse build configuration for supported backends."""
    if not isinstance(data, dict):
        raise ConfigError("`build` must be a mapping")

    native_data = data.get("native")
    python_data = data.get("python")

    native = None
    if native_data is not None:
        if not isinstance(native_data, dict):
            raise ConfigError("`build.native` must be a mapping")
        backend = _required_str(native_data, "backend", "build.native.backend")
        if backend not in SUPPORTED_BUILD_BACKENDS:
            raise ConfigError(f"Unsupported build backend: {backend}")
        if backend != "cmake":
            raise ConfigError(
                "`build.native` currently supports only the `cmake` backend"
            )
        native = NativeBuildConfig(
            backend=backend,
            source_dir=_required_str(
                native_data, "source_dir", "build.native.source_dir"
            ),
            build_dir=_required_str(native_data, "build_dir", "build.native.build_dir"),
            generator=_optional_str(native_data, "generator"),
            configure_args=_string_list(
                native_data.get("configure_args"), "build.native.configure_args"
            ),
            build_args=_string_list(
                native_data.get("build_args"), "build.native.build_args"
            ),
            targets=_string_list(native_data.get("targets"), "build.native.targets"),
            env=_string_mapping(native_data.get("env"), "build.native.env"),
            hooks=_parse_hooks(native_data.get("hooks"), "build.native.hooks"),
        )

    python_build = None
    if python_data is not None:
        if not isinstance(python_data, dict):
            raise ConfigError("`build.python` must be a mapping")
        backend = _required_str(python_data, "backend", "build.python.backend")
        if backend not in SUPPORTED_BUILD_BACKENDS:
            raise ConfigError(f"Unsupported build backend: {backend}")
        if backend != "python-build":
            raise ConfigError(
                "`build.python` currently supports only the `python-build` backend"
            )
        command = python_data.get("command", ["python3", "-m", "build"])
        python_build = PythonBuildConfig(
            backend=backend,
            command=_command_list(command, "build.python.command"),
            args=_string_list(python_data.get("args"), "build.python.args"),
            env=_string_mapping(python_data.get("env"), "build.python.env"),
            hooks=_parse_hooks(python_data.get("hooks"), "build.python.hooks"),
        )

    return BuildConfig(native=native, python=python_build)


def _parse_tests(data: dict[str, Any]) -> dict[str, TestRunnerConfig]:
    """Parse test runner configuration."""
    if not isinstance(data, dict):
        raise ConfigError("`test` must be a mapping")
    runners_data = data.get("runners") or {}
    if not isinstance(runners_data, dict):
        raise ConfigError("`test.runners` must be a mapping")

    runners: dict[str, TestRunnerConfig] = {}
    for name, runner_data in runners_data.items():
        if not isinstance(runner_data, dict):
            raise ConfigError(f"`test.runners.{name}` must be a mapping")
        backend = _required_str(runner_data, "backend", f"test.runners.{name}.backend")
        if backend not in SUPPORTED_TEST_BACKENDS:
            raise ConfigError(f"Unsupported test backend: {backend}")
        runners[name] = TestRunnerConfig(
            name=name,
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
    return runners


def _parse_deploy(data: dict[str, Any]) -> dict[str, DeployTargetConfig]:
    """Parse deploy target configuration."""
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
        if backend not in SUPPORTED_DEPLOY_BACKENDS:
            raise ConfigError(f"Unsupported deploy backend: {backend}")
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
        if not targets[name].artifacts:
            raise ConfigError(f"`deploy.targets.{name}.artifacts` must not be empty")
    return targets


def _parse_clean(data: dict[str, Any]) -> CleanConfig:
    """Parse clean-path configuration."""
    if not isinstance(data, dict):
        raise ConfigError("`clean` must be a mapping")
    return CleanConfig(paths=_string_list(data.get("paths"), "clean.paths"))


def _validate_test_runner(config: TestRunnerConfig) -> None:
    """Validate backend-specific requirements for a test runner."""
    if config.backend == "pytest" and not config.path:
        raise ConfigError(f"`test.runners.{config.name}.path` is required for pytest")
    if config.backend == "tox" and not config.tox_env:
        raise ConfigError(f"`test.runners.{config.name}.tox_env` is required for tox")
    if config.backend == "ctest" and not config.build_dir:
        raise ConfigError(
            f"`test.runners.{config.name}.build_dir` is required for ctest"
        )


def _parse_hooks(data: Any, path: str) -> HookConfig:
    """Parse hook configuration from an optional mapping."""
    if data is None:
        return HookConfig()
    if not isinstance(data, dict):
        raise ConfigError(f"`{path}` must be a mapping")
    return HookConfig(
        pre=_command_matrix(data.get("pre"), f"{path}.pre"),
        post=_command_matrix(data.get("post"), f"{path}.post"),
    )


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge one mapping into another."""
    result = deep_copy_mapping(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deep_copy(value)
    return result


def deep_copy_mapping(value: dict[str, Any]) -> dict[str, Any]:
    """Create a deep copy of a mapping."""
    return {key: deep_copy(item) for key, item in value.items()}


def deep_copy(value: Any) -> Any:
    """Create a deep copy of nested mappings and lists."""
    if isinstance(value, dict):
        return deep_copy_mapping(value)
    if isinstance(value, list):
        return [deep_copy(item) for item in value]
    return value


def _required_str(data: dict[str, Any], key: str, path: str) -> str:
    """Read a required non-empty string field."""
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"`{path}` is required")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    """Read an optional string field."""
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"`{key}` must be a string")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    """Validate a list of strings and return a shallow copy."""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"`{path}` must be a list of strings")
    return list(value)


def _string_mapping(value: Any, path: str) -> dict[str, str]:
    """Validate a mapping of string keys and values."""
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
    """Validate a non-empty command array."""
    command = _string_list(value, path)
    if not command:
        raise ConfigError(f"`{path}` must not be empty")
    return command


def _command_matrix(value: Any, path: str) -> list[list[str]]:
    """Validate a list of non-empty command arrays."""
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
