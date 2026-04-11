"""Deploy backend contracts and command planning."""

from __future__ import annotations

from pathlib import Path

from ..config import DeployTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import BackendContract, DeployRequest, WorkflowPlan


def plan_deploy(project_root: Path, targets: list[DeployTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured deploy targets."""

    specs: list[CommandSpec] = []
    request = DeployRequest(project_root=project_root)
    for target in targets:
        contract = _deploy_contract(target.backend)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


def deploy_specs(project_root: Path, config: DeployTargetConfig) -> list[CommandSpec]:
    """Build command specs for a deploy target.

    Args:
        project_root: Project root used to resolve artifact patterns.
        config: Parsed deploy target configuration.

    Returns:
        Command specs for the deploy workflow.
    """
    return plan_deploy(project_root, [config]).specs


def supported_deploy_backends() -> set[str]:
    """Return the registered deploy backend names."""

    return set(DEPLOY_BACKENDS)


def validate_deploy_backend(config: DeployTargetConfig) -> None:
    """Validate a configured deploy backend through the registry contract."""

    _deploy_contract(config.backend).validate(config)


def _deploy_contract(
    backend: str,
) -> BackendContract[DeployTargetConfig, DeployRequest]:
    """Resolve a registered deploy backend contract."""

    try:
        return DEPLOY_BACKENDS[backend]
    except KeyError as exc:
        raise ConfigError(f"Unsupported deploy backend: {backend}") from exc


def _twine_plan(
    config: DeployTargetConfig, request: DeployRequest
) -> list[CommandSpec]:
    """Build the twine upload command for a deploy target.

    Args:
        config: Parsed deploy target configuration.
        request: Deploy planning options.

    Returns:
        Upload command spec for the configured target.
    """
    pre_hooks, post_hooks = split_hooks(config.hooks, config.name)
    artifacts = _resolve_artifacts(request.project_root, config.artifacts)
    command = ["twine", "upload"]
    if config.repository:
        command.extend(["--repository", config.repository])
    if config.repository_url:
        command.extend(["--repository-url", config.repository_url])
    command.extend(config.args)
    command.extend(artifacts)
    specs = pre_hooks + [
        CommandSpec(
            command=command,
            env=config.env,
            description=f"deploy target `{config.name}`",
        )
    ]
    specs.extend(post_hooks)
    return specs


def _resolve_artifacts(project_root: Path, patterns: list[str]) -> list[str]:
    """Resolve artifact glob patterns to an ordered list of files.

    Args:
        project_root: Project root used to evaluate artifact glob patterns.
        patterns: Artifact glob patterns from configuration.

    Returns:
        Ordered list of resolved artifact file paths.

    Raises:
        ConfigError: If no files match the configured patterns.
    """
    artifacts: list[str] = []
    for pattern in patterns:
        matches = sorted(project_root.glob(pattern))
        artifacts.extend(str(match) for match in matches if match.is_file())
    if not artifacts:
        raise ConfigError("No artifacts matched the configured deploy patterns")
    return artifacts


def _validate_twine(config: DeployTargetConfig) -> None:
    """Validate Twine deploy target configuration."""

    if not config.artifacts:
        raise ConfigError(f"`deploy.targets.{config.name}.artifacts` must not be empty")


DEPLOY_BACKENDS: dict[str, BackendContract[DeployTargetConfig, DeployRequest]] = {
    "twine": BackendContract(
        name="twine",
        validate=_validate_twine,
        plan=_twine_plan,
    )
}
