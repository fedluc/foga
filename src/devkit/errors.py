from __future__ import annotations


class DevkitError(Exception):
    """Base error for devkit."""

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize a user-facing devkit error."""
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.details = details or {}

    def __str__(self) -> str:
        """Return the plain error message."""
        return self.message


class ConfigError(DevkitError):
    """Raised when configuration is invalid."""


class ExecutionError(DevkitError):
    """Raised when command execution fails."""
