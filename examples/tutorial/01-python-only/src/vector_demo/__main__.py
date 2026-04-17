from __future__ import annotations

from rich.console import Console

from . import centered_norm


def main() -> None:
    vector = [1.0, 2.0, 3.0]
    norm = centered_norm(vector)
    Console().print(f"Centered norm for {vector}: {norm:.3f}")


if __name__ == "__main__":
    main()
