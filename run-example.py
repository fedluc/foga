#!/usr/bin/env python3
"""Run one of the repository tutorial examples by short name."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def main() -> int:
    from foga.example_runner import main as runner_main

    return runner_main()


if __name__ == "__main__":
    raise SystemExit(main())
