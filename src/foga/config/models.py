"""Typed configuration models and selection helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, TypeVar

from ..adapters.kinds import format_backend_kind, lint_backend_kind, test_backend_kind
from ..errors import ConfigError
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


WorkflowEntryT = TypeVar("WorkflowEntryT", bound="NamedBackendConfig")


@dataclass(frozen=True)
class WorkflowSelectionConfig:
    """Shared selection behavior for workflow families with kind defaults.

    Attributes:
        default: Default workflow kind selected when the CLI does not provide
            an explicit choice.
    """

    default: str | None = None

    def available_kinds(self) -> list[str]:
        """Return the configured workflow kinds in stable execution order.

        Returns:
            Ordered workflow kinds configured for the concrete workflow family.
        """

        raise NotImplementedError

    def selected_kinds(self, selection: str | None = None) -> list[str]:
        """Resolve the active workflow kinds for an invocation.

        Args:
            selection: Optional explicit workflow kind selected by the CLI.

        Returns:
            Active workflow kinds for the current invocation.
        """

        selected = selection or self.default or ALL_WORKFLOW_SELECTION
        if selected == ALL_WORKFLOW_SELECTION:
            return self.available_kinds()
        return [selected]


@dataclass(frozen=True)
class NamedBackendConfig:
    """Shared command target fields used by named backend-backed workflows.

    Attributes:
        name: Configured target or runner name.
        backend: Backend identifier selected for the entry.
        launcher: Optional command prefix prepended before the backend command.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around workflow steps.
    """

    name: str
    backend: str
    launcher: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class PathTargetConfig(NamedBackendConfig):
    """Shared path-based target fields used by formatter and linter entries.

    Attributes:
        paths: Paths passed to the backend command.
    """

    paths: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CppBuildConfig:
    """Configuration for a CMake-backed C++ build workflow.

    Attributes:
        backend: C++ build backend identifier.
        source_dir: Source directory passed to CMake.
        build_dir: Build directory passed to CMake.
        generator: Optional generator name for CMake.
        launcher: Optional command prefix prepended before CMake commands.
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
    launcher: list[str] = field(default_factory=list)
    configure_args: list[str] = field(default_factory=list)
    build_args: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class MesonBuildConfig:
    """Configuration for a Meson-backed C++ build workflow.

    Attributes:
        backend: C++ build backend identifier.
        source_dir: Source directory passed to ``meson setup``.
        build_dir: Build directory passed to ``meson setup`` and reused for
            ``meson compile``.
        launcher: Optional command prefix prepended before Meson commands.
        setup_args: Extra arguments passed to ``meson setup``.
        compile_args: Extra arguments passed to ``meson compile``.
        targets: Default C++ targets to compile when none are requested.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around C++ build steps.
    """

    backend: str
    source_dir: str
    build_dir: str
    launcher: list[str] = field(default_factory=list)
    setup_args: list[str] = field(default_factory=list)
    compile_args: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class PythonBuildConfig:
    """Configuration for a Python package build workflow.

    Attributes:
        backend: Python build backend identifier.
        launcher: Optional command prefix prepended before the build command.
        args: Extra arguments passed to the build command.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around Python build steps.
    """

    backend: str
    launcher: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    hooks: HookConfig = field(default_factory=HookConfig)


@dataclass(frozen=True)
class BuildConfig(WorkflowSelectionConfig):
    """Aggregate build configuration for configured build workflows.

    Attributes:
        default: Default build kind selection used when the CLI does not
            request an explicit build mode.
        entries: Build workflow configuration keyed by section name under
            ``build``.
        cpp: Optional C++ build configuration.
        python: Optional Python build configuration.
    """

    entries: dict[str, CppBuildConfig | MesonBuildConfig | PythonBuildConfig] = field(
        default_factory=dict
    )
    cpp: CppBuildConfig | MesonBuildConfig | None = None
    python: PythonBuildConfig | None = None

    def configured_backends(
        self, selection: str | None = None
    ) -> list[CppBuildConfig | MesonBuildConfig | PythonBuildConfig]:
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

        backends: list[CppBuildConfig | MesonBuildConfig | PythonBuildConfig] = []
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


