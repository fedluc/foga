"""CLI entrypoint and command routing for devkit."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .adapters import build_specs, deploy_specs, runner_specs
from .config import DevkitConfig, load_config
from .errors import ConfigError, DevkitError
from .executor import CommandExecutor


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
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
    """Create the top-level argument parser for the CLI."""
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
    """Register the shared profile-selection argument on a parser."""
    parser.add_argument("--profile", help="Configuration profile to apply.")


def _run_build(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured build workflows."""
    specs = build_specs(config.build, targets=args.targets)
    if not specs:
        raise ConfigError("No build workflows configured")
    executor.run_specs(specs, dry_run=args.dry_run)
    return 0


def _run_test(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured test workflows."""
    selected = _select_named_items(config.tests, args.runner, "test runner")
    specs = []
    for runner in selected.values():
        specs.extend(runner_specs(runner))
    if not specs:
        raise ConfigError("No test workflows configured")
    executor.run_specs(specs, dry_run=args.dry_run)
    return 0


def _run_deploy(
    config: DevkitConfig, executor: CommandExecutor, args: argparse.Namespace
) -> int:
    """Execute configured deploy workflows."""
    selected = _select_named_items(config.deploy, args.targets, "deploy target")
    specs = []
    for target in selected.values():
        specs.extend(deploy_specs(config.project_root, target))
    if not specs:
        raise ConfigError("No deploy workflows configured")
    executor.run_specs(specs, dry_run=args.dry_run)
    return 0


def _select_named_items(
    items: dict[str, object], selected_names: list[str] | None, label: str
) -> dict[str, object]:
    """Filter named configuration items and validate explicit selections."""
    if not selected_names:
        return items

    selected: dict[str, object] = {}
    for name in selected_names:
        if name not in items:
            raise ConfigError(f"Unknown {label}: {name}")
        selected[name] = items[name]
    return selected


def _run_clean(config: DevkitConfig) -> int:
    """Remove configured build artifacts from the project root."""
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
