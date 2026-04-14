"""Docs backend contracts and command planning."""

from __future__ import annotations

from pathlib import Path

from ..config.models import DocsTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, DocsRequest, WorkflowPlan


def plan_docs(project_root: Path, targets: list[DocsTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured docs targets.

    Args:
        project_root: Project root used as the default working directory.
        targets: Docs targets selected for the current invocation.

    Returns:
        Prepared command specs for each selected docs target.
    """

    specs: list[CommandSpec] = []
    request = DocsRequest(project_root=project_root)
    for target in targets:
        contract = _docs_contract(target.backend)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def supported_docs_backends() -> set[str]:
    """Return the registered docs backend names.

    Returns:
        Set of registered docs backend names.
    """

    return set(DOCS_BACKENDS)


def validate_docs_backend(config: DocsTargetConfig) -> None:
    """Validate a configured docs backend through the registry contract.

    Args:
        config: Parsed docs target configuration.
    """

    _docs_contract(config.backend).validate(config)


def _docs_contract(backend: str) -> BackendContract[DocsTargetConfig, DocsRequest]:
    """Resolve a registered docs backend contract.

    Args:
        backend: Configured docs backend name.

    Returns:
        Registered backend contract for the requested backend.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return DOCS_BACKENDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(DOCS_BACKENDS))
        raise ConfigError(
            f"Unsupported docs backend: {backend}",
            hint=f"Choose one of the supported docs backends: {supported}.",
        ) from exc


def _sphinx_plan(config: DocsTargetConfig, request: DocsRequest) -> list[CommandSpec]:
    """Build the sphinx-build command for a docs target.

    Args:
        config: Parsed docs target configuration.
        request: Docs planning options.

    Returns:
        Command specs for the configured Sphinx docs target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    command = [
        "sphinx-build",
        "-b",
        config.builder or "html",
        config.source_dir or "",
        config.build_dir or "",
    ]
    command.extend(config.args)
    specs = pre_hooks + [
        CommandSpec(
            command=command,
            cwd=request.project_root,
            env=config.env,
            description=f"docs target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _mkdocs_plan(config: DocsTargetConfig, request: DocsRequest) -> list[CommandSpec]:
    """Build the mkdocs command for a docs target.

    Args:
        config: Parsed docs target configuration.
        request: Docs planning options.

    Returns:
        Command specs for the configured MkDocs target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    command = ["mkdocs", "build"]
    if config.config_file:
        command.extend(["--config-file", config.config_file])
    if config.build_dir:
        command.extend(["--site-dir", config.build_dir])
    command.extend(config.args)
    specs = pre_hooks + [
        CommandSpec(
            command=command,
            cwd=request.project_root,
            env=config.env,
            description=f"docs target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _doxygen_plan(config: DocsTargetConfig, request: DocsRequest) -> list[CommandSpec]:
    """Build the doxygen command for a docs target.

    Args:
        config: Parsed docs target configuration.
        request: Docs planning options.

    Returns:
        Command specs for the configured Doxygen target.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    command = ["doxygen", config.config_file or ""]
    command.extend(config.args)
    specs = pre_hooks + [
        CommandSpec(
            command=command,
            cwd=request.project_root,
            env=config.env,
            description=f"docs target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _validate_sphinx(config: DocsTargetConfig) -> None:
    """Validate sphinx target configuration.

    Args:
        config: Parsed docs target configuration.

    Raises:
        ConfigError: If required Sphinx fields are missing.
    """

    if not config.source_dir:
        raise ConfigError(f"`docs.targets.{config.name}.source_dir` is required")
    if not config.build_dir:
        raise ConfigError(f"`docs.targets.{config.name}.build_dir` is required")


def _validate_mkdocs(config: DocsTargetConfig) -> None:
    """Validate mkdocs target configuration.

    Args:
        config: Parsed docs target configuration.

    Raises:
        ConfigError: If the MkDocs config file is missing.
    """

    if not config.config_file:
        raise ConfigError(f"`docs.targets.{config.name}.config_file` is required")


def _validate_doxygen(config: DocsTargetConfig) -> None:
    """Validate doxygen target configuration.

    Args:
        config: Parsed docs target configuration.

    Raises:
        ConfigError: If the Doxygen config file is missing.
    """

    if not config.config_file:
        raise ConfigError(f"`docs.targets.{config.name}.config_file` is required")


DOCS_BACKENDS: dict[str, BackendContract[DocsTargetConfig, DocsRequest]] = {
    "sphinx": BackendContract(
        name="sphinx",
        validate=_validate_sphinx,
        plan=_sphinx_plan,
    ),
    "mkdocs": BackendContract(
        name="mkdocs",
        validate=_validate_mkdocs,
        plan=_mkdocs_plan,
    ),
    "doxygen": BackendContract(
        name="doxygen",
        validate=_validate_doxygen,
        plan=_doxygen_plan,
    ),
}
