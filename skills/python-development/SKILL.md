---
name: python-development
description: Implement, refactor, review, and maintain Python code in this repository. Use when editing Python source, tests, packaging metadata, CLI/config behavior, documentation tooling, or project workflow files that must be verified with uv, Ruff, pytest, Sphinx, or build checks.
---

# Python Development

Use this skill for Python work in `foga`. Keep changes small, typed,
testable, and consistent with the existing `src/foga/` and `tests/` layout.

This skill is the operational checklist for agents. Its commands intentionally
mirror `docs/development.md`; when the development workflow changes, update both
places in the same patch.

## Working Rules

- Inspect the relevant source, tests, and `pyproject.toml` before editing
  behavior, packaging, or tooling.
- Prefer the repository's existing patterns and module boundaries over new
  abstractions.
- Write the minimum code that solves the request. Add configurability,
  indirection, or helper modules only when the current change needs them.
- Preserve existing CLI and config behavior unless the task explicitly changes
  it.
- Use standard-library solutions unless the repository already depends on a
  better fit.
- Add or update tests in the same change when behavior changes.
- If a required tool or verification command is unavailable, state what failed
  and why.

## Environment

Set up or refresh the environment with the development and documentation extras:

```bash
uv sync --extra dev --extra docs
```

## Python Standards

- Target the Python version declared in `pyproject.toml`.
- Add type hints for public functions and non-trivial internal helpers.
- Prefer `pathlib.Path`, dataclasses, and explicit typed containers over
  stringly typed state.
- Use concrete built-in generics such as `list[str]` and `dict[str, str]`.
- Keep functions focused. Split code only when it improves readability or
  testability.
- Raise precise exceptions with actionable messages at filesystem, subprocess,
  CLI, and config boundaries.
- Keep comments sparse. Add them only for behavior that is not obvious from the
  code.
- Use `from __future__ import annotations` when surrounding modules do.

## Docstrings

- Keep added or touched Python docstrings in valid Google style.
- Do not add placeholder docstrings. Explain parameters, returns, exceptions, or
  fields when that information is not obvious.
- Review touched public functions, helpers, and dataclasses before finishing.

## Tests

- Prefer tests that assert observable behavior instead of implementation
  details.
- Keep fixtures local to the test module unless they are broadly reused.
- For CLI changes, test exit codes and user-visible output.
- For config parsing, test both valid and invalid inputs.
- Add regression coverage for bug fixes before or alongside the fix.

Run targeted tests first when a narrower test file covers the change, for
example:

```bash
uv run pytest tests/test_cli.py
```

Run the full test suite before finishing behavior, CLI, or config changes:

```bash
uv run pytest
```

## Ruff

- Use Ruff as the formatting and linting tool.
- Fix lint violations in touched code rather than suppressing them by default.
- Add ignores only when the repository already has a reason or the alternative
  is clearly worse.

Format and lint with uv:

```bash
uv run ruff format .
uv run ruff check .
```

## Documentation

- Update README, docs, or examples when user-visible CLI, config, packaging, or
  workflow behavior changes.

When documentation changes, build docs with warnings treated as errors:

```bash
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
```

## Packaging and Layout

- Keep application code under `src/foga/` and tests under `tests/`.
- Keep project and tool configuration in `pyproject.toml`.
- Prefer PEP 621 metadata in `pyproject.toml`.
- Keep the committed `uv.lock` in sync with dependency metadata.
- `foga` expects a root-level `foga.yml` for project configuration.

When dependency metadata changes, refresh the committed lockfile:

```bash
uv lock
```

Before release-oriented changes, build the distributions:

```bash
uv run python -m build
```
