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
   `tox -e <env>` becomes `tox`, and `cmake` or `ctest` become native
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

Install the project in editable mode with development dependencies:

```bash
pip install -e .[dev,docs]
```

Standard verification:

```bash
ruff check .
pytest
python -m build
sphinx-build -W --keep-going -b html docs docs/_build/html
```

## Devcontainer

The repository includes a devcontainer in
[`/.devcontainer/devcontainer.json`](https://github.com/fedluc/foga/blob/main/.devcontainer/devcontainer.json).
When opened in a compatible environment, it installs:

- Python 3.11
- `foga` in editable mode with the `dev` extra, including `ruff`
- common native-tooling dependencies used by package workflows:
  `build-essential`, `clang`, `cmake`, `ninja-build`, `pkg-config`, and `gdb`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex via `npm`
