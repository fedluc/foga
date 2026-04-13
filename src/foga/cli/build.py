"""Helpers for the ``foga build`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.build import plan_build
from ..config.constants import (
    ALL_WORKFLOW_SELECTION,
    NATIVE_WORKFLOW_KIND,
    PYTHON_WORKFLOW_KIND,
)
from ..config.loading import load_config
from ..config.models import FogaConfig
from ..errors import ConfigError
from ..executor import CommandExecutor
from .common import (
    WORKFLOW_SELECTION_METAVAR,
    WorkflowSelection,
    config_path_from_context,
    selection_value,
)


@dataclass(slots=True)
class BuildArgs:
    """Parsed arguments for the build command."""

    selection: str | None
    targets: list[str] | None
    dry_run: bool


def build_command(
    ctx: typer.Context,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Apply a named configuration profile before resolving the command.",
        ),
    ] = None,
    selection: Annotated[
        WorkflowSelection | None,
        typer.Argument(
            help=(
                "Run only the selected build kind: "
                f"{NATIVE_WORKFLOW_KIND}, {PYTHON_WORKFLOW_KIND}, "
                f"or {ALL_WORKFLOW_SELECTION}."
            ),
            metavar=WORKFLOW_SELECTION_METAVAR,
        ),
    ] = None,
    targets: Annotated[
        list[str] | None,
        typer.Option(
            "--target",
            help=(
                "Build only the named native target. Repeat to include "
                "multiple targets."
            ),
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned build commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured build workflows."""
    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = BuildArgs(
        selection=selection_value(selection),
        targets=targets,
        dry_run=dry_run,
    )
    return run_build(config, executor, args)


def run_build(config: FogaConfig, executor: CommandExecutor, args: BuildArgs) -> int:
    """Execute configured build workflows."""
    resolved_selection = args.selection or config.build.default

    if args.targets and config.build.selected_kinds(args.selection) == [
        PYTHON_WORKFLOW_KIND
    ]:
        raise ConfigError("`build --target` can only be used with native builds")

    plan = plan_build(config.build, selection=args.selection, targets=args.targets)
    if not plan.specs:
        if resolved_selection and resolved_selection != ALL_WORKFLOW_SELECTION:
            raise ConfigError(f"No {resolved_selection} build workflows configured")
        raise ConfigError("No build workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
