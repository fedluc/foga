"""Helpers for the ``devkit deploy`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.deploy import plan_deploy
from ..config.loading import load_config
from ..config.models import DevkitConfig
from ..errors import ConfigError
from ..executor import CommandExecutor
from .common import config_path_from_context, select_named_items


@dataclass(slots=True)
class DeployArgs:
    """Parsed arguments for the deploy command."""

    targets: list[str] | None
    dry_run: bool


def deploy_command(
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
            help="Run only the named deploy target. Repeat to select multiple targets.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned deploy commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured deployment workflows."""
    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = DeployArgs(targets=targets, dry_run=dry_run)
    return run_deploy(config, executor, args)


def run_deploy(
    config: DevkitConfig, executor: CommandExecutor, args: DeployArgs
) -> int:
    """Execute configured deploy workflows."""
    selected = select_named_items(config.deploy, args.targets, "deploy target")
    plan = plan_deploy(config.project_root, list(selected.values()))
    if not plan.specs:
        raise ConfigError("No deploy workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
