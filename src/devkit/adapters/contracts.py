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
    """Options used when planning build backend commands."""

    targets: list[str] | None = None


@dataclass(frozen=True)
class DeployRequest:
    """Options used when planning deploy backend commands."""

    project_root: Path


@dataclass(frozen=True)
class WorkflowPlan:
    """Prepared command specs for a CLI workflow."""

    specs: list[CommandSpec]


@dataclass(frozen=True)
class BackendContract(Generic[ConfigT, ContextT]):
    """Stable internal contract for backend validation and planning."""

    name: str
    validate: Callable[[ConfigT], None]
    plan: Callable[[ConfigT, ContextT], list[CommandSpec]]
