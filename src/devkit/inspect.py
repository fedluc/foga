"""Helpers for the ``devkit inspect`` command."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .config import (
    WORKFLOW_SELECTIONS,
    DevkitConfig,
    build_kind,
    deep_copy_mapping,
    load_config,
)
from .errors import ConfigError


def add_inspect_parser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the inspect command and its subcommands.

    Args:
        subparsers: Top-level subparser collection from the main CLI parser.
    """
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Show the resolved configuration and active command selections.",
    )
    inspect_parser.add_argument("--profile", help="Configuration profile to apply.")
    inspect_parser.add_argument(
        "--full",
        action="store_true",
        help="Show the full resolved configuration document.",
    )
    inspect_subparsers = inspect_parser.add_subparsers(dest="inspect_command")

    inspect_build_parser = inspect_subparsers.add_parser(
        "build", help="Inspect resolved build configuration."
    )
    inspect_build_parser.add_argument(
        "--full",
        action="store_true",
        help="Show the full resolved configuration document.",
    )
    inspect_build_parser.add_argument(
        "selection",
        nargs="?",
        choices=WORKFLOW_SELECTIONS,
        help="Resolve the selected build kind.",
    )
    inspect_build_parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        help="Show native build target overrides in the resolved config.",
    )

    inspect_test_parser = inspect_subparsers.add_parser(
        "test", help="Inspect resolved test configuration."
    )
    inspect_test_parser.add_argument(
        "--full",
        action="store_true",
        help="Show the full resolved configuration document.",
    )
    inspect_test_parser.add_argument(
        "selection",
        nargs="?",
        choices=WORKFLOW_SELECTIONS,
        help="Resolve the selected test kind.",
    )
    inspect_test_parser.add_argument(
        "--runner",
        action="append",
        help="Show only the named test runners in the selection summary.",
    )

    inspect_deploy_parser = inspect_subparsers.add_parser(
        "deploy", help="Inspect resolved deploy configuration."
    )
    inspect_deploy_parser.add_argument(
        "--full",
        action="store_true",
        help="Show the full resolved configuration document.",
    )
    inspect_deploy_parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        help="Show only the named deploy targets in the selection summary.",
    )


def run_inspect(config_path: str | Path, args: argparse.Namespace) -> int:
    """Render the resolved configuration document for the inspect command.

    Args:
        config_path: Path to the configuration file to inspect.
        args: Parsed CLI arguments for the inspect command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If inspect-specific option combinations are invalid.
    """
    config = load_config(config_path, getattr(args, "profile", None))
    _validate_build_target_override(config, args)
    active_profile = _resolve_active_profile_name(config_path, args.profile)
    context = _build_context(config, args)
    resolved_config = _build_resolved_config(config, args)

    document = _build_output_document(
        config=config,
        args=args,
        active_profile=active_profile,
        context=context,
        resolved_config=resolved_config,
    )
    print(yaml.safe_dump(document, sort_keys=False), end="")
    return 0


def _build_output_document(
    config: DevkitConfig,
    args: argparse.Namespace,
    active_profile: str | None,
    context: dict[str, object],
    resolved_config: dict[str, object],
) -> dict[str, object]:
    """Build the inspect output document.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.
        active_profile: Active profile name for the current invocation.
        context: Inspect context summary for the current invocation.
        resolved_config: Full resolved configuration document.

    Returns:
        User-facing inspect output document.
    """
    if getattr(args, "inspect_command", None) and not args.full:
        return {
            "project_root": str(config.project_root),
            "active_profile": active_profile,
            "summary": context,
            "effective_config": _build_effective_config(config, args, resolved_config),
        }

    return {
        "project_root": str(config.project_root),
        "active_profile": active_profile,
        "context": context,
        "resolved_config": resolved_config,
    }


def _validate_build_target_override(
    config: DevkitConfig, args: argparse.Namespace
) -> None:
    """Validate inspect build target overrides.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Raises:
        ConfigError: If a build target override is used with a python-only selection.
    """
    if (
        getattr(args, "inspect_command", None) == "build"
        and args.targets
        and config.build.selected_kinds(args.selection) == ["python"]
    ):
        raise ConfigError(
            "`inspect build --target` can only be used with native builds"
        )


def _build_context(config: DevkitConfig, args: argparse.Namespace) -> dict[str, object]:
    """Build the inspect metadata for the selected command context.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Returns:
        User-facing inspect metadata for the active command context.
    """
    inspect_command = getattr(args, "inspect_command", None)
    if inspect_command == "build":
        return _build_build_context(config, args)
    if inspect_command == "test":
        return _build_test_context(config, args)
    if inspect_command == "deploy":
        return _build_deploy_context(config, args)
    return {"command": "inspect"}


