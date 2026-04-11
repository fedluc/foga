"""Tests for configuration loading and validation."""

from pathlib import Path

import pytest

from devkit.config import load_config
from devkit.errors import ConfigError


def write_config(path: Path, contents: str) -> Path:
    """Write configuration contents to a test-local devkit file."""
    config_path = path / "devkit.yml"
    config_path.write_text(contents, encoding="utf-8")
    return config_path


def test_load_config_applies_default_profile(tmp_path: Path) -> None:
    """Loading config applies the default profile when none is specified."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
profiles:
  default:
    build:
      native:
        configure_args: ["-DUSE_MPI=ON"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
build:
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    config = load_config(config_path)

    assert config.build.native is not None
    assert config.build.native.configure_args == ["-DUSE_MPI=ON"]


def test_load_config_validates_runner_fields(tmp_path: Path) -> None:
    """Loading config rejects incomplete backend-specific runner settings."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
test:
  runners:
    broken:
      backend: tox
""",
    )

    with pytest.raises(ConfigError):
        load_config(config_path)
