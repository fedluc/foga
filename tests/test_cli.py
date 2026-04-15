"""Tests for CLI routing and user-visible output."""

from pathlib import Path

import yaml
from typer.testing import CliRunner

from foga import __version__, cli


def write_config(path: Path) -> Path:
    """Write a minimal valid foga configuration for CLI tests."""
    config = path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
install:
  targets:
    editable:
      backend: pip
      path: .
      editable: true
deploy:
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]
docs:
  targets:
    python-api:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html
format:
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]
lint:
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]
clean:
  paths: ["dist"]
""",
        encoding="utf-8",
    )
    return config


def test_validate_rejects_python_build_command_override(tmp_path: Path, capsys) -> None:
    """Validation rejects redundant python-build command overrides."""
    config = tmp_path / "foga.yml"
    config.write_text(
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
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert (
        "`build.python.command` is not supported for the `python-build` backend"
        in captured.err
    )


def test_validate_command_succeeds(tmp_path: Path, capsys) -> None:
    """The validate command reports success for a valid config."""
    config = write_config(tmp_path)

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Validation OK" in captured.out
    assert "project `demo` is ready to use" in captured.out
    assert "Build workflows" in captured.out
    assert "Test runners" in captured.out
    assert "Docs targets" in captured.out
    assert "Format targets" in captured.out
    assert "Lint targets" in captured.out
    assert "Install targets" in captured.out
    assert "Deploy targets" in captured.out
    assert "Clean paths" in captured.out


def test_root_version_option_reports_installed_version() -> None:
    """The root version option prints the installed package version."""
    runner = CliRunner()

    result = runner.invoke(cli.app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout == f"foga {__version__}\n"


def test_version_command_reports_installed_version() -> None:
    """The version subcommand prints the installed package version."""
    runner = CliRunner()

    result = runner.invoke(cli.app, ["version"])

    assert result.exit_code == 0
    assert result.stdout == f"foga {__version__}\n"


def test_validate_reports_yaml_syntax_errors_with_location(
    tmp_path: Path, capsys
) -> None:
    """Validate surfaces YAML syntax errors with file and location details."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
deploy: [
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Configuration error" in captured.err
    assert "invalid YAML syntax" in captured.err
    assert "File" in captured.err
    assert "Location" in captured.err
    assert "Hint" in captured.err


def test_validate_reports_precise_string_type_errors(tmp_path: Path, capsys) -> None:
    """Validate points to the full path when a string field has the wrong type."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: 42
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "`build.cpp.build_dir` must be a string" in captured.err


def test_inspect_outputs_resolved_config(tmp_path: Path, capsys) -> None:
    """Inspect prints the merged configuration document."""
    config = write_config(tmp_path)

    exit_code = cli.main(["--config", str(config), "inspect"])

    captured = capsys.readouterr()
    document = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert document["active_profile"] is None
    assert document["context"] == {"command": "inspect"}
    assert document["resolved_config"]["project"]["name"] == "demo"


def test_inspect_reports_active_profile_and_build_overrides(
    tmp_path: Path, capsys
) -> None:
    """Inspect build defaults to a concise summary and effective config."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      cpp:
        targets: ["profile-target"]
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
    targets: ["base-target"]
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "inspect",
            "--profile",
            "mpi",
            "build",
            "cpp",
            "--target",
            "cli-target",
        ]
    )

    captured = capsys.readouterr()
    document = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert document["active_profile"] == "mpi"
    assert document["summary"] == {
        "command": "build",
        "selection": "cpp",
        "targets": ["cli-target"],
    }
    assert document["effective_config"] == {
        "build": {
            "cpp": {
                "backend": "cmake",
                "source_dir": "cpp",
                "build_dir": "build",
                "targets": ["cli-target"],
            },
        }
    }


def test_inspect_build_full_outputs_resolved_config(tmp_path: Path, capsys) -> None:
    """Inspect build can opt into the full resolved config output."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      cpp:
        targets: ["profile-target"]
build:
  default: all
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
    targets: ["base-target"]
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "inspect",
            "--profile",
            "mpi",
            "build",
            "--full",
            "cpp",
            "--target",
            "cli-target",
        ]
    )

    captured = capsys.readouterr()
    document = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert document["context"] == {
        "command": "build",
        "selection": "cpp",
        "targets": ["cli-target"],
    }
    assert document["resolved_config"]["build"]["cpp"]["targets"] == ["cli-target"]


def test_inspect_reports_selected_test_runners(tmp_path: Path, capsys) -> None:
    """Inspect test defaults to a concise summary and filtered config."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
    integration:
      backend: tox
      tox_env: py311
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "inspect",
            "test",
            "python",
            "--runner",
            "integration",
        ]
    )

    captured = capsys.readouterr()
    document = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert document["summary"] == {
        "command": "test",
        "selection": "python",
        "runners": ["integration"],
    }
    assert document["effective_config"] == {
        "test": {
            "runners": {
                "integration": {
                    "backend": "tox",
                    "tox_env": "py311",
                }
            }
        }
    }


