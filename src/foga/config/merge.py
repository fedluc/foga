"""Profile merging helpers for foga configuration."""

from __future__ import annotations

from typing import Any

from ..errors import ConfigError


def apply_profile(data: dict[str, Any], profile: str | None) -> dict[str, Any]:
    """Merge an optional named profile into the base configuration.

    Args:
        data: Raw configuration mapping.
        profile: Optional profile name to apply.

    Returns:
        Configuration mapping after profile application.

    Raises:
        ConfigError: If the profile configuration is malformed or missing.
    """

    base = deep_copy_mapping(data)
    profiles = base.pop("profiles", {})
    if profiles and not isinstance(profiles, dict):
        raise ConfigError("`profiles` must be a mapping")

    active_profile = profile
    if active_profile is None and isinstance(profiles, dict) and "default" in profiles:
        active_profile = "default"

    if active_profile is None:
        return base
    if active_profile not in profiles:
        raise ConfigError(f"Unknown profile: {active_profile}")
    profile_data = profiles[active_profile]
    if not isinstance(profile_data, dict):
        raise ConfigError(f"Profile `{active_profile}` must be a mapping")
    _validate_profile_override(base, profile_data, f"profiles.{active_profile}")
    return _deep_merge(base, profile_data)


def deep_copy_mapping(value: dict[str, Any]) -> dict[str, Any]:
    """Create a deep copy of a mapping.

    Args:
        value: Mapping to copy.

    Returns:
        Deep copy of ``value``.
    """

    return {key: _deep_copy(item) for key, item in value.items()}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge one mapping into another.

    Args:
        base: Base mapping to copy.
        override: Mapping whose values override the base mapping.

    Returns:
        Deeply merged mapping.
    """

    result = deep_copy_mapping(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = _deep_copy(value)
    return result


def _validate_profile_override(
    base: dict[str, Any], override: dict[str, Any], path: str
) -> None:
    """Validate that a profile override is compatible with the base config.

    Args:
        base: Base configuration mapping before profile application.
        override: Profile override mapping at the current path.
        path: Configuration path for field-level diagnostics.

    Raises:
        ConfigError: If the override changes container shape or swaps an
            existing backend identifier.
    """

    for key, value in override.items():
        current_path = f"{path}.{key}"
        if key not in base:
            continue

        base_value = base[key]
        if isinstance(base_value, dict):
            _validate_mapping_override(base_value, value, current_path)
            continue

        if isinstance(base_value, list):
            _validate_list_override(value, current_path)
            continue

        _validate_scalar_override(key, base_value, value, current_path)


def _validate_mapping_override(
    base_value: dict[str, Any], value: Any, path: str
) -> None:
    """Validate an override for an existing mapping-valued config field.

    Args:
        base_value: Existing mapping from the base configuration.
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a mapping with a non-mapping.
    """

    if not isinstance(value, dict):
        raise ConfigError(f"`{path}` must remain a mapping in profile overrides")
    _validate_profile_override(base_value, value, path)


def _validate_list_override(value: Any, path: str) -> None:
    """Validate an override for an existing list-valued config field.

    Args:
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a list with a different shape.
    """

    if isinstance(value, dict):
        raise ConfigError(f"`{path}` cannot replace a scalar or list with a mapping")
    if not isinstance(value, list):
        raise ConfigError(f"`{path}` must remain a list in profile overrides")


def _validate_scalar_override(key: str, base_value: Any, value: Any, path: str) -> None:
    """Validate an override for an existing scalar-valued config field.

    Args:
        key: Field name from the configuration mapping.
        base_value: Existing scalar from the base configuration.
        value: Override value supplied by the active profile.
        path: Configuration path for diagnostics.

    Raises:
        ConfigError: If the override replaces a scalar with a mapping or swaps
            an existing backend identifier.
    """

    if isinstance(value, dict):
        raise ConfigError(f"`{path}` cannot replace a scalar or list with a mapping")
    if key == "backend" and base_value != value:
        raise ConfigError(
            f"`{path}` cannot change backend from `{base_value}` to `{value}` "
            "in profile overrides"
        )


def _deep_copy(value: Any) -> Any:
    """Create a deep copy of nested mappings and lists.

    Args:
        value: Value to copy.

    Returns:
        Deep copy of ``value``.
    """

    if isinstance(value, dict):
        return deep_copy_mapping(value)
    if isinstance(value, list):
        return [_deep_copy(item) for item in value]
    return value
