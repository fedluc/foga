# Development

This page is for contributors working on `foga` itself. It covers the local
development environment, routine verification commands, packaging checks,
documentation builds, and the optional devcontainer.

## Set up the environment

Install `uv` first if it is not already available in your shell, then sync the
repository environment with the extras used for development and documentation:

```bash
uv sync --extra dev --extra docs
```

When dependency metadata changes, refresh the committed lockfile:

```bash
uv lock
```

## Run checks while developing

Run the fast checks first while iterating on code:

```bash
uv run ruff check .
uv run pytest
```

When you change documentation, build the docs with warnings treated as errors:

```bash
uv run sphinx-build -W --keep-going -b html docs docs/_build/html
```

Before release-oriented changes, build the source and wheel distributions:

```bash
uv run python -m build
```

## Devcontainer

The repository includes a devcontainer for contributors who want the full
development toolchain without installing system packages locally. Open the
repository in a compatible environment and the post-create setup will install
the toolchain and sync the project with the `dev` and `docs` extras.

The devcontainer is defined in
[`/.devcontainer/devcontainer.json`](https://github.com/fedluc/foga/blob/main/.devcontainer/devcontainer.json)
and installs:

- Python 3.12
- `uv`
- `foga` in editable mode with the `dev` and `docs` extras
- common C++ tooling dependencies used by package workflows:
  `build-essential`, `bubblewrap`, `clang`, `cmake`, `gdb`, `ninja-build`, and
  `pkg-config`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex (`@openai/codex`) via `npm`
