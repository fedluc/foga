"""Typed configuration models and selection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..adapters.kinds import format_backend_kind, lint_backend_kind, test_backend_kind
from .constants import (
    ALL_WORKFLOW_SELECTION,
    CPP_WORKFLOW_KIND,
    PYTHON_WORKFLOW_KIND,
)


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
class CppBuildConfig:
    """Configuration for a C++ CMake build workflow.

    Attributes:
        backend: C++ build backend identifier.
        source_dir: Source directory passed to CMake.
        build_dir: Build directory passed to CMake.
        generator: Optional generator name for CMake.
        configure_args: Extra arguments passed to ``cmake -S``.
        build_args: Extra arguments passed to ``cmake --build``.
        targets: Default C++ targets to build when none are requested.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around C++ build steps.
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
        args: Extra arguments passed to the build command.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around Python build steps.
    """

    backend: str
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
        cpp: Optional C++ build configuration.
        python: Optional Python build configuration.
    """

    default: str | None = None
    entries: dict[str, CppBuildConfig | PythonBuildConfig] = field(default_factory=dict)
    cpp: CppBuildConfig | None = None
    python: PythonBuildConfig | None = None

    def configured_backends(
        self, selection: str | None = None
    ) -> list[CppBuildConfig | PythonBuildConfig]:
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

        backends: list[CppBuildConfig | PythonBuildConfig] = []
        if self.cpp is not None and CPP_WORKFLOW_KIND in active_kinds:
            backends.append(self.cpp)
        if self.python is not None and PYTHON_WORKFLOW_KIND in active_kinds:
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
        if self.cpp is not None:
            kinds.append(CPP_WORKFLOW_KIND)
        if self.python is not None:
            kinds.append(PYTHON_WORKFLOW_KIND)
        return kinds

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active build kinds for an invocation.

        Args:
            selection: Optional explicit build kind from the CLI.

        Returns:
            Ordered build kinds that should run for the invocation.
        """

        selected = selection or self.default or ALL_WORKFLOW_SELECTION
        if selected == ALL_WORKFLOW_SELECTION:
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

        return _ordered_unique(
            test_backend_kind(runner.backend) for runner in self.runners.values()
        )

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active test kinds for an invocation.

        Args:
            selection: Optional explicit test kind from the CLI.

        Returns:
            Ordered test kinds that should run for the invocation.
        """

        selected = selection or self.default or ALL_WORKFLOW_SELECTION
        if selected == ALL_WORKFLOW_SELECTION:
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
            if test_backend_kind(runner.backend) in active_kinds
        }


@dataclass(frozen=True)
class TestRunnerConfig:
    """Configuration for an individual test runner.

    Attributes:
        name: Runner name from the configuration file.
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
class FormatTargetConfig:
    """Configuration for an individual format target.

    Attributes:
        name: Target name from the configuration file.
        backend: Format backend identifier.
        paths: Paths passed to the formatter command.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around formatter steps.
    """

    name: str
    backend: str
    paths: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class FormatConfig:
    """Aggregate format configuration for configured format workflows.

    Attributes:
        default: Default format kind selection used when the CLI does not
            request an explicit format mode.
        targets: Parsed format targets keyed by target name.
    """

    default: str | None = None
    targets: dict[str, FormatTargetConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured format kinds in stable execution order.

        Returns:
            Ordered format kinds derived from configured target backends.
        """

        return _ordered_unique(
            format_backend_kind(target.backend) for target in self.targets.values()
        )

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active format kinds for an invocation.

        Args:
            selection: Optional explicit format kind selection.

        Returns:
            Active format kinds for the current invocation.
        """

        selected = selection or self.default or ALL_WORKFLOW_SELECTION
        if selected == ALL_WORKFLOW_SELECTION:
            return self.available_kinds()
        return [selected]

    def select_targets(
        self, selection: str | None = None
    ) -> dict[str, FormatTargetConfig]:
        """Return format targets matching the active selection.

        Args:
            selection: Optional explicit format kind selection.

        Returns:
            Format targets matching the active format kind set.
        """

        active_kinds = set(self.selected_kinds(selection))
        return {
            name: target
            for name, target in self.targets.items()
            if format_backend_kind(target.backend) in active_kinds
        }


@dataclass(frozen=True)
class LintTargetConfig:
    """Configuration for an individual lint target.

    Attributes:
        name: Target name from the configuration file.
        backend: Lint backend identifier.
        paths: Paths passed to the linter command.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around lint steps.
    """

    name: str
    backend: str
    paths: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class LintConfig:
    """Aggregate lint configuration for configured lint workflows.

    Attributes:
        default: Default lint kind selection used when the CLI does not
            request an explicit lint mode.
        targets: Parsed lint targets keyed by target name.
    """

    default: str | None = None
    targets: dict[str, LintTargetConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured lint kinds in stable execution order.

        Returns:
            Ordered lint kinds derived from configured target backends.
        """

        return _ordered_unique(
            lint_backend_kind(target.backend) for target in self.targets.values()
        )

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active lint kinds for an invocation.

        Args:
            selection: Optional explicit lint kind selection.

        Returns:
            Active lint kinds for the current invocation.
        """

        selected = selection or self.default or ALL_WORKFLOW_SELECTION
        if selected == ALL_WORKFLOW_SELECTION:
            return self.available_kinds()
        return [selected]

    def select_targets(
        self, selection: str | None = None
    ) -> dict[str, LintTargetConfig]:
        """Return lint targets matching the active selection.

        Args:
            selection: Optional explicit lint kind selection.

        Returns:
            Lint targets matching the active lint kind set.
        """

        active_kinds = set(self.selected_kinds(selection))
        return {
            name: target
            for name, target in self.targets.items()
            if lint_backend_kind(target.backend) in active_kinds
        }


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
        paths: Relative paths removed by ``foga clean``.
    """

    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectConfig:
    """Project metadata required by foga.

    Attributes:
        name: Project name displayed in user-facing output.
    """

    name: str


@dataclass(frozen=True)
class FogaConfig:
    """Fully parsed foga configuration.

    Attributes:
        project_root: Directory containing the resolved configuration file.
        project: Parsed project metadata.
        build: Parsed build configuration.
        tests: Parsed test runner configuration and defaults.
        formatters: Parsed format target configuration and defaults.
        linters: Parsed lint target configuration and defaults.
        deploy: Parsed deploy configuration keyed by target name.
        clean: Parsed clean configuration.
        raw: Raw merged configuration mapping after profile application.
    """

    project_root: Path
    project: ProjectConfig
    build: BuildConfig
    tests: TestConfig
    formatters: FormatConfig
    linters: LintConfig
    deploy: dict[str, DeployTargetConfig]
    clean: CleanConfig
    raw: dict[str, Any] = field(repr=False)


def build_kind(config: CppBuildConfig | PythonBuildConfig) -> str:
    """Return the logical kind for a parsed build backend config.

    Args:
        config: Parsed build backend configuration.

    Returns:
        Logical build kind associated with the backend config.
    """

    if isinstance(config, CppBuildConfig):
        return CPP_WORKFLOW_KIND
    return PYTHON_WORKFLOW_KIND


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
