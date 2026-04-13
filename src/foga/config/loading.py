"""Config file loading and top-level YAML validation."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..errors import ConfigError
from .constants import DEFAULT_CONFIG_FILENAME
from .merge import apply_profile
from .models import FogaConfig
from .parsing import _parse_config


def load_config(
    config_path: str | Path = DEFAULT_CONFIG_FILENAME, profile: str | None = None
) -> FogaConfig:
    """Load, merge, and validate a foga configuration file.

    Args:
        config_path: Path to the ``DEFAULT_CONFIG_FILENAME`` file.
        profile: Optional profile to merge into the base configuration.

    Returns:
        Parsed configuration object.

    Raises:
        ConfigError: If the configuration file is missing or malformed.
    """

    path = Path(config_path).resolve()
    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        details: dict[str, str] = {"File": str(path)}
        if mark is not None:
            details["Location"] = f"line {mark.line + 1}, column {mark.column + 1}"
        raise ConfigError(
            "invalid YAML syntax in the configuration file",
            details=details,
            hint="Fix the YAML syntax error and rerun `foga validate`.",
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError(
            "configuration root must be a mapping",
            details={"File": str(path)},
            hint=(
                f"Start `{DEFAULT_CONFIG_FILENAME}` with a top-level mapping such as "
                "`project:`, `build:`, or `test:`."
            ),
        )

    merged = apply_profile(data, profile)
    return _parse_config(merged, path.parent)
