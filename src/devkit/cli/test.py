"""Helpers for the ``devkit test`` command."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

import typer

from ..adapters.testing import plan_tests
from ..config import DevkitConfig, load_config
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
class TestArgs:
    """Parsed arguments for the test command."""

    selection: str | None
    runner: list[str] | None
    dry_run: bool


def test_command(
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
            help="Run only the selected test kind: native, python, or all.",
            metavar=WORKFLOW_SELECTION_METAVAR,
        ),
    ] = None,
    runner: Annotated[
        list[str] | None,
        typer.Option(
            "--runner",
            help="Run only the named test runner. Repeat to select multiple runners.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Show the planned test commands without executing them.",
        ),
    ] = False,
) -> int:
    """Run configured test workflows."""
    config = load_config(config_path_from_context(ctx), profile)
    executor = CommandExecutor(config.project_root)
    args = TestArgs(
        selection=selection_value(selection),
        runner=runner,
        dry_run=dry_run,
    )
    return run_test(config, executor, args)


def run_test(config: DevkitConfig, executor: CommandExecutor, args: TestArgs) -> int:
    """Execute configured test workflows."""
    resolved_selection = args.selection or config.tests.default
    selected_by_kind = config.tests.select_runners(args.selection)
    selected = select_named_items(selected_by_kind, args.runner, "test runner")
    plan = plan_tests(list(selected.values()))
    if not plan.specs:
        if resolved_selection and resolved_selection != "all":
            raise ConfigError(f"No {resolved_selection} test workflows configured")
        raise ConfigError("No test workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0
