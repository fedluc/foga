"""Cross-platform launcher for repository tutorial examples."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ExampleSpec:
    """Metadata for a runnable repository example."""

    name: str
    directory: str
    description: str
    dockerfile: str
    driver_script: str = "run_example.py"
    aliases: tuple[str, ...] = ()


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODE = "docker"
EXAMPLES: tuple[ExampleSpec, ...] = (
    ExampleSpec(
        name="python-only",
        directory="examples/tutorial/01-python-only",
        description=(
            "Pure Python package build in a containerized tutorial environment."
        ),
        dockerfile="examples/tutorial/01-python-only/Dockerfile",
        aliases=("01-python-only", "tutorial/01-python-only"),
    ),
    ExampleSpec(
        name="pybind11-hello",
        directory="examples/tutorial/02-pybind11-hello",
        description=(
            "Minimal pybind11 example with system packages installed in Docker."
        ),
        dockerfile="examples/tutorial/02-pybind11-hello/Dockerfile",
        aliases=("02-pybind11-hello", "tutorial/02-pybind11-hello"),
    ),
    ExampleSpec(
        name="pybind11-tests",
        directory="examples/tutorial/03-pybind11-tests",
        description=(
            "Mixed C++ and Python example with tests and Ruff linting in Docker."
        ),
        dockerfile="examples/tutorial/03-pybind11-tests/Dockerfile",
        aliases=("03-pybind11-tests", "tutorial/03-pybind11-tests"),
    ),
    ExampleSpec(
        name="pybind11-profiles",
        directory="examples/tutorial/04-pybind11-profiles",
        description="Mixed C++ and Python example with profiled builds in Docker.",
        dockerfile="examples/tutorial/04-pybind11-profiles/Dockerfile",
        aliases=("04-pybind11-profiles", "tutorial/04-pybind11-profiles"),
    ),
)


def resolve_example(name: str) -> ExampleSpec:
    """Resolve an example by short name or compatibility alias."""

    for spec in EXAMPLES:
        if name == spec.name or name in spec.aliases:
            return spec
    raise KeyError(name)


def example_root(spec: ExampleSpec) -> Path:
    """Return the repository path for one example."""

    return REPO_ROOT / spec.directory


def driver_path(spec: ExampleSpec) -> Path:
    """Return the per-example driver script path."""

    return example_root(spec) / spec.driver_script


def format_examples() -> str:
    """Render the available example list for CLI help output."""

    lines = ["Available examples:"]
    for spec in EXAMPLES:
        aliases = ", ".join(spec.aliases)
        lines.append(f"  {spec.name:<18} {spec.description}")
        lines.append(f"                    aliases: {aliases}")
    return "\n".join(lines)


def require_tool(name: str) -> str:
    """Resolve an external tool path or raise a user-facing error."""

    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"`{name}` is required to run the repository examples")
    return path


def build_host_command(spec: ExampleSpec, args: Sequence[str]) -> list[str]:
    """Build the local example-driver command."""

    uv = require_tool("uv")
    return [
        uv,
        "run",
        "--project",
        str(example_root(spec)),
        "python",
        str(driver_path(spec)),
        *args,
    ]


def docker_image_tag(spec: ExampleSpec) -> str:
    """Return the Docker image tag used for one example."""

    return f"foga-example-{spec.name}"


def build_docker_build_command(spec: ExampleSpec) -> list[str]:
    """Build the Docker image command for one example."""

    docker = require_tool("docker")
    return [
        docker,
        "build",
        "-f",
        str(REPO_ROOT / spec.dockerfile),
        "-t",
        docker_image_tag(spec),
        str(example_root(spec)),
    ]


def build_docker_run_command(spec: ExampleSpec, args: Sequence[str]) -> list[str]:
    """Build the Docker container run command for one example."""

    docker = require_tool("docker")
    return [
        docker,
        "run",
        "--rm",
        docker_image_tag(spec),
        "python",
        spec.driver_script,
        *args,
    ]


def run_command(command: Sequence[str], *, cwd: Path) -> None:
    """Run one external command with simple logging."""

    print(f"RUN: {shlex.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def run_host_example(spec: ExampleSpec, forwarded_args: Sequence[str]) -> None:
    """Run an example directly on the current machine."""

    run_command(build_host_command(spec, forwarded_args), cwd=REPO_ROOT)


def run_docker_example(spec: ExampleSpec, forwarded_args: Sequence[str]) -> None:
    """Build and run an example inside its dedicated Docker image."""

    run_command(build_docker_build_command(spec), cwd=REPO_ROOT)
    run_command(build_docker_run_command(spec, forwarded_args), cwd=REPO_ROOT)


def run_example(
    name: str,
    forwarded_args: Sequence[str],
    *,
    mode: str = DEFAULT_MODE,
) -> int:
    """Run an example by name in either Docker or host mode."""

    normalized_args = tuple(forwarded_args)

    try:
        spec = resolve_example(name)
    except KeyError:
        print(f"Unknown example: {name}", file=sys.stderr)
        print(format_examples(), file=sys.stderr)
        return 1

    try:
        if mode == "host":
            run_host_example(spec, normalized_args)
        else:
            run_docker_example(spec, normalized_args)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""

    parser = argparse.ArgumentParser(
        prog="run-example.py",
        description=(
            "Run one of the repository tutorial examples by short name. "
            "Docker mode is the default so the examples do not mutate the host."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=("docker", "host"),
        default=DEFAULT_MODE,
        help="Execution mode. `docker` is the default; `host` runs commands locally.",
    )
    parser.add_argument(
        "example",
        nargs="?",
        help="Example short name, such as python-only.",
    )
    parser.add_argument(
        "example_args",
        nargs=argparse.REMAINDER,
        help="Optional walkthrough step names passed to the example driver.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the available example names and exit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the example launcher CLI."""

    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.list or args.example is None:
        print("Usage: python run-example.py [--mode docker|host] <example> [step ...]")
        print("")
        print("Examples:")
        print("  python run-example.py python-only")
        print("  python run-example.py pybind11-profiles --list-steps")
        print("  python run-example.py pybind11-profiles build-release test-release")
        print("  python run-example.py --mode host pybind11-tests lint")
        print("")
        print(format_examples())
        return 0

    return run_example(args.example, args.example_args, mode=args.mode)


if __name__ == "__main__":
    raise SystemExit(main())
