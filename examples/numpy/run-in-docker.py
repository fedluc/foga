#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def require_docker() -> None:
    """Ensure Docker is installed before trying to run the example."""

    if shutil.which("docker") is not None:
        return
    raise SystemExit("docker is required but was not found")


def build_image(repo_root: Path, image_name: str) -> None:
    """Build the Docker image for the NumPy example."""

    subprocess.run(
        [
            "docker",
            "build",
            "-f",
            str(repo_root / "examples" / "numpy" / "Dockerfile"),
            "-t",
            image_name,
            str(repo_root),
        ],
        check=True,
    )


def run_container(image_name: str, command: list[str]) -> int:
    """Run the NumPy example container with the requested command."""

    result = subprocess.run(
        ["docker", "run", "--rm", "-it", image_name, *command],
        check=False,
    )
    return result.returncode


def main(argv: list[str]) -> int:
    """Build the NumPy example image and run a command inside it."""

    require_docker()
    repo_root = Path(__file__).resolve().parents[2]
    image_name = os.environ.get("FOGA_EXAMPLE_IMAGE", "foga-example-numpy")
    command = argv[1:] if len(argv) > 1 else ["bash"]

    build_image(repo_root, image_name)
    return run_container(image_name, command)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
