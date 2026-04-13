"""Workflow-kind helpers shared across adapter and config modules."""

from __future__ import annotations

from ..config.constants import NATIVE_WORKFLOW_KIND, PYTHON_WORKFLOW_KIND
from ..errors import ConfigError

TEST_BACKEND_KINDS: dict[str, str] = {
    "pytest": PYTHON_WORKFLOW_KIND,
    "tox": PYTHON_WORKFLOW_KIND,
    "ctest": NATIVE_WORKFLOW_KIND,
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
