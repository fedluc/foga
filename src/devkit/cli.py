"""CLI entrypoint and command routing for devkit."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Annotated

import click
import typer

from .adapters.build import plan_build
from .adapters.deploy import plan_deploy
from .adapters.testing import plan_tests
from .config import DevkitConfig, load_config
from .errors import ConfigError, DevkitError
from .executor import CommandExecutor
from .inspect import build_inspect_app
from .output import format_clean_action, format_clean_summary, format_error
from .validate import run_validate


class WorkflowSelection(str, Enum):
    """Supported workflow selection values exposed by the CLI."""

    NATIVE = "native"
    PYTHON = "python"
    ALL = "all"


WORKFLOW_SELECTION_METAVAR = "native|python|all"


@dataclass(slots=True)
class CliContext:
    """Shared top-level CLI context."""

    config: str


@dataclass(slots=True)
class BuildArgs:
    """Parsed arguments for the build command."""

    selection: str | None
    targets: list[str] | None
    dry_run: bool


@dataclass(slots=True)
class TestArgs:
    """Parsed arguments for the test command."""

    selection: str | None
    runner: list[str] | None
    dry_run: bool


@dataclass(slots=True)
class DeployArgs:
    """Parsed arguments for the deploy command."""

    targets: list[str] | None
    dry_run: bool


app = typer.Typer(
    add_completion=False,
    help="Unified developer CLI for Python/C++ package workflows.",
    no_args_is_help=False,
    pretty_exceptions_enable=False,
)
app.add_typer(build_inspect_app(), name="inspect")


def _selection_value(selection: WorkflowSelection | None) -> str | None:
    """Normalize optional selection enums to raw config values."""
    if selection is None:
        return None
    return selection.value


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    config: Annotated[
        str,
        typer.Option(
            "--config",
            help="Path to the devkit YAML configuration file to load.",
        ),
    ] = "devkit.yml",
) -> None:
    """Initialize shared CLI context and render root help when needed."""
    ctx.obj = CliContext(config=config)
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help(), nl=False)
        raise typer.Exit(code=0)


@app.command("build")
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
            help="Run only the selected build kind: native, python, or all.",
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
    cli_context = _require_context(ctx)
    config = load_config(cli_context.config, profile)
    executor = CommandExecutor(config.project_root)
    args = BuildArgs(
        selection=_selection_value(selection),
        targets=targets,
        dry_run=dry_run,
    )
    return _run_build(config, executor, args)


@app.command("test")
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
    cli_context = _require_context(ctx)
    config = load_config(cli_context.config, profile)
    executor = CommandExecutor(config.project_root)
    args = TestArgs(
        selection=_selection_value(selection),
        runner=runner,
        dry_run=dry_run,
    )
    return _run_test(config, executor, args)


@app.command("deploy")
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
    cli_context = _require_context(ctx)
    config = load_config(cli_context.config, profile)
    executor = CommandExecutor(config.project_root)
    args = DeployArgs(targets=targets, dry_run=dry_run)
    return _run_deploy(config, executor, args)


@app.command("clean")
def clean_command(
    ctx: typer.Context,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Apply a named configuration profile before resolving the command.",
        ),
    ] = None,
) -> int:
    """Remove configured build artifacts."""
    cli_context = _require_context(ctx)
    config = load_config(cli_context.config, profile)
    return _run_clean(config)


@app.command("validate")
def validate_command(
    ctx: typer.Context,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            help="Apply a named configuration profile before resolving the command.",
        ),
    ] = None,
) -> int:
    """Validate the configuration file."""
    cli_context = _require_context(ctx)
    return run_validate(cli_context.config, profile)


def _require_context(ctx: typer.Context) -> CliContext:
    """Return the top-level CLI context."""
    root_context = ctx.find_root()
    cli_context = root_context.obj
    if not isinstance(cli_context, CliContext):
        raise RuntimeError("CLI context was not initialized")
    return cli_context


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Args:
        argv: Optional CLI arguments. When omitted, Typer reads from
            ``sys.argv``.

    Returns:
        Process exit code for the invoked command.
    """
    try:
        result = app(
            args=argv,
            prog_name="devkit",
            standalone_mode=False,
        )
    except DevkitError as exc:
        print(format_error(exc), file=sys.stderr)
        return 1
    except click.ClickException as exc:
        exc.show(file=sys.stderr)
        return exc.exit_code
    except click.exceptions.Exit as exc:
        return exc.exit_code
    except click.exceptions.Abort:
        print("Aborted!", file=sys.stderr)
        return 1

    if isinstance(result, int):
        return result
    return 0


def _run_build(config: DevkitConfig, executor: CommandExecutor, args: BuildArgs) -> int:
    """Execute configured build workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated build commands.
        args: Parsed CLI arguments for the ``build`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no matching build workflows are configured or if
            incompatible CLI options are combined.
    """
    resolved_selection = args.selection or config.build.default

    if args.targets and config.build.selected_kinds(args.selection) == ["python"]:
        raise ConfigError("`build --target` can only be used with native builds")

    plan = plan_build(config.build, selection=args.selection, targets=args.targets)
    if not plan.specs:
        if resolved_selection and resolved_selection != "all":
            raise ConfigError(f"No {resolved_selection} build workflows configured")
        raise ConfigError("No build workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


def _run_test(config: DevkitConfig, executor: CommandExecutor, args: TestArgs) -> int:
    """Execute configured test workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated test commands.
        args: Parsed CLI arguments for the ``test`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no matching test workflows are configured.
    """
    resolved_selection = args.selection or config.tests.default
    selected_by_kind = config.tests.select_runners(args.selection)
    selected = _select_named_items(selected_by_kind, args.runner, "test runner")
    plan = plan_tests(list(selected.values()))
    if not plan.specs:
        if resolved_selection and resolved_selection != "all":
            raise ConfigError(f"No {resolved_selection} test workflows configured")
        raise ConfigError("No test workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


def _run_deploy(
    config: DevkitConfig, executor: CommandExecutor, args: DeployArgs
) -> int:
    """Execute configured deploy workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated deploy commands.
        args: Parsed CLI arguments for the ``deploy`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no deploy workflows are configured.
    """
    selected = _select_named_items(config.deploy, args.targets, "deploy target")
    plan = plan_deploy(config.project_root, list(selected.values()))
    if not plan.specs:
        raise ConfigError("No deploy workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


def _select_named_items(
    items: dict[str, object], selected_names: list[str] | None, label: str
) -> dict[str, object]:
    """Filter named configuration items and validate explicit selections.

    Args:
        items: Available named items.
        selected_names: Optional list of names explicitly requested by the user.
        label: Human-readable item label used in validation errors.

    Returns:
        All items when no explicit selection is given, otherwise only the
        requested items.

    Raises:
        ConfigError: If any requested item name is unknown.
    """
    if not selected_names:
        return items

    selected: dict[str, object] = {}
    for name in selected_names:
        if name not in items:
            raise ConfigError(f"Unknown {label}: {name}")
        selected[name] = items[name]
    return selected


def _run_clean(config: DevkitConfig) -> int:
    """Remove configured build artifacts from the project root.

    Args:
        config: Loaded project configuration.

    Returns:
        Process exit code for the command.
    """
    removed_any = False
    for path_str in config.clean.paths:
        path = Path(config.project_root, path_str)
        if not path.exists():
            continue
        if path.is_dir():
            print(format_clean_action(str(path), is_dir=True))
            shutil.rmtree(path)
        else:
            print(format_clean_action(str(path), is_dir=False))
            path.unlink()
        removed_any = True
    print(format_clean_summary(removed_any))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
