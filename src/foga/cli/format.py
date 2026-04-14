"""Helpers for the ``foga format`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.formatting import plan_format
from ..config.constants import (
    ALL_WORKFLOW_SELECTION,
    CPP_WORKFLOW_KIND,
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
    select_named_items,
    selection_value,
)


@dataclass(slots=True)
class FormatArgs:
    """Parsed arguments for the format command.

    Attributes:
        selection: Optional format kind selected from the CLI.
        targets: Optional format target names selected from the CLI.
        dry_run: Whether to print commands without executing them.
    """

    selection: str | None
    targets: list[str] | None
    dry_run: bool


def format_command(
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
                "Run only the selected format kind: "
                f"{CPP_WORKFLOW_KIND}, {PYTHON_WORKFLOW_KIND}, "
                f"or {ALL_WORKFLOW_SELECTION}."
            ),
            metavar=WORKFLOW_SELECTION_METAVAR,
        ),
    ] = None,
    targets: Annotated[
        list[str] | None,
        typer.Option(
            "--target",
            help="Run only the named format target. Repeat to select multiple targets.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned format commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured format workflows.

    Args:
        ctx: Typer context carrying the resolved config path.
        profile: Optional profile name applied before command planning.
        selection: Optional format kind selector.
        targets: Optional target names to run.
        dry_run: Whether to print commands without executing them.

    Returns:
        Process exit code for the format command.
    """

    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = FormatArgs(
        selection=selection_value(selection),
        targets=targets,
        dry_run=dry_run,
    )
    return run_format(config, executor, args)


def run_format(config: FogaConfig, executor: CommandExecutor, args: FormatArgs) -> int:
    """Execute configured format workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run or print command specs.
        args: Parsed CLI arguments for ``foga format``.

    Returns:
        Process exit code for the format command.

    Raises:
        ConfigError: If no format workflows match the requested selection.
    """

    resolved_selection = args.selection or config.formatters.default
    selected_by_kind = config.formatters.select_targets(args.selection)
    selected = select_named_items(selected_by_kind, args.targets, "format target")
    plan = plan_format(config.project_root, list(selected.values()))
    if not plan.specs:
        if resolved_selection and resolved_selection != ALL_WORKFLOW_SELECTION:
            raise ConfigError(f"No {resolved_selection} format workflows configured")
        raise ConfigError("No format workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
