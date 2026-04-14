"""Docs backend contracts and command planning."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Callable

from ..config.constants import DOCS_SECTION, TARGETS_KEY
from ..config.models import DocsTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import prepend_launcher, split_hooks
from .contracts import (
    BackendContract,
    ToolRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import DOCS_DOXYGEN, DOCS_MKDOCS, DOCS_SPHINX


def plan_docs(project_root: Path, targets: list[DocsTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured docs targets.

    Args:
        project_root: Project root used as the command working directory.
        targets: Parsed docs targets selected for execution.

    Returns:
        Planned command specs for all selected docs targets.
    """

    specs: list[CommandSpec] = []
    request = ToolRequest(project_root=project_root)
    for target in targets:
        contract = require_backend_contract(DOCS_SECTION, target.backend, DOCS_BACKENDS)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def _plan_docs_target(
    config: DocsTargetConfig,
    request: ToolRequest,
    *,
    command_builder: Callable[[DocsTargetConfig], list[str]],
) -> list[CommandSpec]:
    """Build command specs for a docs backend that emits one shell command.

    Args:
        config: Parsed docs target configuration.
        request: Shared tool request with the project root.
        command_builder: Function that builds the backend command.

    Returns:
        Command specs for the selected docs target, including hooks.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=prepend_launcher(command_builder(config), config.launcher),
            cwd=request.project_root,
            env=config.env,
            description=f"docs target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _build_sphinx_command(config: DocsTargetConfig) -> list[str]:
    """Build the ``sphinx-build`` command for a docs target.

    Args:
        config: Parsed Sphinx docs target configuration.

    Returns:
        Command line for the selected Sphinx target.
    """

    return [
        "sphinx-build",
        "-b",
        config.builder or "html",
        config.source_dir or "",
        config.build_dir or "",
        *config.args,
    ]


def _build_mkdocs_command(config: DocsTargetConfig) -> list[str]:
    """Build the ``mkdocs build`` command for a docs target.

    Args:
        config: Parsed MkDocs target configuration.

    Returns:
        Command line for the selected MkDocs target.
    """

    command = ["mkdocs", "build"]
    if config.config_file:
        command.extend(["--config-file", config.config_file])
    if config.build_dir:
        command.extend(["--site-dir", config.build_dir])
    command.extend(config.args)
    return command


def _build_doxygen_command(config: DocsTargetConfig) -> list[str]:
    """Build the ``doxygen`` command for a docs target.

    Args:
        config: Parsed Doxygen target configuration.

    Returns:
        Command line for the selected Doxygen target.
    """

    return ["doxygen", config.config_file or "", *config.args]


def _validate_required_fields(
    config: DocsTargetConfig,
    *,
    fields: tuple[str, ...],
) -> None:
    """Validate required docs target fields for a backend.

    Args:
        config: Parsed docs target configuration.
        fields: Target fields that must be configured.

    Raises:
        ConfigError: If any required field is missing.
    """

    for field_name in fields:
        if getattr(config, field_name):
            continue
        raise ConfigError(
            f"`{DOCS_SECTION}.{TARGETS_KEY}.{config.name}.{field_name}` is required"
        )


DOCS_BACKENDS: dict[str, BackendContract[DocsTargetConfig, ToolRequest]] = {
    DOCS_SPHINX: BackendContract(
        name=DOCS_SPHINX,
        validate=partial(
            _validate_required_fields,
            fields=("source_dir", "build_dir"),
        ),
        plan=partial(_plan_docs_target, command_builder=_build_sphinx_command),
    ),
    DOCS_MKDOCS: BackendContract(
        name=DOCS_MKDOCS,
        validate=partial(_validate_required_fields, fields=("config_file",)),
        plan=partial(_plan_docs_target, command_builder=_build_mkdocs_command),
    ),
    DOCS_DOXYGEN: BackendContract(
        name=DOCS_DOXYGEN,
        validate=partial(_validate_required_fields, fields=("config_file",)),
        plan=partial(_plan_docs_target, command_builder=_build_doxygen_command),
    ),
}