def _build_build_context(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Build inspect metadata for the build subcommand.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Returns:
        Build inspection metadata.
    """
    active_kinds = config.build.selected_kinds(args.selection)
    selected_entries = [
        name
        for name, build_config in config.build.entries.items()
        if build_kind(build_config) in active_kinds
    ]
    effective_targets = {
        name: list(args.targets) if args.targets else config.build.entries[name].targets
        for name in selected_entries
        if build_kind(config.build.entries[name]) == "native"
    }
    return {
        "command": "build",
        "selection": args.selection or config.build.default or "all",
        "active_kinds": active_kinds,
        "selected_entries": selected_entries,
        "effective_targets": effective_targets,
    }


def _build_test_context(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Build inspect metadata for the test subcommand.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Returns:
        Test inspection metadata.
    """
    selected_runners = _select_named_items(
        config.tests.select_runners(args.selection),
        args.runner,
        "test runner",
    )
    return {
        "command": "test",
        "selection": args.selection or config.tests.default or "all",
        "active_kinds": config.tests.selected_kinds(args.selection),
        "selected_runners": list(selected_runners),
    }


def _build_deploy_context(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Build inspect metadata for the deploy subcommand.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Returns:
        Deploy inspection metadata.
    """
    selected_targets = _select_named_items(config.deploy, args.targets, "deploy target")
    return {
        "command": "deploy",
        "selected_targets": list(selected_targets),
    }


def _build_resolved_config(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Return the resolved config mapping with inspect-time overrides applied.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.

    Returns:
        Resolved configuration mapping for display.
    """
    resolved = deep_copy_mapping(config.raw)
    if getattr(args, "inspect_command", None) != "build" or not args.targets:
        return resolved

    build_entries = resolved.get("build")
    if not isinstance(build_entries, dict):
        return resolved

    active_kinds = set(config.build.selected_kinds(args.selection))
    for name, build_config in config.build.entries.items():
        if (
            build_kind(build_config) != "native"
            or build_kind(build_config) not in active_kinds
        ):
            continue
        build_entry = build_entries.get(name)
        if isinstance(build_entry, dict):
            build_entry["targets"] = list(args.targets)
    return resolved


def _build_effective_config(
    config: DevkitConfig, args: argparse.Namespace, resolved_config: dict[str, object]
) -> dict[str, object]:
    """Build the concise effective config for subcommand inspection.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.
        resolved_config: Full resolved configuration document.

    Returns:
        Concise config fragment relevant to the selected inspect subcommand.
    """
    inspect_command = getattr(args, "inspect_command", None)
    if inspect_command == "build":
        return _build_effective_build_config(config, args, resolved_config)
    if inspect_command == "test":
        return _build_effective_test_config(config, args, resolved_config)
    if inspect_command == "deploy":
        return _build_effective_deploy_config(config, args, resolved_config)
    return resolved_config


def _build_effective_build_config(
    config: DevkitConfig, args: argparse.Namespace, resolved_config: dict[str, object]
) -> dict[str, object]:
    """Build the concise config fragment for build inspection.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.
        resolved_config: Full resolved configuration document.

    Returns:
        Build-specific config fragment.
    """
    build_section = resolved_config.get("build")
    if not isinstance(build_section, dict):
        return {}

    active_kinds = set(config.build.selected_kinds(args.selection))
    selected_entries = {
        name: entry
        for name, entry in build_section.items()
        if name == "default"
        or (
            name in config.build.entries
            and build_kind(config.build.entries[name]) in active_kinds
        )
    }
    return {"build": selected_entries}


def _build_effective_test_config(
    config: DevkitConfig, args: argparse.Namespace, resolved_config: dict[str, object]
) -> dict[str, object]:
    """Build the concise config fragment for test inspection.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.
        resolved_config: Full resolved configuration document.

    Returns:
        Test-specific config fragment.
    """
    test_section = resolved_config.get("test")
    if not isinstance(test_section, dict):
        return {}

    selected_runners = _select_named_items(
        config.tests.select_runners(args.selection),
        args.runner,
        "test runner",
    )
    runners_section = test_section.get("runners")
    if not isinstance(runners_section, dict):
        return {"test": {"default": test_section.get("default"), "runners": {}}}

    effective_test = {"runners": {}}
    if "default" in test_section:
        effective_test["default"] = test_section["default"]
    effective_test["runners"] = {
        name: runners_section[name]
        for name in selected_runners
        if name in runners_section
    }
    return {"test": effective_test}


def _build_effective_deploy_config(
    config: DevkitConfig, args: argparse.Namespace, resolved_config: dict[str, object]
) -> dict[str, object]:
    """Build the concise config fragment for deploy inspection.

    Args:
        config: Loaded project configuration.
        args: Parsed inspect command arguments.
        resolved_config: Full resolved configuration document.

    Returns:
        Deploy-specific config fragment.
    """
    deploy_section = resolved_config.get("deploy")
    if not isinstance(deploy_section, dict):
        return {}

    selected_targets = _select_named_items(config.deploy, args.targets, "deploy target")
    targets_section = deploy_section.get("targets")
    if not isinstance(targets_section, dict):
        return {"deploy": {"targets": {}}}

    return {
        "deploy": {
            "targets": {
                name: targets_section[name]
                for name in selected_targets
                if name in targets_section
            }
        }
    }


def _resolve_active_profile_name(
    config_path: str | Path, requested_profile: str | None
) -> str | None:
    """Resolve the active profile name for inspect output.

    Args:
        config_path: Path to the configuration file.
        requested_profile: Explicit profile requested on the CLI.

    Returns:
        Active profile name, or ``None`` when no profile applies.
    """
    if requested_profile is not None:
        return requested_profile

    path = Path(config_path).resolve()
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return None

    profiles = data.get("profiles")
    if not isinstance(profiles, dict):
        return None
    if "default" in profiles:
        return "default"
    return None


def _select_named_items(
    items: dict[str, object], selected_names: list[str] | None, label: str
) -> dict[str, object]:
    """Filter named configuration items and validate explicit selections.

    Args:
        items: Available named items.
        selected_names: Optional list of names explicitly requested by the user.
        label: Human-readable item label used in validation errors.

    Returns:
        All items when no explicit selection is given, otherwise only the
        requested items.

    Raises:
        ConfigError: If any requested item name is unknown.
    """
    if not selected_names:
        return items

    selected: dict[str, object] = {}
    for name in selected_names:
        if name not in items:
            raise ConfigError(f"Unknown {label}: {name}")
        selected[name] = items[name]
    return selected
