"""Tests for configuration loading and validation."""

from pathlib import Path

import pytest

from foga.config.loading import load_config
from foga.errors import ConfigError


def write_config(path: Path, contents: str) -> Path:
    """Write configuration contents to a test-local foga file."""
    config_path = path / "foga.yml"
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
      cpp:
        configure_args: ["-DUSE_MPI=ON"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    config = load_config(config_path)

    assert config.build.cpp is not None
    assert config.build.cpp.configure_args == ["-DUSE_MPI=ON"]


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


def test_load_config_rejects_unknown_build_entry_names(tmp_path: Path) -> None:
    """Build config only accepts the cpp and python workflow entry names."""
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

    with pytest.raises(
        ConfigError,
        match="`build.wheelhouse` is not a supported build entry",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_test_keys(tmp_path: Path) -> None:
    """Test config only accepts the default and runners keys."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
test:
  adas:
    backend: pytest
    path: tests
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match="`test.adas` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_format_keys(tmp_path: Path) -> None:
    """Format config only accepts the default and targets keys."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
format:
  adas:
    backend: ruff-format
    paths: ["src"]
""",
    )

    with pytest.raises(
        ConfigError,
        match="`format.adas` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_lint_keys(tmp_path: Path) -> None:
    """Lint config only accepts the default and targets keys."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
lint:
  adas:
    backend: ruff-check
    paths: ["src"]
""",
    )

    with pytest.raises(
        ConfigError,
        match="`lint.adas` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_deploy_keys(tmp_path: Path) -> None:
    """Deploy config only accepts the targets key."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
deploy:
  adas:
    backend: twine
    artifacts: ["dist/*"]
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]
""",
    )

    with pytest.raises(
        ConfigError,
        match="`deploy.adas` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_install_keys(tmp_path: Path) -> None:
    """Install config only accepts the targets key."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
install:
  adas:
    backend: pip
    path: .
  targets:
    editable:
      backend: pip
      path: .
""",
    )

    with pytest.raises(
        ConfigError,
        match="`install.adas` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_docs_keys(tmp_path: Path) -> None:
    """Docs config only accepts the targets key."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
docs:
  adas:
    backend: sphinx
    source_dir: docs
    build_dir: docs/_build/html
""",
    )

    with pytest.raises(
        ConfigError,
        match="`docs.adas` is not a supported configuration key",
    ):
        load_config(config_path)


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


def test_load_config_parses_hook_command_arrays(tmp_path: Path) -> None:
    """Hook commands use direct command arrays."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    hooks:
      pre:
        - ["python3", "tools/prepare.py"]
      post:
        - ["python3", "tools/cleanup.py"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    config = load_config(config_path)

    assert config.build.python is not None
    assert config.build.python.hooks.pre == [["python3", "tools/prepare.py"]]
    assert config.build.python.hooks.post == [["python3", "tools/cleanup.py"]]


def test_load_config_parses_launcher_command_arrays(tmp_path: Path) -> None:
    """Launcher fields are loaded as direct command arrays."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
    launcher: ["uv", "run"]
  python:
    backend: python-build
    launcher: ["uv", "run"]
test:
  runners:
    unit:
      backend: tox
      tox_env: py312
      launcher: ["pipx", "run"]
docs:
  targets:
    api:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html
      launcher: ["uv", "run"]
format:
  targets:
    python-style:
      backend: ruff-format
      paths: ["src"]
      launcher: ["pipx", "run"]
lint:
  targets:
    python-style:
      backend: ruff-check
      paths: ["src"]
      launcher: ["pipx", "run"]
install:
  targets:
    editable:
      backend: pip
      path: .
      editable: true
      launcher: ["uv", "run"]
deploy:
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]
      launcher: ["uv", "run"]
""",
    )

    config = load_config(config_path)

    assert config.build.cpp is not None
    assert config.build.python is not None
    assert config.build.cpp.launcher == ["uv", "run"]
    assert config.build.python.launcher == ["uv", "run"]
    assert config.tests.runners["unit"].launcher == ["pipx", "run"]
    assert config.docs.targets["api"].launcher == ["uv", "run"]
    assert config.formatters.targets["python-style"].launcher == ["pipx", "run"]
    assert config.linters.targets["python-style"].launcher == ["pipx", "run"]
    assert config.install["editable"].launcher == ["uv", "run"]
    assert config.deploy["pypi"].launcher == ["uv", "run"]


def test_load_config_rejects_shell_string_launchers(tmp_path: Path) -> None:
    """Launcher fields must use command arrays instead of shell strings."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    launcher: uv run
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match="`build.python.launcher` must be a non-empty list of strings",
    ):
        load_config(config_path)


def test_load_config_rejects_empty_launcher_arrays(tmp_path: Path) -> None:
    """Launcher fields reject empty command arrays."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
test:
  runners:
    unit:
      backend: pytest
      path: tests
      launcher: []
""",
    )

    with pytest.raises(
        ConfigError,
        match="`test.runners.unit.launcher` must be a non-empty list of strings",
    ):
        load_config(config_path)


def test_load_config_rejects_shell_string_hook_commands(tmp_path: Path) -> None:
    """Hook commands must use command arrays instead of shell strings."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    hooks:
      pre:
        - python3 tools/prepare.py
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match="`build.python.hooks.pre\\[0\\]` must be a non-empty list of strings",
    ):
        load_config(config_path)


