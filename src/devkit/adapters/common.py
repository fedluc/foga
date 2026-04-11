"""Shared helpers for backend command generation."""

from __future__ import annotations

from ..config import HookConfig
from ..executor import CommandSpec


def split_hooks(
    hooks: HookConfig, prefix: str
) -> tuple[list[CommandSpec], list[CommandSpec]]:
    """Build command specs for pre- and post-hooks separately."""

    pre = [
        CommandSpec(command=command, description=f"{prefix} pre-hook")
        for command in hooks.pre
    ]
    post = [
        CommandSpec(command=command, description=f"{prefix} post-hook")
        for command in hooks.post
    ]
    return pre, post
