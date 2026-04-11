"""Test backend contracts and command planning."""

from __future__ import annotations

from ..config import TestRunnerConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, WorkflowPlan


def plan_tests(runners: list[TestRunnerConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured test runners."""

    specs: list[CommandSpec] = []
    for runner in runners:
        contract = _test_contract(runner.backend)
        contract.validate(runner)
        specs.extend(contract.plan(runner, None))
    return WorkflowPlan(specs=specs)


def runner_specs(config: TestRunnerConfig) -> list[CommandSpec]:
    """Build command specs for a configured test runner.

    Args:
        config: Parsed test runner configuration.

    Returns:
        Command specs for the full runner workflow, including hooks.
    """
    return plan_tests([config]).specs


def supported_test_backends() -> set[str]:
    """Return the registered test backend names."""

    return set(TEST_BACKENDS)


def validate_test_backend(config: TestRunnerConfig) -> None:
    """Validate a configured test backend through the registry contract."""

    _test_contract(config.backend).validate(config)


def _test_contract(backend: str) -> BackendContract[TestRunnerConfig, None]:
    """Resolve a registered test backend contract."""

    try:
        return TEST_BACKENDS[backend]
    except KeyError as exc:
        raise ConfigError(f"Unsupported test backend: {backend}") from exc


def _pytest_plan(config: TestRunnerConfig, _: None) -> list[CommandSpec]:
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
    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=command,
            env=config.env,
            description=f"pytest runner `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _tox_plan(config: TestRunnerConfig, _: None) -> list[CommandSpec]:
    """Build the tox command for a test runner.

    Args:
        config: Parsed tox runner configuration.

    Returns:
        Command spec for the tox invocation.
    """
    command = ["tox", "-e", config.tox_env or ""]
    command.extend(config.args)
    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=command, env=config.env, description=f"tox runner `{config.name}`"
        )
    ]
    specs.extend(post_hooks)
    return specs


def _ctest_plan(config: TestRunnerConfig, _: None) -> list[CommandSpec]:
    """Build the optional CMake and ctest commands for a native test runner.

    Args:
        config: Parsed ctest runner configuration.

    Returns:
        Command specs for optional configure and build steps followed by ctest.
    """
    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs: list[CommandSpec] = list(pre_hooks)
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
    specs.extend(post_hooks)
    return specs


def _validate_pytest(config: TestRunnerConfig) -> None:
    """Validate pytest runner configuration."""

    if not config.path:
        raise ConfigError(f"`test.runners.{config.name}.path` is required for pytest")


def _validate_tox(config: TestRunnerConfig) -> None:
    """Validate tox runner configuration."""

    if not config.tox_env:
        raise ConfigError(f"`test.runners.{config.name}.tox_env` is required for tox")


def _validate_ctest(config: TestRunnerConfig) -> None:
    """Validate ctest runner configuration."""

    if not config.build_dir:
        raise ConfigError(
            f"`test.runners.{config.name}.build_dir` is required for ctest"
        )


TEST_BACKENDS: dict[str, BackendContract[TestRunnerConfig, None]] = {
    "pytest": BackendContract(
        name="pytest",
        validate=_validate_pytest,
        plan=_pytest_plan,
    ),
    "tox": BackendContract(
        name="tox",
        validate=_validate_tox,
        plan=_tox_plan,
    ),
    "ctest": BackendContract(
        name="ctest",
        validate=_validate_ctest,
        plan=_ctest_plan,
    ),
}
