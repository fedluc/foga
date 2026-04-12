"""CLI entrypoint and command routing for devkit."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

from .adapters.build import plan_build
from .adapters.deploy import plan_deploy
from .adapters.testing import plan_tests
from .config import (
    WORKFLOW_SELECTIONS,
    DevkitConfig,
    build_kind,
    deep_copy_mapping,
    load_config,
)
from .errors import ConfigError, DevkitError
from .executor import CommandExecutor


def main(argv: list[str] | None = None) -> int:
    """Run the CLI.

    Args:
        argv: Optional CLI arguments. When omitted, ``argparse`` reads from
            ``sys.argv``.

    Returns:
        Process exit code for the invoked command.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command is None:
            parser.print_help()
            return 0

        config = load_config(args.config, getattr(args, "profile", None))

        if args.command == "validate":
            print(f"Configuration valid for project `{config.project.name}`")
            return 0
        if args.command == "inspect":
            return _run_inspect(config, args)
        executor = CommandExecutor(config.project_root)
        if args.command == "build":
            return _run_build(config, executor, args)
        if args.command == "test":
            return _run_test(config, executor, args)
        if args.command == "deploy":
            return _run_deploy(config, executor, args)
        if args.command == "clean":
            return _run_clean(config)
    except DevkitError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Create the top-level argument parser for the CLI.

    Returns:
        Configured parser for all supported ``devkit`` commands.
    """
    parser = argparse.ArgumentParser(
        description="Unified developer CLI for Python/C++ package workflows."
    )
    parser.add_argument(
        "--config",
        default="devkit.yml",
        help="Path to the devkit YAML configuration file.",
    )

    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser(
        "build", help="Run configured build workflows."
    )
    _add_profile_arg(build_parser)
    build_parser.add_argument(
        "selection",
        nargs="?",
        choices=WORKFLOW_SELECTIONS,
        help="Run only the selected build kind.",
    )
    build_parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        help="Override native build target.",
    )
    build_parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing them."
    )

    test_parser = subparsers.add_parser("test", help="Run configured test workflows.")
    _add_profile_arg(test_parser)
    test_parser.add_argument(
        "selection",
        nargs="?",
        choices=WORKFLOW_SELECTIONS,
        help="Run only the selected test kind.",
    )
    test_parser.add_argument(
        "--runner", action="append", help="Run only the named test runner."
    )
    test_parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing them."
    )

    deploy_parser = subparsers.add_parser(
        "deploy", help="Run configured deployment workflows."
    )
    _add_profile_arg(deploy_parser)
    deploy_parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        help="Run only the named deploy target.",
    )
    deploy_parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing them."
    )

    clean_parser = subparsers.add_parser(
        "clean", help="Remove configured build artifacts."
    )
    _add_profile_arg(clean_parser)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate the configuration file."
    )
    _add_profile_arg(validate_parser)

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Show the resolved configuration and active command selections.",
    )
    _add_profile_arg(inspect_parser)
    inspect_subparsers = inspect_parser.add_subparsers(dest="inspect_command")

    inspect_build_parser = inspect_subparsers.add_parser(
        "build", help="Inspect resolved build configuration."
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
        "--target",
        action="append",
        dest="targets",
        help="Show only the named deploy targets in the selection summary.",
    )

    return parser


def _add_profile_arg(parser: argparse.ArgumentParser) -> None:
    """Register the shared profile-selection argument on a parser.

    Args:
        parser: Parser that should accept the ``--profile`` option.
    """
    parser.add_argument("--profile", help="Configuration profile to apply.")


def _run_build(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured build workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated build commands.
        args: Parsed CLI arguments for the ``build`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no matching build workflows are configured or if
            incompatible CLI options are combined.
    """
    resolved_selection = args.selection or config.build.default

    if args.targets and config.build.selected_kinds(args.selection) == ["python"]:
        raise ConfigError("`build --target` can only be used with native builds")

    plan = plan_build(config.build, selection=args.selection, targets=args.targets)
    if not plan.specs:
        if resolved_selection and resolved_selection != "all":
            raise ConfigError(f"No {resolved_selection} build workflows configured")
        raise ConfigError("No build workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


def _run_test(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured test workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated test commands.
        args: Parsed CLI arguments for the ``test`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no matching test workflows are configured.
    """
    resolved_selection = args.selection or config.tests.default
    selected_by_kind = config.tests.select_runners(args.selection)
    selected = _select_named_items(selected_by_kind, args.runner, "test runner")
    plan = plan_tests(list(selected.values()))
    if not plan.specs:
        if resolved_selection and resolved_selection != "all":
            raise ConfigError(f"No {resolved_selection} test workflows configured")
        raise ConfigError("No test workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


def _run_deploy(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured deploy workflows.

    Args:
        config: Loaded project configuration.
        executor: Command executor used to run generated deploy commands.
        args: Parsed CLI arguments for the ``deploy`` command.

    Returns:
        Process exit code for the command.

    Raises:
        ConfigError: If no deploy workflows are configured.
    """
    selected = _select_named_items(config.deploy, args.targets, "deploy target")
    plan = plan_deploy(config.project_root, list(selected.values()))
    if not plan.specs:
        raise ConfigError("No deploy workflows configured")
    executor.run_specs(plan.specs, dry_run=args.dry_run)
    return 0


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


def _run_inspect(config: DevkitConfig, args: argparse.Namespace) -> int:
    """Print the resolved configuration and active inspect context."""
    if (
        getattr(args, "inspect_command", None) == "build"
        and args.targets
        and config.build.selected_kinds(args.selection) == ["python"]
    ):
        raise ConfigError(
            "`inspect build --target` can only be used with native builds"
        )

    document = {
        "project_root": str(config.project_root),
        "active_profile": config.active_profile,
        "context": _inspect_context(config, args),
        "resolved_config": _inspect_resolved_config(config, args),
    }
    print(yaml.safe_dump(document, sort_keys=False), end="")
    return 0


def _inspect_context(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Build user-facing inspect metadata for the selected command context."""
    inspect_command = getattr(args, "inspect_command", None)
    if inspect_command == "build":
        selected_entries = {
            name: build_config
            for name, build_config in config.build.entries.items()
            if build_kind(build_config) in config.build.selected_kinds(args.selection)
        }
        effective_targets = {
            name: args.targets if args.targets else build_config.targets
            for name, build_config in selected_entries.items()
            if build_kind(build_config) == "native"
        }
        return {
            "command": "build",
            "selection": args.selection or config.build.default or "all",
            "active_kinds": config.build.selected_kinds(args.selection),
            "selected_entries": list(selected_entries),
            "effective_targets": effective_targets,
        }
    if inspect_command == "test":
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
    if inspect_command == "deploy":
        selected_targets = _select_named_items(
            config.deploy, args.targets, "deploy target"
        )
        return {
            "command": "deploy",
            "selected_targets": list(selected_targets),
        }
    return {"command": "inspect"}


def _inspect_resolved_config(
    config: DevkitConfig, args: argparse.Namespace
) -> dict[str, object]:
    """Return the resolved config mapping with inspect-time overrides applied."""
    resolved = deep_copy_mapping(config.raw)
    inspect_command = getattr(args, "inspect_command", None)

    if inspect_command == "build" and args.targets:
        build_entries = resolved.get("build")
        if isinstance(build_entries, dict):
            active_kinds = set(config.build.selected_kinds(args.selection))
            for name, build_config in config.build.entries.items():
                if build_kind(build_config) != "native":
                    continue
                if build_kind(build_config) not in active_kinds:
                    continue
                build_entry = build_entries.get(name)
                if isinstance(build_entry, dict):
                    build_entry["targets"] = list(args.targets)

    return resolved


def _run_clean(config: DevkitConfig) -> int:
    """Remove configured build artifacts from the project root.

    Args:
        config: Loaded project configuration.

    Returns:
        Process exit code for the command.
    """
    for path_str in config.clean.paths:
        path = Path(config.project_root, path_str)
        if not path.exists():
            continue
        if path.is_dir():
            print(f"Removing directory {path}")
            shutil.rmtree(path)
        else:
            print(f"Removing file {path}")
            path.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
