# devkit

`devkit` is a Python package and CLI for developers maintaining Python packages
with native C or C++ bindings. It centralizes build, test, deploy, and cleanup
workflows behind a single YAML configuration file.

## Status

This repository contains the first implementation pass with:

- YAML configuration via `devkit.yml`
- Profile-based overrides
- Built-in adapters for CMake, `python -m build`, `pytest`, `tox`, `ctest`, and
  Twine uploads
- CLI commands for `build`, `test`, `deploy`, `clean`, and `validate`

## Quick Start

1. Install the package in editable mode:

```bash
pip install -e .[dev]
```

2. Lint the code during development:

```bash
ruff check .
```

3. Add a `devkit.yml` file to your project.

4. Run commands such as:

```bash
devkit validate
devkit build --profile mpi
devkit test --runner unit
devkit deploy --profile release --dry-run
```

See [`examples/qupled/devkit.yml`](examples/qupled/devkit.yml) for a concrete
configuration derived from the current `qupled` workflow.

## Override Precedence

`devkit` applies configuration in this order:

1. Base `devkit.yml`
2. Selected profile overrides from `profiles.<name>`
3. CLI overrides for the active command

Current CLI overrides are execution-scoped rather than persistent config
rewrites: `build --target` overrides configured native build targets for that
invocation, while `test --runner` and `deploy --target` narrow the selected
configured workflows after profile application.

Profile overrides are validated before merge. They may override existing values
and extend nested mappings, but they must preserve container shape for existing
paths and cannot change the backend identifier of an already configured build,
test, or deploy entry.

## Devcontainer

The repository includes a devcontainer in [`.devcontainer/devcontainer.json`](/Users/flufsr/Documents/devkit/.devcontainer/devcontainer.json).
When opened in a compatible environment, it installs:

- Python 3.11
- `devkit` in editable mode with the `dev` extra, including `ruff`
- common native-tooling dependencies used by package workflows:
  `build-essential`, `clang`, `cmake`, `ninja-build`, `pkg-config`, and `gdb`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex via `npm`
