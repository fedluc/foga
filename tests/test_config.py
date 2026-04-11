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


def test_load_config_accepts_generic_named_build_entries(tmp_path: Path) -> None:
    """Build config can use arbitrary section names with registered backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  wheelhouse:
    backend: python-build
    args: ["--wheel"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    config = load_config(config_path)

    assert "wheelhouse" in config.build.entries
    assert config.build.python is None


def test_load_config_rejects_build_section_backend_mismatch(tmp_path: Path) -> None:
    """Legacy build sections still validate against the backend contract."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  native:
    backend: python-build
""",
    )

    with pytest.raises(ConfigError, match="build.native.*native build backend"):
        load_config(config_path)


def test_load_config_validates_deploy_target_artifacts(tmp_path: Path) -> None:
    """Deploy target validation still runs through the backend registry."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
deploy:
  targets:
    pypi:
      backend: twine
      artifacts: []
""",
    )

    with pytest.raises(ConfigError, match="deploy.targets.pypi.artifacts"):
        load_config(config_path)
