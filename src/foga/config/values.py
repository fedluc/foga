"""Primitive config value parsing helpers."""

from __future__ import annotations

from typing import Any

from ..errors import ConfigError
from .constants import WORKFLOW_SELECTIONS
from .models import HookConfig


def reject_unknown_keys(
    data: dict[str, Any], section: str, allowed_keys: set[str]
) -> None:
    """Reject unexpected keys in a top-level config section.

    Args:
        data: Raw section mapping to validate.
        section: Top-level section name used in the error message.
        allowed_keys: Accepted keys for the section.

    Raises:
        ConfigError: If the section contains unsupported keys.
    """

    for key in data:
        if key in allowed_keys:
            continue
        allowed = ", ".join(sorted(allowed_keys))
        raise ConfigError(
            f"`{section}.{key}` is not a supported configuration key",
            hint=f"Use only these keys under `{section}`: {allowed}.",
        )


def required_str(data: dict[str, Any], key: str, path: str) -> str:
    """Read a required non-empty string field.

    Args:
        data: Source mapping.
        key: Mapping key to read.
        path: Full configuration path used in validation errors.

    Returns:
        Non-empty string value.

    Raises:
        ConfigError: If the value is missing, empty, or not a string.
    """

    value = data.get(key)
    if value is None:
        raise ConfigError(f"`{path}` is required")
    if not isinstance(value, str):
        raise ConfigError(f"`{path}` must be a string")
    if not value.strip():
        raise ConfigError(f"`{path}` must not be empty")
    return value


def optional_str(data: dict[str, Any], key: str, path: str) -> str | None:
    """Read an optional string field.

    Args:
        data: Source mapping.
        key: Mapping key to read.
        path: Full configuration path used in validation errors.

    Returns:
        String value when present, otherwise ``None``.

    Raises:
        ConfigError: If the value is present but not a string.
    """

    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError(f"`{path}` must be a string")
    return value


def optional_bool(data: dict[str, Any], key: str, path: str) -> bool | None:
    """Read an optional boolean field.

    Args:
        data: Source mapping.
        key: Mapping key to read.
        path: Full configuration path used in validation errors.

    Returns:
        Boolean value when present, otherwise ``None``.

    Raises:
        ConfigError: If the value is present but not a boolean.
    """

    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ConfigError(f"`{path}` must be a boolean")
    return value


def parse_workflow_selection(value: Any, path: str) -> str | None:
    """Parse a workflow kind selector.

    Args:
        value: Raw selector value from configuration.
        path: Configuration path used in validation errors.

    Returns:
        Parsed workflow kind or ``None`` when the field is unset.

    Raises:
        ConfigError: If the selector is not one of the supported values.
    """

    if value is None:
        return None
    if not isinstance(value, str) or value not in WORKFLOW_SELECTIONS:
        expected = ", ".join(WORKFLOW_SELECTIONS)
        raise ConfigError(f"`{path}` must be one of: {expected}")
    return value


def parse_hooks(data: Any, path: str) -> HookConfig:
    """Parse hook configuration from an optional mapping.

    Args:
        data: Raw hook configuration value.
        path: Configuration path used in validation errors.

    Returns:
        Parsed hook configuration.

    Raises:
        ConfigError: If the hook configuration is malformed.
    """

    if data is None:
        return HookConfig()
    if not isinstance(data, dict):
        raise ConfigError(f"`{path}` must be a mapping")
    reject_unknown_keys(data, path, {"pre", "post"})
    return HookConfig(
        pre=command_matrix(data.get("pre"), f"{path}.pre"),
        post=command_matrix(data.get("post"), f"{path}.post"),
    )


def command_array(value: Any, path: str, *, field_name: str) -> list[str]:
    """Validate one non-empty command array.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.
        field_name: User-facing field name used in validation hints.

    Returns:
        Validated command array, or an empty list when ``value`` is ``None``.

    Raises:
        ConfigError: If the value is not a non-empty list of strings.
    """

    if value is None:
        return []
    if isinstance(value, str):
        raise ConfigError(
            f"`{path}` must be a non-empty list of strings",
            hint=(
                f"Shell command strings are not supported for {field_name}; "
                'use a list such as `["uv", "run"]`.'
            ),
        )
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) for item in value)
    ):
        raise ConfigError(f"`{path}` must be a non-empty list of strings")
    return list(value)


def string_list(value: Any, path: str) -> list[str]:
    """Validate a list of strings and return a shallow copy.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        List of strings, or an empty list when ``value`` is ``None``.

    Raises:
        ConfigError: If the value is not a list of strings.
    """

    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"`{path}` must be a list of strings")
    return list(value)


def string_mapping(value: Any, path: str) -> dict[str, str]:
    """Validate a mapping of string keys and values.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        Mapping of strings, or an empty mapping when ``value`` is ``None``.

    Raises:
        ConfigError: If the value is not a mapping of strings.
    """

    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"`{path}` must be a mapping")
    mapping: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise ConfigError(f"`{path}` must map strings to strings")
        mapping[key] = item
    return mapping


def command_matrix(value: Any, path: str) -> list[list[str]]:
    """Validate a list of non-empty command arrays.

    Args:
        value: Raw configuration value.
        path: Full configuration path used in validation errors.

    Returns:
        Validated command matrix.

    Raises:
        ConfigError: If the value is not a list of non-empty command arrays.
    """

    if value is None:
        return []
    if not isinstance(value, list):
        raise ConfigError(f"`{path}` must be a list of command arrays")
    commands: list[list[str]] = []
    for index, item in enumerate(value):
        if isinstance(item, str):
            raise ConfigError(
                f"`{path}[{index}]` must be a non-empty list of strings",
                hint=(
                    "Shell command strings are not supported in hooks; use a "
                    'list such as `["python3", "script.py"]`.'
                ),
            )
        if (
            not isinstance(item, list)
            or not all(isinstance(part, str) for part in item)
            or not item
        ):
            raise ConfigError(f"`{path}[{index}]` must be a non-empty list of strings")
        commands.append(list(item))
    return commands


def unsupported_backend_message(
    workflow: str, backend: str, supported_backends: set[str]
) -> str:
    """Build a stable error for unsupported backend names.

    Args:
        workflow: Workflow family containing the invalid backend.
        backend: Unsupported backend name from the configuration.
        supported_backends: Registered backend names for the workflow.

    Returns:
        User-facing validation error with the supported backend list.
    """

    supported = ", ".join(sorted(supported_backends))
    return f"Unsupported {workflow} backend: {backend}. Supported backends: {supported}"