def test_load_config_rejects_unknown_hook_keys(tmp_path: Path) -> None:
    """Hook config only accepts explicit pre and post command lists."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    hooks:
      before:
        - ["python3", "tools/prepare.py"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match="`build.python.hooks.before` is not a supported configuration key",
    ):
        load_config(config_path)


def test_load_config_rejects_hook_entry_mappings(tmp_path: Path) -> None:
    """Hook entries do not accept structured per-command mappings."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: python-build
    hooks:
      pre:
        - argv: ["python3", "tools/prepare.py"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match="`build.python.hooks.pre\\[0\\]` must be a non-empty list of strings",
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
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build
test:
  default: cpp
  runners:
    unit:
      backend: pytest
      path: tests
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
    )

    config = load_config(config_path)

    assert config.build.default == "python"
    assert config.tests.default == "cpp"


def test_load_config_allows_build_default_for_missing_kind(tmp_path: Path) -> None:
    """Build defaults can point at a kind that is not currently configured."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  default: python
  cpp:
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
  cpp:
    env:
      OpenMP_ROOT: /opt/homebrew/opt/libomp
  python:
    backend: python-build
test:
  runners:
    cpp-tests:
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
  cpp:
    backend: python-build
""",
    )

    with pytest.raises(
        ConfigError,
        match=("Unsupported build backend: python-build. Supported backends: cmake"),
    ):
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


def test_load_config_validates_install_target_requirements(tmp_path: Path) -> None:
    """Install target validation runs through the backend registry."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
install:
  targets:
    editable:
      backend: pip
      editable: true
""",
    )

    with pytest.raises(
        ConfigError,
        match="`install.targets.editable.path` is required when `editable` is true",
    ):
        load_config(config_path)


def test_load_config_lists_supported_build_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown cpp build backends only list cpp-compatible backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  cpp:
    backend: unknown
""",
    )

    with pytest.raises(
        ConfigError,
        match=("Unsupported build backend: unknown. Supported backends: cmake"),
    ):
        load_config(config_path)


def test_load_config_lists_supported_python_build_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown python build backends only list Python-compatible backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
build:
  python:
    backend: unknown
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
    )

    with pytest.raises(
        ConfigError,
        match=("Unsupported build backend: unknown. Supported backends: python-build"),
    ):
        load_config(config_path)


def test_load_config_lists_supported_test_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown test backends list the registered test backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
test:
  runners:
    unit:
      backend: unknown
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported test backend: unknown. Supported backends: ctest, pytest, tox"
        ),
    ):
        load_config(config_path)


def test_load_config_lists_supported_format_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown format backends list the registered format backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
format:
  targets:
    python-style:
      backend: unknown
      paths: ["src"]
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported format backend: unknown. Supported backends: black, "
            "clang-format, ruff-format"
        ),
    ):
        load_config(config_path)


def test_load_config_lists_supported_lint_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown lint backends list the registered lint backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
lint:
  targets:
    python-style:
      backend: unknown
      paths: ["src"]
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported lint backend: unknown. Supported backends: clang-tidy, "
            "pylint, ruff-check"
        ),
    ):
        load_config(config_path)


def test_load_config_lists_supported_deploy_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown deploy backends list the registered deploy backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
deploy:
  targets:
    pypi:
      backend: unknown
      artifacts: ["dist/*"]
""",
    )

    with pytest.raises(
        ConfigError,
        match=("Unsupported deploy backend: unknown. Supported backends: twine"),
    ):
        load_config(config_path)


