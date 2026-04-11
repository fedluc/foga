"""Build adapter command generation."""

from __future__ import annotations

from ..config import BuildConfig, NativeBuildConfig
from ..executor import CommandSpec


def build_specs(
    config: BuildConfig, targets: list[str] | None = None
) -> list[CommandSpec]:
    """Build the command sequence for configured build workflows."""
    specs: list[CommandSpec] = []
    if config.native is not None:
        specs.extend(_hook_specs(config.native.hooks.pre, "native pre-hook"))
        specs.extend(_cmake_specs(config.native, targets))
        specs.extend(_hook_specs(config.native.hooks.post, "native post-hook"))
    if config.python is not None:
        specs.extend(_hook_specs(config.python.hooks.pre, "python build pre-hook"))
        specs.append(
            CommandSpec(
                command=config.python.command + config.python.args,
                env=config.python.env,
                description="python package build",
            )
        )
        specs.extend(_hook_specs(config.python.hooks.post, "python build post-hook"))
    return specs


def _cmake_specs(
    config: NativeBuildConfig, targets: list[str] | None
) -> list[CommandSpec]:
    """Build CMake configure and build commands for a native workflow."""
    command = [
        "cmake",
        "-S",
        config.source_dir,
        "-B",
        config.build_dir,
    ]
    if config.generator:
        command.extend(["-G", config.generator])
    command.extend(config.configure_args)

    specs = [
        CommandSpec(command=command, env=config.env, description="cmake configure")
    ]

    active_targets = targets if targets else config.targets
    build_command = [
        "cmake",
        "--build",
        config.build_dir,
        "--parallel",
    ]
    build_command.extend(config.build_args)
    if active_targets:
        for target in active_targets:
            specs.append(
                CommandSpec(
                    command=build_command + ["--target", target],
                    env=config.env,
                    description=f"cmake build target `{target}`",
                )
            )
    else:
        specs.append(
            CommandSpec(
                command=build_command, env=config.env, description="cmake build"
            )
        )
    return specs


def _hook_specs(commands: list[list[str]], description: str) -> list[CommandSpec]:
    """Convert configured hook commands into executable command specs."""
    return [
        CommandSpec(command=command, description=description) for command in commands
    ]
