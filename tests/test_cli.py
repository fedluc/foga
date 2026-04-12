"""Tests for CLI routing and user-visible output."""

from pathlib import Path

import yaml

from devkit import cli


def write_config(path: Path) -> Path:
    """Write a minimal valid devkit configuration for CLI tests."""
    config = path / "devkit.yml"
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
deploy:
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]
clean:
  paths: ["dist"]
""",
        encoding="utf-8",
    )
    return config


def test_validate_rejects_python_build_command_override(tmp_path: Path, capsys) -> None:
    """Validation rejects redundant python-build command overrides."""
    config = tmp_path / "devkit.yml"
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
    assert "Configuration valid" in captured.out


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
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      native:
        targets: ["profile-target"]
build:
  native:
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
            "native",
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
        "selection": "native",
        "active_kinds": ["native"],
        "selected_entries": ["native"],
        "effective_targets": {"native": ["cli-target"]},
    }
    assert document["effective_config"] == {
        "build": {
            "native": {
                "backend": "cmake",
                "source_dir": "cpp",
                "build_dir": "build",
                "targets": ["cli-target"],
            },
        }
    }


def test_inspect_build_full_outputs_resolved_config(tmp_path: Path, capsys) -> None:
    """Inspect build can opt into the full resolved config output."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      native:
        targets: ["profile-target"]
build:
  default: all
  native:
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
            "native",
            "--target",
            "cli-target",
        ]
    )

    captured = capsys.readouterr()
    document = yaml.safe_load(captured.out)
    assert exit_code == 0
    assert document["context"] == {
        "command": "build",
        "selection": "native",
        "active_kinds": ["native"],
        "selected_entries": ["native"],
        "effective_targets": {"native": ["cli-target"]},
    }
    assert document["resolved_config"]["build"]["native"]["targets"] == ["cli-target"]


def test_inspect_reports_selected_test_runners(tmp_path: Path, capsys) -> None:
    """Inspect test defaults to a concise summary and filtered config."""
    config = tmp_path / "devkit.yml"
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
    native-cpp:
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
        "active_kinds": ["python"],
        "selected_runners": ["integration"],
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
    assert (
        "`inspect build --target` can only be used with native builds" in captured.err
    )


def test_build_dry_run_routes_to_executor(tmp_path: Path, monkeypatch) -> None:
    """The build command forwards dry-run execution to the executor."""
    config = write_config(tmp_path)
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["count"] = len(specs)
        captured["dry_run"] = dry_run

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

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

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "--dry-run"])

    assert exit_code == 0
    assert captured == {"count": 1, "dry_run": True}


def test_build_cli_target_overrides_profile_and_base_targets(
    tmp_path: Path, monkeypatch
) -> None:
    """CLI target selection takes precedence over profile and base targets."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  mpi:
    build:
      native:
        targets: ["profile-target"]
build:
  native:
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

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

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
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
build:
  native:
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

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "python", "--dry-run"])

    assert exit_code == 0
    assert captured["commands"] == [["python3", "-m", "build"]]


def test_build_uses_default_selection_when_cli_selection_is_omitted(
    tmp_path: Path, monkeypatch
) -> None:
    """Build defaults apply when the CLI does not specify a selection."""
    config = tmp_path / "devkit.yml"
    config.write_text(
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

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "build", "--dry-run"])

    assert exit_code == 0
    assert captured["commands"] == [["python3", "-m", "build"]]


def test_test_selection_runs_only_selected_runner_kind(
    tmp_path: Path, monkeypatch
) -> None:
    """Explicit test selection narrows execution to matching runner kinds."""
    config = tmp_path / "devkit.yml"
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
    native-cpp:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "native", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == ["ctest runner `native-cpp`"]


def test_build_all_selection_runs_all_configured_workflows(
    tmp_path: Path, monkeypatch
) -> None:
    """The explicit all build selection includes every configured build kind."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
build:
  native:
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

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

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
    config = tmp_path / "devkit.yml"
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
    native-cpp:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == ["pytest runner `unit`"]


def test_test_all_selection_runs_all_configured_runner_kinds(
    tmp_path: Path, monkeypatch
) -> None:
    """The explicit all test selection includes python and native runners."""
    config = tmp_path / "devkit.yml"
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
    native-cpp:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

    exit_code = cli.main(["--config", str(config), "test", "all", "--dry-run"])

    assert exit_code == 0
    assert captured["descriptions"] == [
        "pytest runner `unit`",
        "ctest runner `native-cpp`",
    ]


def test_test_runner_filter_applies_after_kind_selection(
    tmp_path: Path, monkeypatch
) -> None:
    """Runner filtering only considers runners from the selected kind."""
    config = tmp_path / "devkit.yml"
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
    native-cpp:
      backend: ctest
      build_dir: build/tests
""",
        encoding="utf-8",
    )
    captured: dict[str, object] = {}

    def fake_run_specs(self, specs, dry_run=False):
        captured["descriptions"] = [spec.description for spec in specs]

    monkeypatch.setattr("devkit.executor.CommandExecutor.run_specs", fake_run_specs)

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


def test_validate_accepts_example_style_profile_overrides_without_backend(
    tmp_path: Path, capsys
) -> None:
    """Validation ignores profile-only build or test fragments without backend."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
profiles:
  default:
    build:
      native:
        env:
          OpenMP_ROOT: /opt/homebrew/opt/libomp
    test:
      runners:
        native-cpp:
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
    assert "Configuration valid" in captured.out


def test_build_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Build reports the default kind when it points to no configured workflow."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
build:
  default: native
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
    assert "No native build workflows configured" in captured.err


def test_test_uses_default_selection_error_when_default_kind_is_missing(
    tmp_path: Path, capsys
) -> None:
    """Test reports the default kind when it points to no configured workflow."""
    config = tmp_path / "devkit.yml"
    config.write_text(
        """
project:
  name: demo
build:
  python:
    backend: python-build
test:
  default: native
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
    assert "No native test workflows configured" in captured.err
