# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with native C or C++ bindings. It centralizes build, test, deploy, and cleanup
workflows behind a single YAML configuration file.

## Status

This repository contains the first implementation pass with:

- YAML configuration via `foga.yml`
- Profile-based overrides
- Built-in adapters for CMake, `python -m build`, `pytest`, `tox`, `ctest`, and
  Twine uploads
- CLI commands for `build`, `test`, `deploy`, `clean`, `validate`, and
  `inspect`

## Quick Start

1. Install the package in editable mode:

```bash
pip install -e .[dev]
```

2. Lint the code during development:

```bash
ruff check .
```

3. Add a `foga.yml` file to your project.

4. Run commands such as:

```bash
foga validate
foga inspect --profile mpi
foga inspect build native --target native_tests
foga inspect build --full native --target native_tests
foga build python
foga build all --profile mpi
foga test native
foga test python --runner unit
foga deploy --profile release --dry-run
```

See [`examples/qupled/foga.yml`](examples/qupled/foga.yml) for a concrete
configuration derived from the current `qupled` workflow.

## Hooks And Escape Hatches

`foga` supports command hooks as a narrow escape hatch around built-in
workflows. Hooks are intentionally limited: each hook entry must be a command
array, and `foga` executes that array directly without shell parsing.

```yaml
build:
  python:
    backend: python-build
    hooks:
      pre:
        - ["python3", "tools/prepare_build.py"]
      post:
        - ["python3", "tools/cleanup_build.py"]
```

Supported boundaries:

- `hooks.pre` and `hooks.post` are the only supported hook phases
- each hook command must be expressed as `["tool", "arg"]`
- hooks run before or after the generated workflow command for that backend

Intentionally unsupported:

- raw shell strings such as `make build && make test`
- per-hook mappings such as `argv`, `shell`, `cwd`, or inline environment overrides

If a workflow needs complex orchestration, keep that logic in a project script
or tool and call it from a structured hook command instead of embedding shell
logic into `foga.yml`.

## Override Precedence

`foga` applies configuration in this order:

1. Base `foga.yml`
2. Selected profile overrides from `profiles.<name>`
3. CLI overrides for the active command

Current CLI overrides are execution-scoped rather than persistent config
rewrites: `build python|native|all` and `test python|native|all` select the
workflow kind for that invocation, `build --target` overrides configured native
build targets, while `test --runner` and `deploy --target` narrow the selected
configured workflows after profile application.

You can also define defaults in configuration:

```yaml
build:
  default: python
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build

test:
  default: native
  runners:
    unit:
      backend: pytest
      path: tests
    native-cpp:
      backend: ctest
      build_dir: build/tests
```

When omitted, `foga build` and `foga test` still run all configured
workflows for backward compatibility.

Profile overrides are validated before merge. They may override existing values
and extend nested mappings, but they must preserve container shape for existing
paths and cannot change the backend identifier of an already configured build,
test, or deploy entry.

## Inspecting Resolved Configuration

Use `foga inspect` to print the effective YAML configuration after profile
selection, without executing any workflow:

```bash
foga inspect
foga inspect --profile mpi
foga inspect build native --target native_tests
foga inspect build --full native --target native_tests
foga inspect test python --runner unit
foga inspect deploy --target pypi
```

Top-level `foga inspect` still prints the full resolved configuration. The
command-specific variants default to a concise summary plus the relevant config
fragment for the selected build, test, or deploy scope. Add `--full` to any
command-specific inspect invocation to print the full resolved configuration
document instead.

The concise command-specific output includes:

- `active_profile` to show which profile was applied, if any
- `summary` to show the active inspect mode with direct fields such as
  `selection`, `targets`, or `runners`
- `effective_config` to show only the relevant config fragment for the selected
  build, test, or deploy scope

When run in an interactive terminal, inspect output is colorized for easier
scanning. Non-interactive output stays plain YAML so it remains easy to pipe or
parse.

With `--full`, the output includes:

- `context` to show the active inspect mode and selected runners or targets
- `resolved_config` to show the merged configuration document, including active
  build target overrides when provided to `inspect build`

## Devcontainer

The repository includes a devcontainer in [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).
When opened in a compatible environment, it installs:

- Python 3.11
- `foga` in editable mode with the `dev` extra, including `ruff`
- common native-tooling dependencies used by package workflows:
  `build-essential`, `clang`, `cmake`, `ninja-build`, `pkg-config`, and `gdb`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex via `npm`
