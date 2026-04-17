"""Guided runner for the tested pybind11 tutorial example."""

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
        "description": "Run the full tested pybind11 walkthrough.",
        "commands": (
            (
                "Validate the config before reusing build directories.",
                ("validate",),
            ),
            (
                "Install the Python-side development dependencies. The Docker image already bakes in the system toolchain.",
                ("install", "--target", "dev"),
            ),
            (
                "Build the C++ targets and the Python wheel.",
                ("build",),
            ),
            (
                "Run the Python and C++ test suites.",
                ("test",),
            ),
            (
                "Run the configured lint workflow.",
                ("lint",),
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
    "install-system": {
        "description": "Install the native build toolchain on the current machine.",
        "commands": (
            (
                "Install the system toolchain declared in the config.",
                ("install", "--target", "system"),
            ),
        ),
    },
    "build": {
        "description": "Build the configured C++ and Python targets.",
        "commands": (("Build the C++ and Python outputs.", ("build",)),),
    },
    "test": {
        "description": "Run the Python and C++ tests.",
        "commands": (("Run the configured test workflows.", ("test",)),),
    },
    "lint": {
        "description": "Run the configured lint workflow.",
        "commands": (("Run the lint workflow.", ("lint",)),),
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
        description="Run the tested pybind11 tutorial example walkthrough."
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
