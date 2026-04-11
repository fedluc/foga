"""Test adapter command generation."""

from __future__ import annotations

from ..config import TestRunnerConfig
from ..executor import CommandSpec


def runner_specs(config: TestRunnerConfig) -> list[CommandSpec]:
    """Build command specs for a configured test runner.

    Args:
        config: Parsed test runner configuration.

    Returns:
        Command specs for the full runner workflow, including hooks.
    """
    specs = [
        CommandSpec(command=command, description=f"{config.name} pre-hook")
        for command in config.hooks.pre
    ]
    specs.extend(_backend_specs(config))
    specs.extend(
        CommandSpec(command=command, description=f"{config.name} post-hook")
        for command in config.hooks.post
    )
    return specs


def _backend_specs(config: TestRunnerConfig) -> list[CommandSpec]:
    """Dispatch runner command generation based on backend type.

    Args:
        config: Parsed test runner configuration.

    Returns:
        Command specs for the selected backend.

    Raises:
        ValueError: If the backend is unsupported.
    """
    if config.backend == "pytest":
        return [_pytest_spec(config)]
    if config.backend == "tox":
        return [_tox_spec(config)]
    if config.backend == "ctest":
        return _ctest_specs(config)
    raise ValueError(f"Unsupported backend: {config.backend}")


def _pytest_spec(config: TestRunnerConfig) -> CommandSpec:
    """Build the pytest command for a test runner.

    Args:
        config: Parsed pytest runner configuration.

    Returns:
        Command spec for the pytest invocation.
    """
    command = ["pytest", config.path or "."]
    if config.marker:
        command.extend(["-m", config.marker])
    command.extend(config.args)
    return CommandSpec(
        command=command, env=config.env, description=f"pytest runner `{config.name}`"
    )


def _tox_spec(config: TestRunnerConfig) -> CommandSpec:
    """Build the tox command for a test runner.

    Args:
        config: Parsed tox runner configuration.

    Returns:
        Command spec for the tox invocation.
    """
    command = ["tox", "-e", config.tox_env or ""]
    command.extend(config.args)
    return CommandSpec(
        command=command, env=config.env, description=f"tox runner `{config.name}`"
    )


def _ctest_specs(config: TestRunnerConfig) -> list[CommandSpec]:
    """Build the optional CMake and ctest commands for a native test runner.

    Args:
        config: Parsed ctest runner configuration.

    Returns:
        Command specs for optional configure and build steps followed by ctest.
    """
    specs: list[CommandSpec] = []
    if config.source_dir:
        configure_command = [
            "cmake",
            "-S",
            config.source_dir,
            "-B",
            config.build_dir or "",
        ]
        if config.generator:
            configure_command.extend(["-G", config.generator])
        configure_command.extend(config.configure_args)
        specs.append(
            CommandSpec(
                command=configure_command,
                env=config.env,
                description=f"ctest configure `{config.name}`",
            )
        )
        build_command = ["cmake", "--build", config.build_dir or "", "--parallel"]
        build_command.extend(config.build_args)
        if config.target:
            build_command.extend(["--target", config.target])
        specs.append(
            CommandSpec(
                command=build_command,
                env=config.env,
                description=f"ctest build `{config.name}`",
            )
        )

    command = ["ctest", "--test-dir", config.build_dir or "", "--output-on-failure"]
    command.extend(config.args)
    specs.append(
        CommandSpec(
            command=command, env=config.env, description=f"ctest runner `{config.name}`"
        )
    )
    return specs
