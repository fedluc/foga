"""Tests for command execution logging and failures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from foga.errors import ExecutionError
from foga.executor import CommandExecutor, CommandSpec


def test_run_dry_run_prints_structured_command_output(tmp_path: Path, capsys) -> None:
    """Dry-run output includes the execution mode and step description."""
    executor = CommandExecutor(tmp_path)

    executor.run(
        CommandSpec(["pytest", "tests"], description="pytest runner `unit`"),
        dry_run=True,
    )

    captured = capsys.readouterr()
    assert "[foga]" in captured.out
    assert "DRY-RUN" in captured.out
    assert "pytest tests" in captured.out
    assert "Step" in captured.out
    assert "pytest runner `unit`" in captured.out


def test_run_reports_actionable_failure_details(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Execution failures include the command, step, and working directory."""
    executor = CommandExecutor(tmp_path)

    def fake_run(*args, **kwargs) -> None:
        raise subprocess.CalledProcessError(returncode=23, cmd=["pytest", "tests"])

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ExecutionError) as exc_info:
        executor.run(
            CommandSpec(["pytest", "tests"], description="pytest runner `unit`")
        )

    error = exc_info.value
    assert error.message == "command exited with status 23"
    assert error.details == {
        "Command": "pytest tests",
        "Step": "pytest runner `unit`",
        "Working directory": str(tmp_path),
    }
