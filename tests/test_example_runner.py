"""Tests for the repository example launcher."""

from __future__ import annotations

from pathlib import Path

from foga import example_runner


def test_resolve_example_supports_short_name_and_alias() -> None:
    assert example_runner.resolve_example("python-only").name == "python-only"
    assert example_runner.resolve_example("01-python-only").name == "python-only"


def test_build_docker_commands_use_example_metadata(monkeypatch) -> None:
    spec = example_runner.resolve_example("pybind11-hello")
    monkeypatch.setattr(example_runner, "require_tool", lambda name: f"/{name}")

    build_command = example_runner.build_docker_build_command(spec)
    run_command = example_runner.build_docker_run_command(spec, ["build", "cpp"])

    assert build_command[:4] == [
        "/docker",
        "build",
        "-f",
        str(example_runner.REPO_ROOT / spec.dockerfile),
    ]
    assert run_command == [
        "/docker",
        "run",
        "--rm",
        example_runner.docker_image_tag(spec),
        "build",
        "cpp",
    ]


def test_run_example_uses_docker_mode_by_default(monkeypatch) -> None:
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_run(spec: example_runner.ExampleSpec, args: tuple[str, ...]) -> None:
        calls.append((spec.name, args))

    monkeypatch.setattr(example_runner, "run_docker_example", fake_run)

    exit_code = example_runner.run_example("pybind11-hello", [])

    assert exit_code == 0
    assert calls == [("pybind11-hello", ())]


def test_run_example_can_use_host_mode(monkeypatch) -> None:
    calls: list[tuple[str, tuple[str, ...]]] = []

    def fake_run(spec: example_runner.ExampleSpec, args: tuple[str, ...]) -> None:
        calls.append((spec.name, args))

    monkeypatch.setattr(example_runner, "run_host_example", fake_run)

    exit_code = example_runner.run_example(
        "pybind11-profiles",
        ["inspect", "--profile", "release", "build", "cpp"],
        mode="host",
    )

    assert exit_code == 0
    assert calls == [
        (
            "pybind11-profiles",
            ("inspect", "--profile", "release", "build", "cpp"),
        )
    ]


def test_main_lists_examples_when_no_name_is_provided(capsys) -> None:
    exit_code = example_runner.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "python-only" in captured.out
    assert "pybind11-profiles" in captured.out
    assert "--mode docker|host" in captured.out


def test_root_launcher_exists() -> None:
    assert Path("/workspaces/foga/run-example.py").exists()