def test_load_config_lists_supported_install_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown install backends list the registered install backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
install:
  targets:
    editable:
      backend: unknown
      path: .
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported install backend: unknown. Supported backends: apt-get, "
            "brew, npm, pip, poetry, uv, yum"
        ),
    ):
        load_config(config_path)


def test_load_config_lists_supported_docs_backends_for_unknown_backend(
    tmp_path: Path,
) -> None:
    """Unknown docs backends list the registered docs backends."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
docs:
  targets:
    api:
      backend: unknown
      source_dir: docs
      build_dir: docs/_build/html
""",
    )

    with pytest.raises(
        ConfigError,
        match=(
            "Unsupported docs backend: unknown. Supported backends: doxygen, "
            "mkdocs, sphinx"
        ),
    ):
        load_config(config_path)


def test_load_config_validates_docs_backend_fields(tmp_path: Path) -> None:
    """Docs targets still validate backend-specific required fields."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
docs:
  targets:
    api:
      backend: sphinx
      source_dir: docs
""",
    )

    with pytest.raises(
        ConfigError,
        match="`docs.targets.api.build_dir` is required",
    ):
        load_config(config_path)


def test_load_config_parses_docs_targets(tmp_path: Path) -> None:
    """Docs targets are loaded into the parsed config."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
docs:
  targets:
    python-api:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html
      builder: dirhtml
    site:
      backend: mkdocs
      config_file: mkdocs.yml
      build_dir: site
""",
    )

    config = load_config(config_path)

    assert list(config.docs.targets) == ["python-api", "site"]
    assert config.docs.targets["python-api"].builder == "dirhtml"
    assert config.docs.targets["site"].config_file == "mkdocs.yml"


def test_load_config_parses_install_targets(tmp_path: Path) -> None:
    """Install targets are loaded into the parsed config."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
install:
  targets:
    editable:
      backend: pip
      path: .
      editable: true
    python-deps:
      backend: poetry
      args: ["--sync"]
""",
    )

    config = load_config(config_path)

    assert list(config.install) == ["editable", "python-deps"]
    assert config.install["editable"].editable is True
    assert config.install["python-deps"].args == ["--sync"]


def test_load_config_parses_brew_install_targets(tmp_path: Path) -> None:
    """Brew install targets are loaded into the parsed config."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
install:
  targets:
    macos-deps:
      backend: brew
      packages: ["cmake", "llvm"]
""",
    )

    config = load_config(config_path)

    assert list(config.install) == ["macos-deps"]
    assert config.install["macos-deps"].packages == ["cmake", "llvm"]


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
      cpp: broken
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    with pytest.raises(
        ConfigError,
        match="`profiles.default.build.cpp` must remain a mapping",
    ):
        load_config(config_path)


def test_load_config_parses_format_and_lint_defaults(tmp_path: Path) -> None:
    """Workflow defaults are loaded for format and lint selection."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
format:
  default: python
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]
    cpp-style:
      backend: clang-format
      paths: ["src/demo.cpp"]
lint:
  default: cpp
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]
    python-static:
      backend: pylint
      paths: ["src"]
    cpp-style:
      backend: clang-tidy
      paths: ["src/demo.cpp"]
""",
    )

    config = load_config(config_path)

    assert config.formatters.default == "python"
    assert config.linters.default == "cpp"
    assert config.linters.targets["python-static"].backend == "pylint"


def test_load_config_validates_format_and_lint_paths(tmp_path: Path) -> None:
    """Format and lint targets require at least one configured path."""
    config_path = write_config(
        tmp_path,
        """
project:
  name: demo
format:
  targets:
    python-style:
      backend: ruff-format
lint:
  targets:
    python-style:
      backend: ruff-check
      paths: ["src"]
""",
    )

    with pytest.raises(
        ConfigError,
        match="`format.targets.python-style.paths` must not be empty",
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
      cpp:
        backend: python-build
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
""",
    )

    with pytest.raises(
        ConfigError,
        match="`profiles.default.build.cpp.backend` cannot change backend",
    ):
        load_config(config_path)
