# Development

## Repository workflow

Repositories adopting `foga` usually already have shell scripts, Make targets,
or CI snippets for build and test commands. The migration goal is not to delete
everything immediately. Start by moving the stable workflow definition into
`foga.yml`.

Suggested migration path:

1. Inventory the commands your repository already uses for build, test, deploy,
   and cleanup.
2. Map each stable workflow to a built-in backend first:
   `python -m build` becomes `python-build`, `pytest` becomes `pytest`,
   `tox -e <env>` becomes `tox`, and `cmake` or `ctest` become C++
   backends.
3. Keep repo-specific scripts only for logic that is genuinely project-specific.
4. Wrap small prep or cleanup steps with hooks instead of copying full shell
   scripts into YAML.
5. Replace CI shell fragments with `foga` commands once dry-run output and
   local execution are stable.
6. Remove obsolete scripts only after the `foga` workflow is trusted.

Good candidates to keep outside `foga`:

- long project bootstrap flows
- commands that provision external infrastructure
- heavy orchestration that is better expressed in Python or shell than YAML

## Working on this repository

Install `uv` first if it is not already available in your shell, then sync the
repository environment with the extras used in development and documentation:

```bash
uv sync --extra dev --extra docs
```

Standard verification:

```bash
uv run ruff check .
uv run pytest
uv run python -m build
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