def test_inspect_build_rejects_target_override_for_python_selection(
    tmp_path: Path, capsys
) -> None:
    """Inspect mirrors build target validation for python-only selections."""
    config = write_config(tmp_path)

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "inspect",
            "build",
            "python",
            "--target",
            "wheel",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "`inspect build --target` can only be used with cpp builds" in captured.err


def test_build_dry_run_routes_to_executor(tmp_path: Path, monkeypatch) -> None:
    """The build command forwards dry-run execution to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_test_dry_run_routes_planned_specs_to_executor(
    tmp_path: Path, monkeypatch
) -> None:
    """The test command routes the workflow plan to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_format_dry_run_routes_planned_specs_to_executor(
    tmp_path: Path, monkeypatch
) -> None:
    """The format command routes the workflow plan to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "format", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_docs_dry_run_routes_planned_specs_to_executor(
    tmp_path: Path, monkeypatch
) -> None:
    """The docs command routes the workflow plan to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "docs", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_lint_dry_run_routes_planned_specs_to_executor(
    tmp_path: Path, monkeypatch
) -> None:
    """The lint command routes the workflow plan to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "lint", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_install_command_dry_run_outputs_planned_commands(
    tmp_path: Path, capsys
) -> None:
    """Install dry-run prints the planned commands for the selected targets."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
install:
  targets:
    editable:
      backend: pip
      path: .
      editable: true
    system:
      backend: apt-get
      launcher: ["sudo"]
      packages: ["cmake", "clang"]
      args: ["-y"]
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "install", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "python3 -m pip install -e ." in captured.out
    assert "sudo apt-get install -y cmake clang" in captured.out


def test_build_cli_target_overrides_profile_and_base_targets(
    tmp_path: Path, monkeypatch
) -> None:
    """CLI target selection takes precedence over profile and base targets."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      cpp:
        targets: ["profile-target"]
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
    targets: ["base-target"]
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["commands"] = [spec.command for spec in specs]
        captured["dry_run"] = dry_run

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "build",
            "--profile",
            "mpi",
            "--target",
            "cli-target",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert captured["dry_run"] is True
    assert captured["commands"] == [
        ["cmake", "-S", "cpp", "-B", "build"],
        ["cmake", "--build", "build", "--parallel", "--target", "cli-target"],
    ]


def test_build_selection_runs_only_selected_workflow_kind(
    tmp_path: Path, monkeypatch
) -> None:
    """Explicit build selection narrows execution to the requested kind."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["commands"] = [spec.command for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "python", "--dry-run"])

    assert exit_code == 0
    assert captured["commands"] == [["python3", "-m", "build"]]


def test_build_uses_default_selection_when_cli_selection_is_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    """Build defaults apply when the CLI does not specify a selection."""
    config = tmp_path / "foga.yml"
    config.write_text(
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
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["commands"] = [spec.command for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "--dry-run"])

    assert exit_code == 0
    assert captured["commands"] == [["python3", "-m", "build"]]


def test_test_selection_runs_only_selected_runner_kind(
    tmp_path: Path, monkeypatch
) -> None:
    """Explicit test selection narrows execution to matching runner kinds."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "cpp", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == ["ctest runner `cpp-tests`"]


def test_build_all_selection_runs_all_configured_workflows(
    tmp_path: Path, monkeypatch
) -> None:
    """The explicit all build selection includes every configured build kind."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "all", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == [
        "cmake configure",
        "cmake build",
        "python package build",
    ]


def test_test_uses_default_selection_when_cli_selection_is_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    """Test defaults apply when the CLI does not specify a selection."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  default: python
  runners:
    unit:
      backend: pytest
      path: tests
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == ["pytest runner `unit`"]


def test_test_all_selection_runs_all_configured_runner_kinds(
    tmp_path: Path, monkeypatch
) -> None:
    """The explicit all test selection includes python and cpp runners."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "all", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == [
        "pytest runner `unit`",
        "ctest runner `cpp-tests`",
    ]


def test_test_runner_filter_applies_after_kind_selection(
    tmp_path: Path, monkeypatch
) -> None:
    """Runner filtering only considers runners from the selected kind."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
    integration:
      backend: tox
      tox_env: py311
    cpp-tests:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "test",
            "python",
            "--runner",
            "integration",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert captured["descriptions"] == ["tox runner `integration`"]


def test_format_selection_and_target_filter_apply_together(
    tmp_path: Path, monkeypatch
) -> None:
    """Format filtering applies target selection after kind selection."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
