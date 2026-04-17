"""Shared helpers for Typer-based CLI commands."""

from __future__ import annotations

from enum import Enum

import typer

from ..config.constants import (
    ALL_WORKFLOW_SELECTION,
    CPP_WORKFLOW_KIND,
    PYTHON_WORKFLOW_KIND,
)


class WorkflowSelection(str, Enum):
    """Supported workflow selection values exposed by the CLI."""

    CPP = CPP_WORKFLOW_KIND
    PYTHON = PYTHON_WORKFLOW_KIND
    ALL = ALL_WORKFLOW_SELECTION


WORKFLOW_SELECTION_METAVAR = (
    f"{CPP_WORKFLOW_KIND}|{PYTHON_WORKFLOW_KIND}|{ALL_WORKFLOW_SELECTION}"
)


def selection_value(selection: WorkflowSelection | None) -> str | None:
    """Normalize optional selection enums to raw config values."""
    if selection is None:
        return None
    return selection.value


def config_path_from_context(ctx: typer.Context) -> str:
    """Resolve the top-level ``--config`` option from the root CLI context."""
    root_context = ctx.find_root()
    config_path = root_context.obj
    if not isinstance(config_path, str):
        raise RuntimeError("CLI context was not initialized")
    return config_path
