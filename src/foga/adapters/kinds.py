"""Workflow-kind helpers shared across adapter and config modules."""

from __future__ import annotations

from ..config.constants import CPP_WORKFLOW_KIND, PYTHON_WORKFLOW_KIND
from ..errors import ConfigError

TEST_BACKEND_KINDS: dict[str, str] = {
    "pytest": PYTHON_WORKFLOW_KIND,
    "tox": PYTHON_WORKFLOW_KIND,
    "ctest": CPP_WORKFLOW_KIND,
}

FORMAT_BACKEND_KINDS: dict[str, str] = {
    "black": PYTHON_WORKFLOW_KIND,
    "ruff-format": PYTHON_WORKFLOW_KIND,
    "clang-format": CPP_WORKFLOW_KIND,
}

LINT_BACKEND_KINDS: dict[str, str] = {
    "ruff-check": PYTHON_WORKFLOW_KIND,
    "clang-tidy": CPP_WORKFLOW_KIND,
}


def test_backend_kind(backend: str) -> str:
    """Return the logical kind associated with a test backend.

    Args:
        backend: Registered test backend identifier.

    Returns:
        Logical test kind used for CLI selection.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return TEST_BACKEND_KINDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(TEST_BACKEND_KINDS))
        raise ConfigError(
            f"Unsupported test backend: {backend}",
            hint=f"Choose one of the supported test backends: {supported}.",
        ) from exc


def format_backend_kind(backend: str) -> str:
    """Return the logical kind associated with a format backend.

    Args:
        backend: Registered format backend identifier.

    Returns:
        Logical format kind used for CLI selection.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return FORMAT_BACKEND_KINDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(FORMAT_BACKEND_KINDS))
        raise ConfigError(
            f"Unsupported format backend: {backend}",
            hint=f"Choose one of the supported format backends: {supported}.",
        ) from exc


def lint_backend_kind(backend: str) -> str:
    """Return the logical kind associated with a lint backend.

    Args:
        backend: Registered lint backend identifier.

    Returns:
        Logical lint kind used for CLI selection.

    Raises:
        ConfigError: If the backend name is not registered.
    """

    try:
        return LINT_BACKEND_KINDS[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(LINT_BACKEND_KINDS))
        raise ConfigError(
            f"Unsupported lint backend: {backend}",
            hint=f"Choose one of the supported lint backends: {supported}.",
        ) from exc
