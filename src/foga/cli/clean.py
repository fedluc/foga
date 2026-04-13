"""Helpers for the ``foga clean`` command."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import typer

from ..config.loading import load_config
from ..config.models import FogaConfig
from ..output import format_clean_action, format_clean_summary
from .common import config_path_from_context


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
    config = load_config(config_path_from_context(ctx), profile)
    return run_clean(config)


def run_clean(config: FogaConfig) -> int:
    """Remove configured build artifacts from the project root."""
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
