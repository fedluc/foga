"""CLI entrypoint and command routing for devkit."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .adapters.build import plan_build
from .adapters.deploy import plan_deploy
from .adapters.testing import plan_tests
from .config import WORKFLOW_SELECTIONS, DevkitConfig, load_config
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
        executor = CommandExecutor(config.project_root)

        if args.command == "validate":
            print(f"Configuration valid for project `{config.project.name}`")
            return 0
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
    if args.targets and config.build.selected_kinds(args.selection) == ["python"]:
        raise ConfigError("`build --target` can only be used with native builds")

    plan = plan_build(config.build, selection=args.selection, targets=args.targets)
    if not plan.specs:
        if args.selection:
            raise ConfigError(f"No {args.selection} build workflows configured")
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
    selected_by_kind = config.tests.select_runners(args.selection)
    selected = _select_named_items(selected_by_kind, args.runner, "test runner")
    plan = plan_tests(list(selected.values()))
    if not plan.specs:
        if args.selection:
            raise ConfigError(f"No {args.selection} test workflows configured")
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
