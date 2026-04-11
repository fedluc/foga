"""Tests for adapter command generation."""

from pathlib import Path

import pytest

from devkit import config as cfg
from devkit.adapters.build import build_specs
from devkit.adapters.deploy import deploy_specs
from devkit.adapters.testing import runner_specs
from devkit.errors import ConfigError


def test_build_specs_generate_cmake_and_python_commands() -> None:
    """Build specs include native and Python commands in order."""
    config = cfg.BuildConfig(
        native=cfg.NativeBuildConfig(
            backend="cmake",
            source_dir="src/native",
            build_dir="build/native",
            generator="Ninja",
            configure_args=["-DUSE_MPI=OFF"],
            build_args=["--verbose"],
            targets=["native_tests"],
            env={"CC": "clang"},
            hooks=cfg.HookConfig(pre=[["echo", "prep"]]),
        ),
        python=cfg.PythonBuildConfig(
            backend="python-build",
            args=["--wheel"],
        ),
    )

    specs = build_specs(config)

    assert specs[0].command == ["echo", "prep"]
    assert specs[1].command == [
        "cmake",
        "-S",
        "src/native",
        "-B",
        "build/native",
        "-G",
        "Ninja",
        "-DUSE_MPI=OFF",
    ]
    assert specs[2].command == [
        "cmake",
        "--build",
        "build/native",
        "--parallel",
        "--verbose",
        "--target",
        "native_tests",
    ]
    assert specs[3].command == ["python3", "-m", "build", "--wheel"]


def test_ctest_runner_can_prepare_target_before_running() -> None:
    """ctest runners can configure and build before executing tests."""
    runner = cfg.TestRunnerConfig(
        name="native",
        backend="ctest",
        source_dir="src/native",
        build_dir="build/native-tests",
        target="native_tests",
        configure_args=["-DBUILD_NATIVE_TESTS=ON"],
    )

    specs = runner_specs(runner)

    assert specs[0].command == [
        "cmake",
        "-S",
        "src/native",
        "-B",
        "build/native-tests",
        "-DBUILD_NATIVE_TESTS=ON",
    ]
    assert specs[1].command == [
        "cmake",
        "--build",
        "build/native-tests",
        "--parallel",
        "--target",
        "native_tests",
    ]
    assert specs[2].command == [
        "ctest",
        "--test-dir",
        "build/native-tests",
        "--output-on-failure",
    ]


def test_deploy_specs_resolve_matching_artifacts(tmp_path: Path) -> None:
    """Deploy specs include matched artifact paths for uploads."""
    dist = tmp_path / "dist"
    dist.mkdir()
    wheel = dist / "demo-0.1.0-py3-none-any.whl"
    wheel.write_text("artifact", encoding="utf-8")

    target = cfg.DeployTargetConfig(
        name="pypi",
        backend="twine",
        artifacts=["dist/*"],
        repository="testpypi",
    )

    specs = deploy_specs(tmp_path, target)

    assert specs[0].command == [
        "twine",
        "upload",
        "--repository",
        "testpypi",
        str(wheel),
    ]


def test_deploy_specs_fail_when_no_artifacts_found(tmp_path: Path) -> None:
    """Deploy spec generation fails when artifact globs match nothing."""
    target = cfg.DeployTargetConfig(
        name="pypi",
        backend="twine",
        artifacts=["dist/*"],
    )

    with pytest.raises(ConfigError):
        deploy_specs(tmp_path, target)