format:
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]
    black-style:
      backend: black
      paths: ["src"]
    cpp-style:
      backend: clang-format
      paths: ["src/demo.cpp"]
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "format",
            "python",
            "--target",
            "black-style",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert captured["descriptions"] == ["black formatter `black-style`"]


def test_docs_target_filter_selects_named_docs_target(
    tmp_path: Path, monkeypatch
) -> None:
    """Docs target filtering only runs the selected docs target."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
docs:
  targets:
    python-api:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html
    cpp-api:
      backend: doxygen
      config_file: Doxyfile
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(
        [
            "--config",
            str(config),
            "docs",
            "--target",
            "cpp-api",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert captured["descriptions"] == ["docs target `cpp-api`"]


def test_lint_uses_default_selection_when_cli_selection_is_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    """Lint defaults apply when the CLI does not specify a selection."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
lint:
  default: cpp
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]
    cpp-style:
      backend: clang-tidy
      paths: ["src/demo.cpp"]
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("foga.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "lint", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == ["clang-tidy target `cpp-style`"]


def test_docs_reports_missing_workflows(tmp_path: Path, capsys) -> None:
    """Docs reports a clear error when no docs targets are configured."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "docs", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No docs workflows configured" in captured.err


def test_validate_accepts_example_style_profile_overrides_without_backend(
    tmp_path: Path, capsys
) -> None:
    """Validation ignores profile-only build or test fragments without backend."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  default:
    build:
      cpp:
        env:
          OpenMP_ROOT: /opt/homebrew/opt/libomp
    test:
      runners:
        cpp-tests:
          env:
            OpenMP_ROOT: /opt/homebrew/opt/libomp
build:
  default: all
  python:
    backend: python-build
test:
  default: all
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Validation OK" in captured.out


def test_build_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Build reports the default kind when it points to no configured workflow."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  default: cpp
  python:
    backend: python-build
test:
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "build", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No cpp build workflows configured" in captured.err


def test_test_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Test reports the default kind when it points to no configured workflow."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  default: cpp
  runners:
    unit:
      backend: pytest
      path: tests
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "test", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No cpp test workflows configured" in captured.err


def test_format_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Format reports the default kind when it points to no configured workflow."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
format:
  default: cpp
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "format", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No cpp format workflows configured" in captured.err


def test_lint_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Lint reports the default kind when it points to no configured workflow."""
    config = tmp_path / "foga.yml"
    config.write_text(
        """
project:
  name: demo
lint:
  default: cpp
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]
""",
        encoding="utf-8",
    )

    exit_code = cli.main(["--config", str(config), "lint", "--dry-run"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No cpp lint workflows configured" in captured.err


def test_help_text_describes_common_profile_target_runner_and_dry_run_options() -> None:
    """Help text explains the common workflow-oriented CLI options."""
    runner = CliRunner()

    root_result = runner.invoke(cli.app, ["--help"])
    build_result = runner.invoke(cli.app, ["build", "--help"])
    test_result = runner.invoke(cli.app, ["test", "--help"])
    version_result = runner.invoke(cli.app, ["version", "--help"])
    docs_result = runner.invoke(cli.app, ["docs", "--help"])
    format_result = runner.invoke(cli.app, ["format", "--help"])
    lint_result = runner.invoke(cli.app, ["lint", "--help"])
    deploy_result = runner.invoke(cli.app, ["deploy", "--help"])

    assert root_result.exit_code == 0
    assert build_result.exit_code == 0
    assert test_result.exit_code == 0
    assert version_result.exit_code == 0
    assert docs_result.exit_code == 0
    assert format_result.exit_code == 0
    assert lint_result.exit_code == 0
    assert deploy_result.exit_code == 0

    assert "Show the installed foga version and exit." in root_result.stdout
    assert "Apply a named configuration profile" in build_result.stdout
    assert "Show the planned build commands without executing" in build_result.stdout
    assert "them." in build_result.stdout
    assert "Run only the named test runner." in test_result.stdout
    assert "multiple runners." in test_result.stdout
    assert "Print the installed foga version." in version_result.stdout
    assert "Run only the named docs target." in docs_result.stdout
    assert "Run only the named format target." in format_result.stdout
    assert "Run only the named lint target." in lint_result.stdout
    assert "Run only the named deploy target." in deploy_result.stdout
    assert "multiple targets." in deploy_result.stdout
    assert "Path to the foga YAML configuration file to load." in root_result.stdout
    assert "[cpp|python|all]" in build_result.stdout
    assert "[cpp|python|all]" in format_result.stdout
    assert "[cpp|python|all]" in lint_result.stdout
    assert (
        "[cpp|python|all]"
        in runner.invoke(cli.app, ["inspect", "build", "--help"]).stdout
    )
