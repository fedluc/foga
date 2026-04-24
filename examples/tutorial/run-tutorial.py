#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import typer

app = typer.Typer(add_completion=False, invoke_without_command=True)


def available_examples(tutorial_root: Path) -> list[str]:
    """Return the tutorial directories that provide a Docker image.

    Args:
        tutorial_root: Root directory that contains the tutorial examples.

    Returns:
        Sorted example directory names that include a Dockerfile.
    """
    return sorted(
        path.name
        for path in tutorial_root.iterdir()
        if path.is_dir() and (path / "Dockerfile").is_file()
    )


def print_available_examples(examples: list[str]) -> None:
    """Print the available example names.

    Args:
        examples: Tutorial example names to print.
    """

    print("\n".join(examples))


def require_example_name(example: str | None, examples: list[str]) -> str:
    """Validate the selected example name.

    Args:
        example: User-provided example name.
        examples: Supported example names.

    Returns:
        The validated example name.

    Raises:
        typer.Exit: If no valid example name was provided.
    """

    if example in examples:
        return example

    typer.secho("Choose one of the available examples:", err=True, fg=typer.colors.RED)
    for candidate in examples:
        typer.echo(f"  - {candidate}", err=True)
    raise typer.Exit(code=2)


def require_docker() -> None:
    """Ensure Docker is available before running the example.

    Raises:
        typer.Exit: If Docker is not installed.
    """

    if shutil.which("docker") is None:
        typer.secho(
            "Docker is required but was not found.", err=True, fg=typer.colors.RED
        )
        raise typer.Exit(code=1)


def build_image(example_dir: Path, image_name: str) -> int:
    """Build the Docker image for a tutorial example.

    Args:
        example_dir: Filesystem path to the tutorial directory.
        image_name: Docker image tag to build.

    Returns:
        The Docker build exit code.
    """

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as build_log:
        build_log_path = Path(build_log.name)

    try:
        with build_log_path.open("w", encoding="utf-8") as stream:
            result = subprocess.run(
                ["docker", "build", "--no-cache", "-t", image_name, str(example_dir)],
                stdout=stream,
                stderr=subprocess.STDOUT,
                check=False,
            )

        if result.returncode != 0:
            print("Docker image build failed. Full output follows:")
            print(build_log_path.read_text(encoding="utf-8"), end="")

        return result.returncode
    finally:
        build_log_path.unlink(missing_ok=True)


def run_container(image_name: str) -> int:
    """Start an interactive shell inside the tutorial container.

    Args:
        image_name: Docker image tag to run.

    Returns:
        The container exit code.
    """

    print("Environment ready.")
    print("You will be dropped into the container, where you can run the example.")
    print('Run "exit" to leave the container.')
    print()
    print("Entering container...")
    print()

    run_result = subprocess.run(
        ["docker", "run", "--rm", "-it", image_name, "bash", "-i"],
        check=False,
    )
    return run_result.returncode


def run_tutorial(example_name: str, tutorial_root: Path) -> int:
    """Build and run the selected tutorial example in Docker.

    Args:
        example_name: Name of the tutorial example to run.
        tutorial_root: Root directory that contains the tutorial examples.

    Returns:
        The final process exit code.
    """

    require_docker()
    example_dir = tutorial_root / example_name
    image_name = f"foga-tutorial-{example_name}"

    print(f"Setting up tutorial environment for {example_name}")
    build_exit_code = build_image(example_dir, image_name)
    if build_exit_code != 0:
        return build_exit_code
    return run_container(image_name)


@app.callback()
def main(
    example: str | None = typer.Argument(None, help="Tutorial example name."),
    list_examples: bool = typer.Option(
        False,
        "--list",
        help="Print the available examples and exit.",
    ),
) -> None:
    """Build and run a tutorial example in Docker.

    Args:
        example: Tutorial example name to run.
        list_examples: Whether to print the available examples and exit.

    Raises:
        typer.Exit: Always exits with the command status code.
    """

    tutorial_root = Path(__file__).resolve().parent
    examples = available_examples(tutorial_root)

    if list_examples:
        print_available_examples(examples)
        raise typer.Exit(code=0)

    example_name = require_example_name(example, examples)
    raise typer.Exit(code=run_tutorial(example_name, tutorial_root))


if __name__ == "__main__":
    app()
