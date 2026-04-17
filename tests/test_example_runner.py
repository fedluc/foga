"""Tests for the repository example launcher."""

from __future__ import annotations

from pathlib import Path

from foga import example_runner


def test_resolve_example_supports_short_name_and_alias() -> None:
    assert example_runner.resolve_example("python-only").name == "python-only"
    assert example_runner.resolve_example("01-python-only").name == "python-only"


def test_build_commands_use_example_metadata(monkeypatch) -> None:
    spec = example_runner.resolve_example("pybind11-hello")
    monkeypatch.setattr(example_runner, "require_tool", lambda name: f"/{name}")

    host_command = example_runner.build_host_command(spec, ["--list-steps"])
    build_command = example_runner.build_docker_build_command(spec)
    run_command = example_runner.build_docker_run_command(spec, ["build-cpp"])

    assert host_command == [
        "/uv",
        "run",
        "--project",
        str(example_runner.example_root(spec)),
        "python",
        str(example_runner.driver_path(spec)),
        "--list-steps",
    ]
    assert build_command[:4] == [
        "/docker",
        "build",
        "-f",
        str(example_runner.REPO_ROOT / spec.dockerfile),
    ]
    assert build_command[-1] == str(example_runner.example_root(spec))
    assert run_command == [
        "/docker",
        "run",
        "--rm",
        example_runner.docker_image_tag(spec),
        "python",
        spec.driver_script,
        "build-cpp",
    ]


def test_run_docker_example_runs_driver_once(monkeypatch) -> None:
    spec = example_runner.resolve_example("python-only")
    calls: list[tuple[tuple[str, ...], Path]] = []

    monkeypatch.setattr(
        example_runner,
        "build_docker_build_command",
        lambda spec: ["docker", "build", spec.name],
    )
    monkeypatch.setattr(
        example_runner,
        "build_docker_run_command",
        lambda spec, args: ["docker", "run", spec.name, *args],
    )

    def fake_run(command: list[str], *, cwd: Path) -> None:
        calls.append((tuple(command), cwd))

    monkeypatch.setattr(example_runner, "run_command", fake_run)

    example_runner.run_docker_example(spec, ("validate",))

    assert calls == [
        (("docker", "build", "python-only"), example_runner.REPO_ROOT),
        (("docker", "run", "python-only", "validate"), example_runner.REPO_ROOT),
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
        ["build-release", "test-release"],
        mode="host",
    )

    assert exit_code == 0
    assert calls == [("pybind11-profiles", ("build-release", "test-release"))]


def test_main_lists_examples_when_no_name_is_provided(capsys) -> None:
    exit_code = example_runner.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "python-only" in captured.out
    assert "pybind11-profiles" in captured.out
    assert "[step ...]" in captured.out


def test_example_driver_scripts_exist() -> None:
    for spec in example_runner.EXAMPLES:
        assert example_runner.driver_path(spec).exists()


def test_root_launcher_exists() -> None:
    assert Path("/workspaces/foga/run-example.py").exists()
