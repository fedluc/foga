"""CLI entrypoint and top-level command registration for foga."""

from __future__ import annotations

import sys
from typing import Annotated

import click
import typer
import typer.rich_utils as typer_rich_utils

from .. import __version__
from ..config.constants import DEFAULT_CONFIG_FILENAME
from ..errors import FogaError
from ..output import FOGA_PINK_HEX, FOGA_TEAL_HEX, format_error, format_status
from .build import build_command
from .clean import clean_command
from .deploy import deploy_command
from .docs import docs_command
from .format import format_command
from .inspect import build_inspect_app
from .install import install_command
from .lint import lint_command
from .test import test_command
from .validate import validate_command


def _configure_rich_help_palette() -> None:
    """Apply the foga brand palette to Typer's Rich help output."""
    brand_pink = f"bold {FOGA_PINK_HEX}"
    brand_teal = f"bold {FOGA_TEAL_HEX}"
    accent_teal = FOGA_TEAL_HEX

    typer_rich_utils.STYLE_USAGE = brand_pink
    typer_rich_utils.STYLE_USAGE_COMMAND = brand_teal
    typer_rich_utils.STYLE_OPTION = brand_teal
    typer_rich_utils.STYLE_SWITCH = brand_teal
    typer_rich_utils.STYLE_NEGATIVE_OPTION = brand_pink
    typer_rich_utils.STYLE_NEGATIVE_SWITCH = brand_pink
    typer_rich_utils.STYLE_METAVAR = brand_pink
    typer_rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = brand_teal
    typer_rich_utils.STYLE_OPTIONS_PANEL_BORDER = "dim"
    typer_rich_utils.STYLE_COMMANDS_PANEL_BORDER = "dim"
    typer_rich_utils.STYLE_ERRORS_PANEL_BORDER = FOGA_PINK_HEX
    typer_rich_utils.STYLE_ABORTED = brand_pink
    typer_rich_utils.STYLE_DEPRECATED = brand_pink
    typer_rich_utils.STYLE_REQUIRED_SHORT = brand_pink
    typer_rich_utils.STYLE_REQUIRED_LONG = brand_pink
    typer_rich_utils.STYLE_HELPTEXT = ""
    typer_rich_utils.STYLE_HELPTEXT_FIRST_LINE = ""
    typer_rich_utils.STYLE_OPTION_HELP = ""
    typer_rich_utils.STYLE_OPTION_ENVVAR = accent_teal
    typer_rich_utils.RICH_HELP = (
        f"Try [bold {FOGA_TEAL_HEX}]'{{command_path}} {{help_option}}'[/] for help."
    )


_configure_rich_help_palette()

app = typer.Typer(
    add_completion=False,
    help="Unified developer CLI for Python/C++ package workflows.",
    no_args_is_help=False,
    pretty_exceptions_enable=False,
)
app.add_typer(build_inspect_app(), name="inspect")
app.command("build")(build_command)
app.command("test")(test_command)
app.command("docs")(docs_command)
app.command("format")(format_command)
app.command("install")(install_command)
app.command("lint")(lint_command)
app.command("deploy")(deploy_command)
app.command("clean")(clean_command)
app.command("validate")(validate_command)


def _version_text() -> str:
    """Return the user-facing CLI version string.

    Returns:
        Installed ``foga`` version string rendered for CLI output.
    """

    return f"foga {__version__}"


def _show_version_callback(value: bool) -> None:
    """Print the CLI version and exit when the eager flag is used.

    Args:
        value: Whether the ``--version`` flag was requested.

    Raises:
        typer.Exit: Always, after printing the installed version.
    """

    if not value:
        return
    typer.echo(_version_text())
    raise typer.Exit(code=0)


@app.command("version")
def version_command() -> int:
    """Print the installed foga version.

    Returns:
        Process exit code for the version command.
    """

    typer.echo(_version_text())
    return 0


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
    show_version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_show_version_callback,
            help="Show the installed foga version and exit.",
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Initialize shared CLI context and render root help when needed."""
    ctx.obj = config
    _ = show_version
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
        print(
            format_status("ABORT", "operation cancelled", tone="warning"),
            file=sys.stderr,
        )
        return 1

    if isinstance(result, int):
        return result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
