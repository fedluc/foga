"""Test backend contracts and command planning."""

from __future__ import annotations

from ..config.constants import RUNNERS_KEY, TEST_SECTION
from ..config.models import TestRunnerConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, WorkflowPlan, require_backend_contract
from .kinds import TEST_CTEST, TEST_PYTEST, TEST_TOX


def plan_tests(runners: list[TestRunnerConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured test runners.

    Args:
        runners: Test runners selected for the current invocation.

    Returns:
        Prepared command specs for each selected test runner.
    """

    specs: list[CommandSpec] = []
    for runner in runners:
        contract = require_backend_contract(TEST_SECTION, runner.backend, TEST_BACKENDS)
        contract.validate(runner)
        specs.extend(contract.plan(runner, None))
    return WorkflowPlan(specs=specs)


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
    """Build the optional CMake and ctest commands for a C++ test runner.

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
    """Validate pytest runner configuration.

    Args:
        config: Parsed pytest runner configuration.

    Raises:
        ConfigError: If the pytest path is missing.
    """

    if not config.path:
        raise ConfigError(
            f"`{TEST_SECTION}.{RUNNERS_KEY}.{config.name}.path` is required for pytest"
        )


def _validate_tox(config: TestRunnerConfig) -> None:
    """Validate tox runner configuration.

    Args:
        config: Parsed tox runner configuration.

    Raises:
        ConfigError: If the tox environment is missing.
    """

    if not config.tox_env:
        raise ConfigError(
            f"`{TEST_SECTION}.{RUNNERS_KEY}.{config.name}.tox_env` is required for tox"
        )


def _validate_ctest(config: TestRunnerConfig) -> None:
    """Validate ctest runner configuration.

    Args:
        config: Parsed ctest runner configuration.

    Raises:
        ConfigError: If the ctest build directory is missing.
    """

    if not config.build_dir:
        raise ConfigError(
            f"`{TEST_SECTION}.{RUNNERS_KEY}.{config.name}.build_dir` "
            "is required for ctest"
        )


TEST_BACKENDS: dict[str, BackendContract[TestRunnerConfig, None]] = {
    TEST_PYTEST: BackendContract(
        name=TEST_PYTEST,
        validate=_validate_pytest,
        plan=_pytest_plan,
    ),
    TEST_TOX: BackendContract(
        name=TEST_TOX,
        validate=_validate_tox,
        plan=_tox_plan,
    ),
    TEST_CTEST: BackendContract(
        name=TEST_CTEST,
        validate=_validate_ctest,
        plan=_ctest_plan,
    ),
}
