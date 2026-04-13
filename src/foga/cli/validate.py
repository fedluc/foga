"""Helpers for the ``foga validate`` command."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer
import yaml

from ..config.loading import load_config
from ..config.models import FogaConfig
from ..output import format_detail, format_status
from .common import config_path_from_context


@dataclass(frozen=True)
class ValidationSummary:
    """User-facing validation summary details."""

    project_name: str
    active_profile: str | None
    build_workflows: list[str]
    test_runners: list[str]
    deploy_targets: list[str]
    clean_paths: list[str]


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
    return run_validate(config_path_from_context(ctx), profile)


def run_validate(config_path: str | Path, profile: str | None) -> int:
    """Validate the configuration file and print a concise summary.

    Args:
        config_path: Path to the configuration file to validate.
        profile: Optional profile name to apply before validation.

    Returns:
        Process exit code for the validation command.
    """
    config = load_config(config_path, profile)
    summary = _build_validation_summary(config, config_path, profile)
    print(_format_validation_summary(summary))
    return 0


def _build_validation_summary(
    config: FogaConfig, config_path: str | Path, requested_profile: str | None
) -> ValidationSummary:
    """Build the success summary for a validated configuration.

    Args:
        config: Loaded configuration object.
        config_path: Path to the configuration file that was validated.
        requested_profile: Explicit profile name requested by the user.

    Returns:
        Structured validation summary for display.
    """
    return ValidationSummary(
        project_name=config.project.name,
        active_profile=_resolve_active_profile_name(config_path, requested_profile),
        build_workflows=list(config.build.entries) or config.build.available_kinds(),
        test_runners=list(config.tests.runners),
        deploy_targets=list(config.deploy),
        clean_paths=config.clean.paths,
    )


def _format_validation_summary(summary: ValidationSummary) -> str:
    """Render the validate success summary.

    Args:
        summary: Validation details to display.

    Returns:
        User-facing summary string.
    """
    lines = [
        format_status(
            "Validation OK",
            f"project `{summary.project_name}` is ready to use",
            tone="success",
        ),
        format_detail("Profile", summary.active_profile or "none"),
        format_detail(
            "Build workflows",
            ", ".join(summary.build_workflows) if summary.build_workflows else "none",
        ),
        format_detail(
            "Test runners",
            ", ".join(summary.test_runners) if summary.test_runners else "none",
        ),
        format_detail(
            "Deploy targets",
            ", ".join(summary.deploy_targets) if summary.deploy_targets else "none",
        ),
        format_detail(
            "Clean paths",
            ", ".join(summary.clean_paths) if summary.clean_paths else "none",
        ),
    ]
    return "\n".join(lines)


def _resolve_active_profile_name(
    config_path: str | Path, requested_profile: str | None
) -> str | None:
    """Resolve the active profile name for validate output.

    Args:
        config_path: Path to the configuration file being validated.
        requested_profile: Explicit profile name requested by the user.

    Returns:
        Active profile name, if one can be determined.
    """
    if requested_profile is not None:
        return requested_profile

    path = Path(config_path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return None

    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        return None
    if "default" in profiles:
        return "default"
    return None
