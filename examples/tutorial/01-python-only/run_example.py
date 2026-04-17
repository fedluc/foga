"""Guided runner for the pure Python tutorial example."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
STEPS = {
    "default": {
        "description": "Run the full pure Python walkthrough.",
        "commands": (
            (
                "Validate the config before creating any local project state.",
                ("validate",),
            ),
            (
                "Install the example development environment with uv.",
                ("install", "--target", "dev"),
            ),
            (
                "Build the wheel for the pure Python package.",
                ("build",),
            ),
        ),
    },
    "validate": {
        "description": "Check that the example config resolves cleanly.",
        "commands": (("Validate the example config.", ("validate",)),),
    },
    "install": {
        "description": "Create the example development environment.",
        "commands": (
            ("Install the development environment.", ("install", "--target", "dev")),
        ),
    },
    "build": {
        "description": "Build the Python package artifact.",
        "commands": (("Build the Python package.", ("build",)),),
    },
}


def print_steps(*, stream: object = sys.stdout) -> None:
    print("Available steps:", file=stream)
    for name, step in STEPS.items():
        print(f"  {name:<14} {step['description']}", file=stream)


def run_foga(command_args: Sequence[str], note: str) -> None:
    command = ["uv", "run", "foga", "--config", "foga.yml", *command_args]
    print(f"\n== {note}")
    print(f"$ {shlex.join(command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the pure Python tutorial example walkthrough."
    )
    parser.add_argument(
        "steps",
        nargs="*",
        help="Named walkthrough steps. Defaults to `default`.",
    )
    parser.add_argument(
        "--list-steps",
        action="store_true",
        help="Print the available walkthrough steps and exit.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.list_steps:
        print_steps()
        return 0

    for step_name in args.steps or ["default"]:
        step = STEPS.get(step_name)
        if step is None:
            print(f"Unknown step: {step_name}", file=sys.stderr)
            print_steps(stream=sys.stderr)
            return 1
        for note, command_args in step["commands"]:
            run_foga(command_args, note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
