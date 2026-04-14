"""Shared backend contracts and workflow planning structures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generic, TypeVar

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
