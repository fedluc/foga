"""Helpers for the ``foga docs`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.docs import plan_docs
from ..config.loading import load_config
from ..config.models import FogaConfig
from ..errors import ConfigError
from ..executor import CommandExecutor
from .common import config_path_from_context


@dataclass(slots=True)
class DocsArgs:
    """Parsed arguments for the docs command.

    Attributes:
        targets: Optional docs target names selected from the CLI.
        dry_run: Whether to print commands without executing them.
    """

    targets: list[str] | None
    dry_run: bool


def docs_command(
    ctx: typer.Context,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Apply a named configuration profile before resolving the command.",
        ),
    ] = None,
    targets: Annotated[
        list[str] | None,
        typer.Option(
            "--target",
            help="Run only the named docs target. Repeat to select multiple targets.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned docs commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured documentation workflows.

    Args:
        ctx: Typer context carrying the resolved config path.
        profile: Optional profile name to apply before resolving commands.
        targets: Optional docs target names to run.
        dry_run: Whether to print commands without executing them.

    Returns:
        Process exit code for the invoked docs command.
    """

    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = DocsArgs(targets=targets, dry_run=dry_run)
    return run_docs(config, executor, args)


def run_docs(config: FogaConfig, executor: CommandExecutor, args: DocsArgs) -> int:
    """Execute configured documentation workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run or print command specs.
        args: Parsed docs command arguments.

    Returns:
        Process exit code for the docs command.

    Raises:
        ConfigError: If no docs workflows are configured.
    """

    selected = config.docs.selected_targets(args.targets)
    plan = plan_docs(config.project_root, list(selected.values()))
    if not plan.specs:
        raise ConfigError("No docs workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
