"""Tests for adapter command generation."""

from pathlib import Path

import pytest

from foga.adapters.build import plan_build
from foga.adapters.deploy import plan_deploy
from foga.adapters.formatting import plan_format
from foga.adapters.linting import plan_lint
from foga.adapters.testing import plan_tests
from foga.config.models import (
    BuildConfig,
    CppBuildConfig,
    DeployTargetConfig,
    FormatTargetConfig,
    HookConfig,
    LintTargetConfig,
    PythonBuildConfig,
    TestRunnerConfig,
)
from foga.errors import ConfigError


def test_plan_build_generates_cmake_and_python_commands() -> None:
    """Build planning includes cpp and Python commands in order."""
    config = BuildConfig(
        cpp=CppBuildConfig(
            backend="cmake",
            source_dir="src/cpp",
            build_dir="build/cpp",
            generator="Ninja",
            configure_args=["-DUSE_MPI=OFF"],
            build_args=["--verbose"],
            targets=["cpp_tests"],
            env={"CC": "clang"},
            hooks=HookConfig(pre=[["echo", "prep"]]),
        ),
        python=PythonBuildConfig(
            backend="python-build",
            args=["--wheel"],
        ),
    )

    specs = plan_build(config).specs

    assert specs[0].command == ["echo", "prep"]
    assert specs[1].command == [
        "cmake",
        "-S",
        "src/cpp",
        "-B",
        "build/cpp",
        "-G",
        "Ninja",
        "-DUSE_MPI=OFF",
    ]
    assert specs[2].command == [
        "cmake",
        "--build",
        "build/cpp",
        "--parallel",
        "--verbose",
        "--target",
        "cpp_tests",
    ]
    assert specs[3].command == ["python3", "-m", "build", "--wheel"]


def test_plan_build_returns_registered_backend_specs_in_order() -> None:
    """Build planning uses the registered backend contracts in config order."""
    config = BuildConfig(
        cpp=CppBuildConfig(
            backend="cmake",
            source_dir="src/cpp",
            build_dir="build/cpp",
        ),
        python=PythonBuildConfig(
            backend="python-build",
            args=["--wheel"],
        ),
    )

    plan = plan_build(config, targets=["cpp_tests"])

    assert [spec.description for spec in plan.specs] == [
        "cmake configure",
        "cmake build target `cpp_tests`",
        "python package build",
    ]


def test_plan_build_can_select_only_python_backends() -> None:
    """Build planning can narrow execution to Python workflows."""
    config = BuildConfig(
        entries={
            "cpp": CppBuildConfig(
                backend="cmake",
                source_dir="src/cpp",
                build_dir="build/cpp",
            ),
            "wheel": PythonBuildConfig(
                backend="python-build",
                args=["--wheel"],
            ),
        }
    )

    plan = plan_build(config, selection="python")

    assert [spec.description for spec in plan.specs] == ["python package build"]


def test_plan_tests_ctest_runner_can_prepare_target_before_running() -> None:
    """ctest runners can configure and build before executing tests."""
    runner = TestRunnerConfig(
        name="cpp",
        backend="ctest",
        source_dir="src/cpp",
        build_dir="build/cpp-tests",
        target="cpp_tests",
        configure_args=["-DBUILD_CPP_TESTS=ON"],
    )

    specs = plan_tests([runner]).specs

    assert specs[0].command == [
        "cmake",
        "-S",
        "src/cpp",
        "-B",
        "build/cpp-tests",
        "-DBUILD_CPP_TESTS=ON",
    ]
    assert specs[1].command == [
        "cmake",
        "--build",
        "build/cpp-tests",
        "--parallel",
        "--target",
        "cpp_tests",
    ]
    assert specs[2].command == [
        "ctest",
        "--test-dir",
        "build/cpp-tests",
        "--output-on-failure",
    ]


