"""CLI entrypoint and top-level command registration for foga."""

from __future__ import annotations

import sys
from typing import Annotated

import click
import typer

from ..config.constants import DEFAULT_CONFIG_FILENAME
from ..errors import FogaError
from ..output import format_error
from .build import build_command
from .clean import clean_command
from .deploy import deploy_command
from .format import format_command
from .inspect import build_inspect_app
from .lint import lint_command
from .test import test_command
from .validate import validate_command

app = typer.Typer(
    add_completion=False,
    help="Unified developer CLI for Python/C++ package workflows.",
    no_args_is_help=False,
    pretty_exceptions_enable=False,
)
app.add_typer(build_inspect_app(), name="inspect")
app.command("build")(build_command)
app.command("test")(test_command)
app.command("format")(format_command)
app.command("lint")(lint_command)
app.command("deploy")(deploy_command)
app.command("clean")(clean_command)
app.command("validate")(validate_command)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    config: Annotated[
        str,
        typer.Option(
            "--config",
            help="Path to the foga YAML configuration file to load.",
        ),
    ] = DEFAULT_CONFIG_FILENAME,
) -> None:
    """Initialize shared CLI context and render root help when needed."""
    ctx.obj = config
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help(), nl=False)
        raise typer.Exit(code=0)


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
            prog_name="foga",
            standalone_mode=False,
        )
    except FogaError as exc:
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


if __name__ == "__main__":
    raise SystemExit(main())
