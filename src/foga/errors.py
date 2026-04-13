from __future__ import annotations


class FogaError(Exception):
    """Base error for foga."""

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
        details: dict[str, str] | None = None,
    ) -> None:
        """Initialize a user-facing foga error."""
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.details = details or {}

    def __str__(self) -> str:
        """Return the plain error message."""
        return self.message


class ConfigError(FogaError):
    """Raised when configuration is invalid."""


class ExecutionError(FogaError):
    """Raised when command execution fails."""
