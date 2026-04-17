"""Validation coverage for repository example configurations."""

from __future__ import annotations

from pathlib import Path

import pytest

from foga import cli

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIGS = [
    ROOT / "examples/tutorial/01-python-only/foga.yml",
    ROOT / "examples/tutorial/02-pybind11-hello/foga.yml",
    ROOT / "examples/tutorial/03-pybind11-tests/foga.yml",
    ROOT / "examples/tutorial/04-pybind11-profiles/foga.yml",
    ROOT / "examples/qupled/foga.yml",
    ROOT / "examples/pybind11/foga.yml",
]


@pytest.mark.parametrize(
    "config_path",
    EXAMPLE_CONFIGS,
    ids=lambda path: path.parent.name,
)
def test_example_configs_validate(
    config_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every checked-in example configuration should validate successfully."""
    exit_code = cli.main(["--config", str(config_path), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Validation OK" in captured.out