@dataclass(frozen=True)
class TestConfig(WorkflowSelectionConfig):
    """Aggregate test configuration for configured test workflows.

    Attributes:
        default: Default test kind selection used when the CLI does not request
            an explicit test mode.
        default_runners: Default runner names selected when the CLI omits
            ``--runner``.
        runners: Parsed test runners keyed by runner name.
    """

    __test__ = False

    default_runners: list[str] = field(default_factory=list)
    runners: dict[str, TestRunnerConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured test kinds in stable execution order.

        Returns:
            Ordered test kinds present in the configured runners.
        """

        return _available_kinds_for_entries(self.runners, test_backend_kind)

    def select_runners(
        self, selection: str | None = None
    ) -> dict[str, TestRunnerConfig]:
        """Return runners matching the active test kind selection.

        Args:
            selection: Optional explicit test kind from the CLI.

        Returns:
            Runner mapping filtered to the active test kinds.
        """

        return _select_entries_by_kind(
            self.runners,
            active_kinds=set(self.selected_kinds(selection)),
            kind_resolver=test_backend_kind,
        )

    def selected_runners(
        self,
        selection: str | None = None,
        runner_names: list[str] | None = None,
    ) -> dict[str, TestRunnerConfig]:
        """Resolve the effective test runners for one invocation.

        Args:
            selection: Optional explicit test kind selected by the CLI.
            runner_names: Optional explicit runner names selected by the CLI.

        Returns:
            Runner mapping after kind selection and named default resolution.
        """

        return _select_named_entries(
            self.select_runners(selection),
            selected_names=runner_names,
            default_names=self.default_runners,
            label="test runner",
        )


@dataclass(frozen=True)
class TestRunnerConfig(NamedBackendConfig):
    """Configuration for an individual test runner.

    Attributes:
        name: Runner name from the configuration file.
        backend: Test backend identifier.
        launcher: Optional command prefix prepended before test commands.
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

    __test__ = False

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
class FormatTargetConfig(PathTargetConfig):
    """Configuration for an individual format target.

    Attributes:
        name: Target name from the configuration file.
        backend: Format backend identifier.
        launcher: Optional command prefix prepended before formatter commands.
        paths: Paths passed to the formatter command.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around formatter steps.
    """


@dataclass(frozen=True)
class FormatConfig(WorkflowSelectionConfig):
    """Aggregate format configuration for configured format workflows.

    Attributes:
        default: Default format kind selection used when the CLI does not
            request an explicit format mode.
        default_targets: Default target names selected when the CLI omits
            ``--target``.
        targets: Parsed format targets keyed by target name.
    """

    default_targets: list[str] = field(default_factory=list)
    targets: dict[str, FormatTargetConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured format kinds in stable execution order.

        Returns:
            Ordered format kinds derived from configured target backends.
        """

        return _available_kinds_for_entries(self.targets, format_backend_kind)

    def select_targets(
        self, selection: str | None = None
    ) -> dict[str, FormatTargetConfig]:
        """Return format targets matching the active selection.

        Args:
            selection: Optional explicit format kind selection.

        Returns:
            Format targets matching the active format kind set.
        """

        return _select_entries_by_kind(
            self.targets,
            active_kinds=set(self.selected_kinds(selection)),
            kind_resolver=format_backend_kind,
        )

    def selected_targets(
        self,
        selection: str | None = None,
        target_names: list[str] | None = None,
    ) -> dict[str, FormatTargetConfig]:
        """Resolve the effective format targets for one invocation."""

        return _select_named_entries(
            self.select_targets(selection),
            selected_names=target_names,
            default_names=self.default_targets,
            label="format target",
        )


@dataclass(frozen=True)
class LintTargetConfig(PathTargetConfig):
    """Configuration for an individual lint target.

    Attributes:
        name: Target name from the configuration file.
        backend: Lint backend identifier.
        launcher: Optional command prefix prepended before lint commands.
        paths: Paths passed to the linter command.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around lint steps.
    """


@dataclass(frozen=True)
class LintConfig(WorkflowSelectionConfig):
    """Aggregate lint configuration for configured lint workflows.

    Attributes:
        default: Default lint kind selection used when the CLI does not
            request an explicit lint mode.
        default_targets: Default target names selected when the CLI omits
            ``--target``.
        targets: Parsed lint targets keyed by target name.
    """

    default_targets: list[str] = field(default_factory=list)
    targets: dict[str, LintTargetConfig] = field(default_factory=dict)

    def available_kinds(self) -> list[str]:
        """Return the configured lint kinds in stable execution order.

        Returns:
            Ordered lint kinds derived from configured target backends.
        """

        return _available_kinds_for_entries(self.targets, lint_backend_kind)

    def select_targets(
        self, selection: str | None = None
    ) -> dict[str, LintTargetConfig]:
        """Return lint targets matching the active selection.

        Args:
            selection: Optional explicit lint kind selection.

        Returns:
            Lint targets matching the active lint kind set.
        """

        return _select_entries_by_kind(
            self.targets,
            active_kinds=set(self.selected_kinds(selection)),
            kind_resolver=lint_backend_kind,
        )

    def selected_targets(
        self,
        selection: str | None = None,
        target_names: list[str] | None = None,
    ) -> dict[str, LintTargetConfig]:
        """Resolve the effective lint targets for one invocation."""

        return _select_named_entries(
            self.select_targets(selection),
            selected_names=target_names,
            default_names=self.default_targets,
            label="lint target",
        )


@dataclass(frozen=True)
class InstallTargetConfig(NamedBackendConfig):
    """Configuration for an individual install target.

    Attributes:
        name: Install target name from the configuration file.
        backend: Install backend identifier.
        launcher: Optional command prefix prepended before install commands.
        packages: Optional package names, specifiers, or package-manager targets.
        path: Optional local path installed by backends that support it.
        editable: Whether pip-style backends should install the path in editable mode.
        groups: Optional uv dependency groups synced from ``pyproject.toml``.
        extras: Optional uv extras synced from ``pyproject.toml``.
        install_project: Whether uv project sync should install the local project.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around install steps.
    """

    packages: list[str] = field(default_factory=list)
    path: str | None = None
    editable: bool = False
    groups: list[str] = field(default_factory=list)
    extras: list[str] = field(default_factory=list)
    install_project: bool | None = None


@dataclass(frozen=True)
class DeployTargetConfig(NamedBackendConfig):
    """Configuration for an individual deploy target.

    Attributes:
        name: Deploy target name from the configuration file.
        backend: Deploy backend identifier.
        launcher: Optional command prefix prepended before deploy commands.
        artifacts: Glob patterns used to resolve artifacts for upload.
        repository: Optional named repository understood by the backend.
        repository_url: Optional explicit repository URL.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around deploy steps.
    """

    artifacts: list[str] = field(default_factory=list)
    repository: str | None = None
    repository_url: str | None = None


@dataclass(frozen=True)
class DocsTargetConfig(NamedBackendConfig):
    """Configuration for an individual documentation target.

    Attributes:
        name: Docs target name from the configuration file.
        backend: Docs backend identifier.
        launcher: Optional command prefix prepended before docs commands.
        args: Extra backend-specific command arguments.
        env: Environment variables applied to generated commands.
        hooks: Commands executed around docs steps.
        source_dir: Source directory used by documentation generators.
        build_dir: Output directory used by documentation generators.
        builder: Optional output builder name for Sphinx.
        config_file: Optional backend-specific config file path.
    """

    source_dir: str | None = None
    build_dir: str | None = None
    builder: str | None = None
    config_file: str | None = None


@dataclass(frozen=True)
class DocsConfig:
    """Aggregate docs configuration for configured documentation workflows.

    Attributes:
        default_targets: Default docs target names selected when the CLI omits
            ``--target``.
        targets: Parsed docs targets keyed by target name.
    """

    default_targets: list[str] = field(default_factory=list)
    targets: dict[str, DocsTargetConfig] = field(default_factory=dict)

    def selected_targets(
        self, target_names: list[str] | None = None
    ) -> dict[str, DocsTargetConfig]:
        """Resolve the effective docs targets for one invocation."""

        return _select_named_entries(
            self.targets,
            selected_names=target_names,
            default_names=self.default_targets,
            label="docs target",
        )


@dataclass(frozen=True)
class InstallConfig:
    """Aggregate install configuration for configured installation workflows.

    Attributes:
        default_targets: Default install target names selected when the CLI omits
            ``--target``.
        targets: Parsed install targets keyed by target name.
    """

    default_targets: list[str] = field(default_factory=list)
    targets: dict[str, InstallTargetConfig] = field(default_factory=dict)

    def selected_targets(
        self, target_names: list[str] | None = None
    ) -> dict[str, InstallTargetConfig]:
        """Resolve the effective install targets for one invocation."""

        return _select_named_entries(
            self.targets,
            selected_names=target_names,
            default_names=self.default_targets,
            label="install target",
        )


@dataclass(frozen=True)
class DeployConfig:
    """Aggregate deploy configuration for configured deployment workflows.

    Attributes:
        default_targets: Default deploy target names selected when the CLI omits
            ``--target``.
        targets: Parsed deploy targets keyed by target name.
    """

    default_targets: list[str] = field(default_factory=list)
    targets: dict[str, DeployTargetConfig] = field(default_factory=dict)

    def selected_targets(
        self, target_names: list[str] | None = None
    ) -> dict[str, DeployTargetConfig]:
        """Resolve the effective deploy targets for one invocation."""

        return _select_named_entries(
            self.targets,
            selected_names=target_names,
            default_names=self.default_targets,
            label="deploy target",
        )


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
        docs: Parsed documentation target configuration.
        formatters: Parsed format target configuration and defaults.
        linters: Parsed lint target configuration and defaults.
        install: Parsed install configuration and defaults.
        deploy: Parsed deploy configuration and defaults.
        clean: Parsed clean configuration.
        raw: Raw merged configuration mapping after profile application.
    """

    project_root: Path
    project: ProjectConfig
    build: BuildConfig
    tests: TestConfig
    docs: DocsConfig
    formatters: FormatConfig
    linters: LintConfig
    install: InstallConfig
    deploy: DeployConfig
    clean: CleanConfig
    raw: dict[str, Any] = field(repr=False)


def build_kind(config: CppBuildConfig | MesonBuildConfig | PythonBuildConfig) -> str:
    """Return the logical kind for a parsed build backend config.

    Args:
        config: Parsed build backend configuration.

    Returns:
        Logical build kind associated with the backend config.
    """

    if isinstance(config, (CppBuildConfig, MesonBuildConfig)):
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


def _available_kinds_for_entries(
    entries: Mapping[str, WorkflowEntryT],
    kind_resolver: Callable[[str], str],
) -> list[str]:
    """Return unique workflow kinds for named backend-backed entries.

    Args:
        entries: Mapping of configured workflow entries.
        kind_resolver: Function that resolves a backend identifier to a kind.

    Returns:
        Ordered unique workflow kinds for the configured entries.
    """

    return _ordered_unique(kind_resolver(entry.backend) for entry in entries.values())


def _select_entries_by_kind(
    entries: Mapping[str, WorkflowEntryT],
    *,
    active_kinds: set[str],
    kind_resolver: Callable[[str], str],
) -> dict[str, WorkflowEntryT]:
    """Filter named entries down to the active workflow kind set.

    Args:
        entries: Mapping of configured workflow entries.
        active_kinds: Workflow kinds that should remain active.
        kind_resolver: Function that resolves a backend identifier to a kind.

    Returns:
        Entries whose backend kind belongs to the active kind set.
    """

    return {
        name: entry
        for name, entry in entries.items()
        if kind_resolver(entry.backend) in active_kinds
    }


def _select_named_entries(
    entries: Mapping[str, WorkflowEntryT],
    *,
    selected_names: list[str] | None,
    default_names: list[str] | None,
    label: str,
) -> dict[str, WorkflowEntryT]:
    """Resolve named entries, applying configured defaults when needed.

    Args:
        entries: Candidate entries available for the current invocation.
        selected_names: Optional explicit names selected by the CLI.
        default_names: Optional config-level default names.
        label: User-facing label used in validation errors.

    Returns:
        Selected entries in the requested order.

    Raises:
        ConfigError: If an explicit or default name does not exist.
    """

    effective_names = default_names if selected_names is None else selected_names
    if not effective_names:
        return dict(entries)

    selected: dict[str, WorkflowEntryT] = {}
    for name in effective_names:
        if name not in entries:
            raise ConfigError(f"Unknown {label}: {name}")
        selected[name] = entries[name]
    return selected
