"""Tests for CLI routing and user-visible output."""

from pathlib import Path

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


def test_validate_command_succeeds(tmp_path: Path, capsys) -> None:
    """The validate command reports success for a valid config."""
    config = write_config(tmp_path)

    exit_code = cli.main(["--config", str(config), "validate"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Configuration valid" in captured.out


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
