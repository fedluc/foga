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

    assert config.active_profile == "default"
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


def test_load_config_rejects_python_build_command_override(tmp_path: Path) -> None:
    """The python-build backend uses a fixed command and only accepts args."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    command: ["python3", "-m", "build"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "`build.python.command` is not supported for the `python-build` "
            "backend; use `args` to pass extra flags"
        ),
    ):
        load_config(config_path)


def test_load_config_parses_build_and_test_defaults(tmp_path: Path) -> None:
    """Workflow defaults are loaded for build and test selection."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  default: python
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build
test:
  default: native
  runners:
    unit:
      backend: pytest
      path: tests
    native-cpp:
      backend: ctest
      build_dir: build/tests
""",
    )

    config = load_config(config_path)

    assert config.build.default == "python"
    assert config.tests.default == "native"


def test_load_config_allows_build_default_for_missing_kind(tmp_path: Path) -> None:
    """Build defaults can point at a kind that is not currently configured."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  default: python
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    config = load_config(config_path)

    assert config.build.default == "python"


def test_load_config_allows_test_default_all_when_kind_is_missing(
    tmp_path: Path,
) -> None:
    """Test defaults can request all configured runners even if one kind is absent."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  default: all
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    config = load_config(config_path)

    assert config.tests.default == "all"


def test_load_config_ignores_unconfigured_build_and_test_sections(
    tmp_path: Path,
) -> None:
    """Sections without a backend are treated as not configured."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  default: all
  native:
    env:
      OpenMP_ROOT: /opt/homebrew/opt/libomp
  python:
    backend: python-build
test:
  runners:
    native-cpp:
      env:
        OpenMP_ROOT: /opt/homebrew/opt/libomp
    unit:
      backend: pytest
      path: tests
""",
    )

    config = load_config(config_path)

    assert config.build.available_kinds() == ["python"]
    assert list(config.tests.runners) == ["unit"]


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


def test_load_config_lists_supported_build_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown build backends report the registered backend names."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  native:
    backend: unknown
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported build backend: unknown. "
            "Supported backends: cmake, python-build"
        ),
    ):
        load_config(config_path)


def test_load_config_rejects_profile_mapping_shape_changes(tmp_path: Path) -> None:
    """Profile overrides must preserve mapping-shaped config sections."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
profiles:
  default:
    build:
      native: broken
build:
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    with pytest.raises(
        ConfigError,
        match="`profiles.default.build.native` must remain a mapping",
    ):
        load_config(config_path)


def test_load_config_rejects_profile_backend_changes(tmp_path: Path) -> None:
    """Profiles cannot swap the backend for an existing configured workflow."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
profiles:
  default:
    build:
      native:
        backend: python-build
build:
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    with pytest.raises(
        ConfigError,
        match="`profiles.default.build.native.backend` cannot change backend",
    ):
        load_config(config_path)
