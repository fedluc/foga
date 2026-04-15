"""Helpers for the ``foga install`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.install import plan_install
from ..config.loading import load_config
from ..config.models import FogaConfig
from ..errors import ConfigError
from ..executor import CommandExecutor
from .common import config_path_from_context, select_named_items


@dataclass(slots=True)
class InstallArgs:
    """Parsed arguments for the install command.

    Attributes:
        targets: Optional install target names selected from the CLI.
        dry_run: Whether to print commands without executing them.
    """

    targets: list[str] | None
    dry_run: bool


def install_command(
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
            help=(
                "Run only the named install target. Repeat to select multiple targets."
            ),
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned install commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured installation workflows.

    Args:
        ctx: Typer context carrying the resolved config path.
        profile: Optional profile name to apply before resolving commands.
        targets: Optional install target names to run.
        dry_run: Whether to print commands without executing them.

    Returns:
        Process exit code for the invoked install command.
    """

    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = InstallArgs(targets=targets, dry_run=dry_run)
    return run_install(config, executor, args)


def run_install(
    config: FogaConfig, executor: CommandExecutor, args: InstallArgs
) -> int:
    """Execute configured install workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run or print command specs.
        args: Parsed install command arguments.

    Returns:
        Process exit code for the install command.

    Raises:
        ConfigError: If no install workflows are configured.
    """

    selected = select_named_items(config.install, args.targets, "install target")
    plan = plan_install(config.project_root, list(selected.values()))
    if not plan.specs:
        raise ConfigError("No install workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
