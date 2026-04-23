"""Shared terminal output helpers for user-facing CLI messages."""

from __future__ import annotations

import os
import sys
from typing import TextIO

from .config.constants import DEFAULT_CONFIG_FILENAME
from .errors import ConfigError, ExecutionError, FogaError

FOGA_TEAL_HEX = "#16859d"
FOGA_PINK_HEX = "#ff4ca5"
FOGA_AMBER_HEX = "#f59e0b"
FOGA_TEAL_RGB = (22, 133, 157)
FOGA_PINK_RGB = (255, 76, 165)
FOGA_AMBER_RGB = (245, 158, 11)

RESET = "\033[0m"


def _ansi_truecolor(rgb: tuple[int, int, int], *, bold: bool = False) -> str:
    """Build an ANSI truecolor escape sequence."""
    prefix = "1;" if bold else ""
    red, green, blue = rgb
    return f"\033[{prefix}38;2;{red};{green};{blue}m"


STYLES = {
    "brand": _ansi_truecolor(FOGA_PINK_RGB, bold=True),
    "heading": _ansi_truecolor(FOGA_TEAL_RGB, bold=True),
    "label": _ansi_truecolor(FOGA_TEAL_RGB),
    "success": _ansi_truecolor(FOGA_TEAL_RGB, bold=True),
    "warning": _ansi_truecolor(FOGA_AMBER_RGB, bold=True),
    "error": _ansi_truecolor(FOGA_PINK_RGB, bold=True),
    "muted": "\033[2m",
}


def _stream_or_default(stream: TextIO | None, fallback: TextIO) -> TextIO:
    """Resolve an optional stream to a concrete stream object."""
    return stream if stream is not None else fallback


def supports_color(stream: TextIO | None) -> bool:
    """Return whether ANSI color output should be emitted for a stream."""
    resolved = _stream_or_default(stream, sys.stdout)
    return (
        bool(getattr(resolved, "isatty", lambda: False)())
        and "NO_COLOR" not in os.environ
    )


def style(text: str, token: str, stream: TextIO | None = None) -> str:
    """Wrap text in ANSI style codes when the stream supports colors."""
    resolved = _stream_or_default(stream, sys.stdout)
    if not supports_color(resolved):
        return text
    return f"{STYLES[token]}{text}{RESET}"


def format_status(
    title: str, message: str, *, tone: str = "label", stream: TextIO | None = None
) -> str:
    """Format a labeled status line for CLI output."""
    return f"{style(title, tone, stream)}: {message}"


def format_detail(label: str, value: str, *, stream: TextIO | None = None) -> str:
    """Format a secondary detail line for CLI output."""
    return f"  {style(label, 'label', stream)}: {value}"


def format_command(
    command: str,
    *,
    dry_run: bool,
    description: str | None,
    stream: TextIO | None = None,
) -> str:
    """Format command execution or dry-run output."""
    tone = "warning" if dry_run else "heading"
    mode = "DRY-RUN" if dry_run else "RUN"
    line = format_status(mode, command, tone=tone, stream=stream)
    if description:
        line = f"{line}\n{format_detail('Step', description, stream=stream)}"
    return line


def format_clean_action(
    path: str, *, is_dir: bool, stream: TextIO | None = None
) -> str:
    """Format a cleanup action line."""
    item_type = "directory" if is_dir else "file"
    return format_status(
        "Clean",
        f"removed {item_type} `{path}`",
        tone="success",
        stream=stream,
    )


def format_clean_summary(removed_any: bool, *, stream: TextIO | None = None) -> str:
    """Format the final clean summary."""
    message = "completed requested cleanup" if removed_any else "nothing to remove"
    tone = "success" if removed_any else "warning"
    return format_status("Clean", message, tone=tone, stream=stream)


def format_error(exc: FogaError, *, stream: TextIO | None = None) -> str:
    """Render a structured CLI error message."""
    resolved = _stream_or_default(stream, sys.stderr)
    if isinstance(exc, ConfigError):
        title = "Configuration error"
        hint = (
            exc.hint or f"Update `{DEFAULT_CONFIG_FILENAME}` and rerun `foga validate`."
        )
    elif isinstance(exc, ExecutionError):
        title = "Execution failed"
        hint = (
            exc.hint
            or "Inspect the command output above, fix the underlying tool "
            "error, and retry."
        )
    else:
        title = "Error"
        hint = exc.hint

    lines = [format_status(title, exc.message, tone="error", stream=resolved)]
    for label, value in exc.details.items():
        lines.append(format_detail(label, value, stream=resolved))
    if hint:
        lines.append(format_detail("Hint", hint, stream=resolved))
    return "\n".join(lines)
