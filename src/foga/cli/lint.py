"""Helpers for the ``foga lint`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.linting import plan_lint
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
class LintArgs:
    """Parsed arguments for the lint command."""

    selection: str | None
    targets: list[str] | None
    dry_run: bool


def lint_command(
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
                "Run only the selected lint kind: "
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
            help="Run only the named lint target. Repeat to select multiple targets.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned lint commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured lint workflows."""

    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = LintArgs(
        selection=selection_value(selection),
        targets=targets,
        dry_run=dry_run,
    )
    return run_lint(config, executor, args)


def run_lint(config: FogaConfig, executor: CommandExecutor, args: LintArgs) -> int:
    """Execute configured lint workflows."""

    resolved_selection = args.selection or config.linters.default
    selected_by_kind = config.linters.select_targets(args.selection)
    selected = select_named_items(selected_by_kind, args.targets, "lint target")
    plan = plan_lint(config.project_root, list(selected.values()))
    if not plan.specs:
        if resolved_selection and resolved_selection != ALL_WORKFLOW_SELECTION:
            raise ConfigError(f"No {resolved_selection} lint workflows configured")
        raise ConfigError("No lint workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
