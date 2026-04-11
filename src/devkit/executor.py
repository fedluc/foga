"""Command execution helpers used by CLI workflows."""

from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .errors import ExecutionError


@dataclass(frozen=True)
class CommandSpec:
    """A command invocation with optional execution metadata.

    Attributes:
        command: Command and arguments to execute.
        cwd: Optional working directory for the command.
        env: Environment variables layered on top of the process environment.
        description: Optional human-readable description for log output.
    """

    command: list[str]
    cwd: Path | None = None
    env: dict[str, str] = field(default_factory=dict)
    description: str | None = None


class CommandExecutor:
    """Run prepared command specs relative to a project root."""

    def __init__(self, project_root: Path):
        """Initialize the executor.

        Args:
            project_root: Default working directory for commands that do not
                define an explicit ``cwd``.
        """
        self.project_root = project_root

    def run_specs(self, specs: list[CommandSpec], dry_run: bool = False) -> None:
        """Execute each command spec in order.

        Args:
            specs: Command specifications to execute.
            dry_run: When ``True``, print commands without executing them.

        Raises:
            ExecutionError: If any command exits with a non-zero status.
        """
        for spec in specs:
            self.run(spec, dry_run=dry_run)

    def run(self, spec: CommandSpec, dry_run: bool = False) -> None:
        """Execute a single command spec or print it during dry runs.

        Args:
            spec: Command specification to execute.
            dry_run: When ``True``, print the command instead of executing it.

        Raises:
            ExecutionError: If the command exits with a non-zero status.
        """
        command_str = shlex.join(spec.command)
        prefix = "[dry-run]" if dry_run else "[run]"
        suffix = f" ({spec.description})" if spec.description else ""
        print(f"{prefix} {command_str}{suffix}")
        if dry_run:
            return

        env = os.environ.copy()
        env.update(spec.env)
        try:
            subprocess.run(
                spec.command,
                cwd=spec.cwd or self.project_root,
                env=env,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            raise ExecutionError(f"Command failed: {command_str}") from exc
