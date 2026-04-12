---
name: python-development
description: Implement, refactor, review, and maintain modern Python projects with consistent repository standards. Use when Codex is editing Python source, tests, packaging metadata, or developer tooling and needs project-specific guidance for code structure, type hints, linting, formatting, and verification. Especially useful for tasks involving `pyproject.toml`, `src/`, `tests/`, CLI code, packaging, or changes that must satisfy `ruff`, `pytest`, and build validation.
---

# Python Development

Use this skill to keep Python changes small, typed, testable, and easy to verify.

## Workflow

1. Inspect the existing module, tests, and `pyproject.toml` before changing behavior.
2. Match the repository's current structure instead of introducing new abstractions by default.
3. Prefer small pure functions, explicit data flow, and standard-library solutions unless the repo already depends on something heavier.
4. Add or update tests in the same change when behavior changes.
5. Run formatting, linting, and relevant tests before finishing.
6. Review any touched Python docstrings before finishing and keep them in valid Google style.

## Coding Standards

- Target Python 3.10+ features already used by the repo.
- Add type hints for public functions and for internal functions when they clarify behavior.
- When Python docstrings are added or touched, keep them in valid Google style. Use `Args:`, `Returns:`, `Raises:`, and `Attributes:` sections where they add value, and do not leave touched public functions, helpers, or dataclasses with placeholder one-line docstrings when parameters, return values, exceptions, or fields need explanation.
- Prefer `pathlib.Path`, `dataclass`, and straightforward collections over stringly-typed or deeply nested state.
- Raise precise exceptions with actionable messages.
- Keep functions focused. Split only when it improves readability or testability.
- Avoid premature frameworks, dependency injection layers, or generic utility modules unless the codebase already uses them.
- Prefer `__future__.annotations` in Python modules when surrounding files use it.
- Keep comments sparse. Add them only when behavior is non-obvious.

## Testing and Validation

Run the smallest useful verification first, then the full repository checks before finalizing.

For this repository, standard verification is:

```bash
ruff format .
ruff check .
pytest
python -m build
```

Use judgment:

- Run targeted tests first when a narrow test file covers the change.
- Run `pytest` for any behavior change, bug fix, or CLI/config update.
- Run `python -m build` when packaging metadata, dependencies, entry points, or install behavior changes.
- If a command cannot be run, state that clearly and explain why.

## Ruff Policy

- Use `ruff format .` as the default formatter.
- Use `ruff check .` as the default linter.
- Fix lint violations in touched files rather than suppressing them by default.
- Add ignores only when the repository has a documented reason and the alternative is clearly worse.

## Testing Policy

- Add tests for new behavior and regressions.
- Prefer assertions on observable behavior, not implementation details.
- Keep fixtures local to the test module unless they are broadly reused.
- For CLI behavior, test exit codes and user-visible output.
- For config parsing, test both valid and invalid inputs.

## Packaging and Project Layout

- Keep application code under `src/` and tests under `tests/` when the repo already follows that layout.
- Keep tool configuration in `pyproject.toml` unless the repo has an established alternative.
- Prefer PEP 621 metadata in `pyproject.toml`.
- Keep development dependencies and verification commands aligned with documentation and devcontainer setup.

## References

- Read [references/python-standards.md](references/python-standards.md) for the detailed checklist and code-review heuristics used by this skill.

## Work Log

- 2026-04-11: In `/workspaces/devkit`, added module, class, and function docstrings across the Python package and tests to improve API readability without changing behavior.
- 2026-04-11: Recorded the repository preference for Google-style Python docstrings so future docstring updates stay consistent.
