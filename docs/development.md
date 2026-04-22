# Development

Install `uv` first if it is not already available in your shell, then sync the
repository environment with the extras used in development and documentation:

```bash
uv sync --extra dev --extra docs
```

If you only need a plain editable install from a local checkout, this also
works:

```bash
pip install -e .[dev]
```

Standard verification:

```bash
# Lint the codebase for style and static issues.
uv run ruff check .
# Run the automated test suite.
uv run pytest
# Build source and wheel distributions.
uv run python -m build
# Build the docs and fail on warnings.
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
```

When dependency metadata changes, refresh the committed lockfile with:

```bash
uv lock
```

## Devcontainer

The repository includes a devcontainer in
[`/.devcontainer/devcontainer.json`](https://github.com/fedluc/foga/blob/main/.devcontainer/devcontainer.json).
When opened in a compatible environment, it installs the repository toolchain,
GitHub CLI, and Codex:

- Python 3.11
- `uv`
- `foga` in editable mode with the `dev` and `docs` extras, including `ruff`
  and Sphinx
- common C++ tooling dependencies used by package workflows:
  `build-essential`, `clang`, `cmake`, `ninja-build`, `pkg-config`, and `gdb`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex (`@openai/codex`) via `npm`