def test_plan_deploy_resolves_matching_artifacts(tmp_path: Path) -> None:
    """Deploy planning includes matched artifact paths for uploads."""
    dist = tmp_path / "dist"
    dist.mkdir()
    wheel = dist / "demo-0.1.0-py3-none-any.whl"
    wheel.write_text("artifact", encoding="utf-8")

    target = DeployTargetConfig(
        name="pypi",
        backend="twine",
        artifacts=["dist/*"],
        repository="testpypi",
    )

    specs = plan_deploy(tmp_path, [target]).specs

    assert specs[0].command == [
        "twine",
        "upload",
        "--repository",
        "testpypi",
        str(wheel),
    ]


def test_plan_tests_combines_selected_runner_contracts() -> None:
    """Test planning combines multiple registered runner backends."""
    runners = [
        TestRunnerConfig(name="unit", backend="pytest", path="tests/unit"),
        TestRunnerConfig(name="integration", backend="tox", tox_env="py311"),
    ]

    plan = plan_tests(runners)

    assert [spec.command for spec in plan.specs] == [
        ["pytest", "tests/unit"],
        ["tox", "-e", "py311"],
    ]


def test_plan_format_builds_registered_formatter_commands(tmp_path: Path) -> None:
    """Format planning includes hooks and backend-specific commands."""
    targets = [
        FormatTargetConfig(
            name="python-style",
            backend="ruff-format",
            paths=["src", "tests"],
            hooks=HookConfig(pre=[["echo", "prep"]]),
        ),
        FormatTargetConfig(
            name="cpp-style",
            backend="clang-format",
            paths=["src/demo.cpp"],
            args=["--style=file"],
        ),
    ]

    plan = plan_format(tmp_path, targets)

    assert [spec.command for spec in plan.specs] == [
        ["echo", "prep"],
        ["ruff", "format", "src", "tests"],
        ["clang-format", "-i", "--style=file", "src/demo.cpp"],
    ]


def test_plan_lint_builds_registered_linter_commands(tmp_path: Path) -> None:
    """Lint planning includes backend-specific commands in order."""
    targets = [
        LintTargetConfig(
            name="python-style",
            backend="ruff-check",
            paths=["src", "tests"],
        ),
        LintTargetConfig(
            name="cpp-style",
            backend="clang-tidy",
            paths=["src/demo.cpp"],
            args=["-p", "build"],
        ),
    ]

    plan = plan_lint(tmp_path, targets)

    assert [spec.command for spec in plan.specs] == [
        ["ruff", "check", "src", "tests"],
        ["clang-tidy", "-p", "build", "src/demo.cpp"],
    ]


def test_plan_deploy_fails_when_no_artifacts_found(tmp_path: Path) -> None:
    """Deploy planning fails when artifact globs match nothing."""
    target = DeployTargetConfig(
        name="pypi",
        backend="twine",
        artifacts=["dist/*"],
    )

    with pytest.raises(ConfigError):
        plan_deploy(tmp_path, [target])


def test_plan_deploy_combines_multiple_targets(tmp_path: Path) -> None:
    """Deploy planning combines registered backend specs for each target."""
    dist = tmp_path / "dist"
    dist.mkdir()
    first = dist / "demo-0.1.0-py3-none-any.whl"
    second = dist / "demo-0.1.0.tar.gz"
    first.write_text("wheel", encoding="utf-8")
    second.write_text("sdist", encoding="utf-8")

    targets = [
        DeployTargetConfig(
            name="testpypi",
            backend="twine",
            artifacts=["dist/*.whl"],
            repository="testpypi",
        ),
        DeployTargetConfig(
            name="release",
            backend="twine",
            artifacts=["dist/*.tar.gz"],
        ),
    ]

    plan = plan_deploy(tmp_path, targets)

    assert [spec.command for spec in plan.specs] == [
        ["twine", "upload", "--repository", "testpypi", str(first)],
        ["twine", "upload", str(second)],
    ]
