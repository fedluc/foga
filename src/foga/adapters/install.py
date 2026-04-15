"""Install backend contracts and command planning."""

from __future__ import annotations

from functools import partial
from pathlib import Path

from ..config.constants import INSTALL_SECTION, TARGETS_KEY
from ..config.models import InstallTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import prepend_launcher, split_hooks
from .contracts import (
    BackendContract,
    ToolRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import (
    INSTALL_APT_GET,
    INSTALL_NPM,
    INSTALL_PIP,
    INSTALL_POETRY,
    INSTALL_UV,
    INSTALL_YUM,
)


def plan_install(
    project_root: Path, targets: list[InstallTargetConfig]
) -> WorkflowPlan:
    """Build a workflow plan for configured install targets.

    Args:
        project_root: Project root used as the command working directory.
        targets: Install targets selected for the current invocation.

    Returns:
        Planned command specs for all selected install targets.
    """

    specs: list[CommandSpec] = []
    request = ToolRequest(project_root=project_root)
    for target in targets:
        contract = require_backend_contract(
            INSTALL_SECTION, target.backend, INSTALL_BACKENDS
        )
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def _install_subjects(config: InstallTargetConfig) -> list[str]:
    """Return positional install subjects for backends that accept them.

    Args:
        config: Parsed install target configuration.

    Returns:
        Ordered positional install subjects built from configured packages and
        an optional local path.
    """

    subjects = list(config.packages)
    if config.path:
        subjects.append(config.path)
    return subjects


def _plan_install_command(
    config: InstallTargetConfig,
    request: ToolRequest,
    *,
    command_prefix: tuple[str, ...],
) -> list[CommandSpec]:
    """Build command specs for install backends with positional subjects.

    Args:
        config: Parsed install target configuration.
        request: Shared planning context with the project root.
        command_prefix: Base command inserted before backend args and subjects.

    Returns:
        Planned command specs for the target, including hooks.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    command = list(command_prefix)
    if config.editable:
        command.append("-e")
    command.extend(config.args)
    command.extend(_install_subjects(config))
    specs = pre_hooks + [
        CommandSpec(
            command=prepend_launcher(command, config.launcher),
            cwd=request.project_root,
            env=config.env,
            description=f"install target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _plan_poetry_install(
    config: InstallTargetConfig, request: ToolRequest
) -> list[CommandSpec]:
    """Build the poetry install command for an install target.

    Args:
        config: Parsed install target configuration.
        request: Shared planning context with the project root.

    Returns:
        Planned command specs for the target, including hooks.
    """

    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    specs = pre_hooks + [
        CommandSpec(
            command=prepend_launcher(
                ["poetry", "install", *config.args],
                config.launcher,
            ),
            cwd=request.project_root,
            env=config.env,
            description=f"install target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _require_subjects(config: InstallTargetConfig) -> None:
    """Validate that an install target defines packages or a local path.

    Args:
        config: Parsed install target configuration.

    Raises:
        ConfigError: If neither ``packages`` nor ``path`` is configured.
    """

    if _install_subjects(config):
        return
    raise ConfigError(
        f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}` must define at least one "
        "package in `packages` or a local `path`"
    )


def _validate_editable_path(config: InstallTargetConfig) -> None:
    """Validate that editable installs also define a local path.

    Args:
        config: Parsed install target configuration.

    Raises:
        ConfigError: If ``editable`` is enabled without a local path.
    """

    if not config.editable or config.path:
        return
    raise ConfigError(
        f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}.path` is required when "
        "`editable` is true"
    )


def _reject_path(config: InstallTargetConfig, backend: str) -> None:
    """Reject local paths for backends that do not support them.

    Args:
        config: Parsed install target configuration.
        backend: Backend name used in the validation error.

    Raises:
        ConfigError: If a local path is configured for an incompatible backend.
    """

    if config.path is None:
        return
    raise ConfigError(
        f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}.path` is not supported "
        f"for the `{backend}` backend"
    )


def _reject_editable(config: InstallTargetConfig, backend: str) -> None:
    """Reject editable mode for backends that do not support it.

    Args:
        config: Parsed install target configuration.
        backend: Backend name used in the validation error.

    Raises:
        ConfigError: If editable mode is configured for an incompatible backend.
    """

    if not config.editable:
        return
    raise ConfigError(
        f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}.editable` is not supported "
        f"for the `{backend}` backend"
    )


def _validate_pip_like(config: InstallTargetConfig) -> None:
    """Validate pip-style install targets.

    Args:
        config: Parsed install target configuration.

    Raises:
        ConfigError: If editable mode is invalid or no install subject is set.
    """

    _validate_editable_path(config)
    _require_subjects(config)


def _validate_poetry(config: InstallTargetConfig) -> None:
    """Validate poetry install targets.

    Args:
        config: Parsed install target configuration.

    Raises:
        ConfigError: If unsupported path, packages, or editable fields are set.
    """

    _reject_path(config, INSTALL_POETRY)
    _reject_editable(config, INSTALL_POETRY)
    if config.packages:
        raise ConfigError(
            f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}.packages` is not "
            f"supported for the `{INSTALL_POETRY}` backend"
        )


def _validate_npm(config: InstallTargetConfig) -> None:
    """Validate npm install targets.

    Args:
        config: Parsed install target configuration.

    Raises:
        ConfigError: If editable mode is configured for npm.
    """

    _reject_editable(config, INSTALL_NPM)


def _validate_system_packages(config: InstallTargetConfig, *, backend: str) -> None:
    """Validate package-manager targets that require explicit package names.

    Args:
        config: Parsed install target configuration.
        backend: Backend name used in validation errors.

    Raises:
        ConfigError: If unsupported fields are set or no packages are configured.
    """

    _reject_path(config, backend)
    _reject_editable(config, backend)
    if config.packages:
        return
    raise ConfigError(
        f"`{INSTALL_SECTION}.{TARGETS_KEY}.{config.name}.packages` must not be empty"
    )


INSTALL_BACKENDS: dict[str, BackendContract[InstallTargetConfig, ToolRequest]] = {
    INSTALL_PIP: BackendContract(
        name=INSTALL_PIP,
        validate=_validate_pip_like,
        plan=partial(
            _plan_install_command,
            command_prefix=("python3", "-m", "pip", "install"),
        ),
    ),
    INSTALL_UV: BackendContract(
        name=INSTALL_UV,
        validate=_validate_pip_like,
        plan=partial(
            _plan_install_command,
            command_prefix=("uv", "pip", "install"),
        ),
    ),
    INSTALL_POETRY: BackendContract(
        name=INSTALL_POETRY,
        validate=_validate_poetry,
        plan=_plan_poetry_install,
    ),
    INSTALL_NPM: BackendContract(
        name=INSTALL_NPM,
        validate=_validate_npm,
        plan=partial(
            _plan_install_command,
            command_prefix=("npm", "install"),
        ),
    ),
    INSTALL_APT_GET: BackendContract(
        name=INSTALL_APT_GET,
        validate=partial(_validate_system_packages, backend=INSTALL_APT_GET),
        plan=partial(
            _plan_install_command,
            command_prefix=(INSTALL_APT_GET, "install"),
        ),
    ),
    INSTALL_YUM: BackendContract(
        name=INSTALL_YUM,
        validate=partial(_validate_system_packages, backend=INSTALL_YUM),
        plan=partial(
            _plan_install_command,
            command_prefix=(INSTALL_YUM, "install"),
        ),
    ),
}
