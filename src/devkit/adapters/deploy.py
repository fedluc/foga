"""Deployment adapter command generation."""

from __future__ import annotations

from pathlib import Path

from ..config import DeployTargetConfig
from ..errors import ConfigError
from ..executor import CommandSpec


def deploy_specs(project_root: Path, config: DeployTargetConfig) -> list[CommandSpec]:
    """Build command specs for a deploy target.

    Args:
        project_root: Project root used to resolve artifact patterns.
        config: Parsed deploy target configuration.

    Returns:
        Command specs for the deploy workflow.
    """
    specs = [
        CommandSpec(command=command, description=f"{config.name} pre-hook")
        for command in config.hooks.pre
    ]
    specs.append(_twine_spec(project_root, config))
    specs.extend(
        CommandSpec(command=command, description=f"{config.name} post-hook")
        for command in config.hooks.post
    )
    return specs


def _twine_spec(project_root: Path, config: DeployTargetConfig) -> CommandSpec:
    """Build the twine upload command for a deploy target.

    Args:
        project_root: Project root used to resolve artifact patterns.
        config: Parsed deploy target configuration.

    Returns:
        Upload command spec for the configured target.
    """
    artifacts = _resolve_artifacts(project_root, config.artifacts)
    command = ["twine", "upload"]
    if config.repository:
        command.extend(["--repository", config.repository])
    if config.repository_url:
        command.extend(["--repository-url", config.repository_url])
    command.extend(config.args)
    command.extend(artifacts)
    return CommandSpec(
        command=command, env=config.env, description=f"deploy target `{config.name}`"
    )


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
