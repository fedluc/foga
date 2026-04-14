"""Shared backend contracts and workflow planning structures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generic, Mapping, TypeVar

from ..errors import ConfigError
from ..executor import CommandSpec

ConfigT = TypeVar("ConfigT")
ContextT = TypeVar("ContextT")


@dataclass(frozen=True)
class BuildRequest:
    """Options used when planning build backend commands.

    Attributes:
        targets: Optional explicit C++ build targets requested by the CLI.
            When unset, the backend should use its configured default targets.
    """

    targets: list[str] | None = None


@dataclass(frozen=True)
class DeployRequest:
    """Options used when planning deploy backend commands.

    Attributes:
        project_root: Project root used to resolve configured deploy artifacts.
    """

    project_root: Path


@dataclass(frozen=True)
class ToolRequest:
    """Options used when planning format or lint commands.

    Attributes:
        project_root: Project root used as the default working directory.
    """

    project_root: Path


@dataclass(frozen=True)
class WorkflowPlan:
    """Prepared command specs for a CLI workflow.

    Attributes:
        specs: Ordered command specs ready for execution or dry-run display.
    """

    specs: list[CommandSpec]


@dataclass(frozen=True)
class BackendContract(Generic[ConfigT, ContextT]):
    """Stable internal contract for backend validation and planning.

    Attributes:
        name: Backend identifier used in configuration.
        validate: Function that validates a parsed backend configuration.
        plan: Function that converts the parsed config into command specs.
    """

    name: str
    validate: Callable[[ConfigT], None]
    plan: Callable[[ConfigT, ContextT], list[CommandSpec]]


def registered_backends(
    registry: Mapping[str, BackendContract[ConfigT, ContextT]],
) -> set[str]:
    """Return backend identifiers from a registry mapping.

    Args:
        registry: Mapping from backend names to backend contracts.

    Returns:
        Set of backend identifiers registered in the mapping.
    """

    return set(registry)


def require_backend_contract(
    workflow: str,
    backend: str,
    registry: Mapping[str, BackendContract[ConfigT, ContextT]],
) -> BackendContract[ConfigT, ContextT]:
    """Resolve a backend contract from a workflow registry.

    Args:
        workflow: Workflow family name used in the error message.
        backend: Requested backend identifier.
        registry: Mapping from backend names to backend contracts.

    Returns:
        Backend contract registered for the requested backend.

    Raises:
        ConfigError: If the backend is not registered for the workflow.
    """

    try:
        return registry[backend]
    except KeyError as exc:
        supported = ", ".join(sorted(registry))
        raise ConfigError(
            f"Unsupported {workflow} backend: {backend}",
            hint=f"Choose one of the supported {workflow} backends: {supported}.",
        ) from exc
