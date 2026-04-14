"""Deploy backend contracts and command planning."""

from __future__ import annotations

from pathlib import Path

from ..config.models import DeployTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec
from .common import split_hooks
from .contracts import (
    BackendContract,
    DeployRequest,
    WorkflowPlan,
    require_backend_contract,
)
from .kinds import DEPLOY_TWINE


def plan_deploy(project_root: Path, targets: list[DeployTargetConfig]) -> WorkflowPlan:
    """Build a workflow plan for configured deploy targets.

    Args:
        project_root: Project root used to resolve configured artifact globs.
        targets: Deploy targets selected for the current invocation.

    Returns:
        Prepared command specs for each selected deploy target.
    """

    specs: list[CommandSpec] = []
    request = DeployRequest(project_root=project_root)
    for target in targets:
        contract = require_backend_contract("deploy", target.backend, DEPLOY_BACKENDS)
        contract.validate(target)
        specs.extend(contract.plan(target, request))
    return WorkflowPlan(specs=specs)


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
        raise ConfigError(
            "No artifacts matched the configured deploy patterns",
            details={"Patterns": ", ".join(patterns)},
            hint=(
                "Build the package artifacts first or adjust "
                "`deploy.targets.*.artifacts`."
            ),
        )
    return artifacts


def _validate_twine(config: DeployTargetConfig) -> None:
    """Validate Twine deploy target configuration."""

    if not config.artifacts:
        raise ConfigError(f"`deploy.targets.{config.name}.artifacts` must not be empty")


DEPLOY_BACKENDS: dict[str, BackendContract[DeployTargetConfig, DeployRequest]] = {
    DEPLOY_TWINE: BackendContract(
        name=DEPLOY_TWINE,
        validate=_validate_twine,
        plan=_twine_plan,
    )
}
