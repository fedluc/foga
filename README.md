# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with native C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, deploy, inspect, and
cleanup workflows.

## What foga does

`foga` gives a project one entrypoint for the common tasks that usually end up
split across Makefiles, shell scripts, CI snippets, and README notes:

- build Python packages and native artifacts from one config file
- run Python and native test workflows through one CLI
- switch environment-specific settings with named profiles
- inspect the resolved config before running anything
- keep escape hatches explicit through structured hooks

The repository includes a full example in
[`examples/qupled/foga.yml`](examples/qupled/foga.yml).

## Installation

Install `foga` as a normal user with:

```bash
pip install foga
```

## Quick Start

1. Add a root-level `foga.yml` file to your project.
2. Start with a minimal configuration.
3. Validate it.
4. Inspect the resolved config.
5. Run build or test workflows.

Minimal example:

```yaml
project:
  name: demo

build:
  python:
    backend: python-build

test:
  runners:
    unit:
      backend: pytest
      path: tests
```

Typical commands:

These examples use the bundled repository example config so they can be run
from this repository root as written. They focus on validation, inspection, and
dry-run output because the bundled config is a documentation fixture rather than
a full standalone project:

```bash
foga --config examples/qupled/foga.yml validate                  # Check that the example config is well-formed
foga --config examples/qupled/foga.yml inspect                   # Print the resolved example configuration
foga --config examples/qupled/foga.yml build --dry-run           # Show planned build commands without executing
foga --config examples/qupled/foga.yml test --dry-run            # Show planned test commands without executing
foga --config examples/qupled/foga.yml deploy --target pypi --dry-run # Preview the example deploy command
```

## End-To-End Workflow

The usual workflow for adopting `foga` in a repository is:

1. Create `foga.yml` with your project name and at least one build or test
   workflow.
2. Run `foga validate` until the configuration passes.
3. Run `foga inspect` to check the merged effective config.
4. Use `foga build --dry-run`, `foga test --dry-run`, or
   `foga deploy --dry-run` to inspect generated commands before execution.
5. Run the real command once the plan looks right.
6. Add profiles only after the base config is working.

That sequence keeps adoption incremental. You do not need to encode every
project script on day one.

## Configuration Layout

`foga` expects a root-level YAML mapping. The main top-level sections are:

- `project`: required project metadata
- `build`: optional build workflows
- `test`: optional test workflows
- `deploy`: optional deployment workflows
- `clean`: optional cleanup targets
- `profiles`: optional named overrides applied on top of the base config

Example shape:

```yaml
project:
  name: demo

build:
  default: all
  native:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build

test:
  default: python
  runners:
    unit:
      backend: pytest
      path: tests

deploy:
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]

clean:
  paths: ["build", "dist"]

profiles:
  release:
    build:
      python:
        args: ["--wheel"]
```

### Project

`project.name` is required and identifies the configured project in validation
output.

### Build

`build` defines up to two workflow kinds:

- `build.native` for native build tooling
- `build.python` for Python package builds

`build.default` may be `native`, `python`, or `all`.

When `build.default` is omitted, `foga build` runs all configured build kinds
for backward compatibility.

`build` itself is optional, but `foga build` only does useful work when at
least one build workflow is configured.

### Test

`test.runners` is a mapping keyed by runner name. Each runner chooses a backend
such as `pytest`, `tox`, or `ctest`.

`test.default` may be `native`, `python`, or `all`.

`test` is optional, but `test.runners` is the important nested section when you
want `foga test` to run anything.

### Deploy

`deploy.targets` is a mapping keyed by target name. Each target currently uses
the `twine` backend to upload matched artifacts.

`deploy` is optional. Configure it only if you want `foga deploy`.

### Clean

`clean.paths` is a simple list of repository-relative paths that `foga clean`
removes.

`clean` is optional.

## Supported Backends

### Build backends

#### `cmake`

`build.native.backend: cmake` generates a configure step and one or more
`cmake --build` steps. Its fields mean:

- `source_dir`: source tree passed to `cmake -S`
- `build_dir`: build tree passed to `cmake -B` and reused for `cmake --build`
- `generator`: optional generator name such as `Ninja`
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the build step
- `targets`: default native targets to build when the CLI does not override them
- `env`: environment variables added to the generated commands
- `hooks`: pre/post commands run around the native workflow

#### `python-build`

`build.python.backend: python-build` runs `python3 -m build` with optional
extra `args`, plus optional `env` and `hooks`.

`foga` intentionally does not allow overriding the full build command for this
backend. Use `args` for extra flags.

Its fields mean:

- `args`: extra flags appended to `python3 -m build`
- `env`: environment variables added to the build command
- `hooks`: pre/post commands run around the Python package build

### Test backends

#### `pytest`

This backend runs `pytest`. Its fields mean:

- `path`: test path passed to `pytest`; this is required for the `pytest` backend
- `marker`: optional `pytest -m` selector
- `args`: extra flags appended after the base pytest command
- `env`: environment variables added to the runner command
- `hooks`: pre/post commands run around the runner

#### `tox`

This backend runs `tox -e <env>`. Its fields mean:

- `tox_env`: environment name passed to `tox -e`; this is required for the
  `tox` backend
- `args`: extra flags appended after `tox -e <env>`
- `env`: environment variables added to the runner command
- `hooks`: pre/post commands run around the runner

#### `ctest`

This backend can configure and build native tests before running `ctest`. Its
fields mean:

- `build_dir`: build tree used by `ctest --test-dir`; this is required
- `source_dir`: optional source tree; when present, `foga` also runs a CMake
  configure step before testing
- `generator`: optional generator name for the configure step
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the native build step
- `target`: optional build target compiled before tests run
- `args`: extra flags appended to the final `ctest` command
- `env`: environment variables added to generated commands
- `hooks`: pre/post commands run around the native test workflow

### Deploy backends

#### `twine`

This backend runs `twine upload`. Its fields mean:

- `artifacts`: glob patterns resolved relative to the project root; this is
  required and must match built package files
- `repository`: optional Twine repository name passed as `--repository`
- `repository_url`: optional explicit upload URL passed as `--repository-url`
- `args`: extra flags appended before artifact paths
- `env`: environment variables added to the upload command
- `hooks`: pre/post commands run around the upload step

## Profiles

Profiles let one repository express environment-specific differences without
copying the entire config. Apply them with `--profile <name>`.

Example:

```yaml
profiles:
  mpi:
    build:
      native:
        configure_args:
          - -DBUILD_NATIVE_TESTS=OFF
          - -DUSE_MPI=ON
      python:
        env:
          USE_MPI: "ON"
```

Use profiles for:

- CI versus local development
- MPI versus non-MPI builds
- platform-specific environment variables
- release-only deployment settings

Profile merge rules are intentionally conservative:

- profile overrides may replace values and extend nested mappings
- they must preserve the container type of existing paths
- they cannot change the backend identifier of an already configured workflow

## Hooks And Escape Hatches

Hooks are the supported escape hatch when a workflow needs a small amount of
custom orchestration around a built-in backend command.

Hook shape:

```yaml
test:
  runners:
    integration:
      backend: pytest
      path: tests
      hooks:
        pre:
          - ["python3", "tools/prepare_integration.py"]
        post:
          - ["python3", "tools/cleanup_integration.py"]
```

Supported behavior:

- only `hooks.pre` and `hooks.post` are supported
- each hook entry must be a non-empty command array
- hooks run directly without shell parsing
- hooks execute around the generated backend command

Intentionally unsupported:

- shell strings such as `"make build && make test"`
- per-hook mappings such as `cwd`, `shell`, `argv`, or inline `env`
- turning the config file into a generic task runner

If logic is complex, keep it in a project script and call that script from a
hook.

## Command Guide

### Validate

Use `foga validate` to catch malformed config early:

```bash
foga --config examples/qupled/foga.yml validate   # Validate the bundled example config
foga --config path/to/foga.yml validate           # Validate a specific config file
```

This is the first command to run after editing the configuration.

### Build

Use `foga build` to run configured build workflows:

```bash
foga --config examples/qupled/foga.yml build --dry-run                    # Preview all configured build workflows
foga --config examples/qupled/foga.yml build python --dry-run             # Preview only the Python package build
foga --config examples/qupled/foga.yml build native --target native_tests --dry-run # Preview one native target explicitly
foga --config examples/qupled/foga.yml build all --profile mpi --dry-run  # Preview builds with the mpi profile applied
foga --config examples/qupled/foga.yml build --dry-run                    # Print the planned build commands
```

### Test

Use `foga test` to run one or more configured test runners:

```bash
foga --config examples/qupled/foga.yml test --dry-run               # Preview all configured test workflows
foga --config examples/qupled/foga.yml test python --runner unit --dry-run # Preview only the Python runner named "unit"
foga --config examples/qupled/foga.yml test native --dry-run        # Preview only native test workflows
foga --config examples/qupled/foga.yml test --profile mpi --dry-run # Preview test commands with the mpi profile
```

### Deploy

Use `foga deploy` to run deployment targets:

```bash
foga --config examples/qupled/foga.yml deploy --target pypi --dry-run # Preview the pypi upload command
```

### Clean

Use `foga clean` to remove configured generated paths:

```bash
foga --config examples/qupled/foga.yml clean   # Remove paths listed in the example config
```

### Inspect

Use `foga inspect` to print the resolved configuration without executing
commands:

```bash
foga --config examples/qupled/foga.yml inspect                                     # Print the full resolved config
foga --config examples/qupled/foga.yml inspect --profile mpi                       # Inspect after applying mpi
foga --config examples/qupled/foga.yml inspect build native --target native_tests  # Inspect native build selection
foga --config examples/qupled/foga.yml inspect test python --runner unit           # Inspect the selected test runner
foga --config examples/qupled/foga.yml inspect deploy --target pypi                # Inspect one deploy target
foga --config examples/qupled/foga.yml inspect --full build native                 # Show the full document for build
```

Top-level `foga inspect` prints the full resolved config. Command-specific
inspection prints a concise summary plus the relevant config fragment unless
`--full` is set.

## Dry-Run Usage

Dry-run mode is the safest way to adopt `foga` in an existing repository.

Available dry-run commands:

- `foga build --dry-run`
- `foga test --dry-run`
- `foga deploy --dry-run`

Dry-run output shows the planned commands without executing them. Use it to
verify:

- the selected profile
- target or runner filtering
- generated backend arguments
- hook ordering
- working assumptions before changing CI or repository scripts

## Override Precedence

`foga` resolves configuration in this order:

1. Base `foga.yml`
2. Selected profile overrides from `profiles.<name>`
3. CLI overrides for the active command

CLI overrides are execution-scoped. They do not rewrite the config file.

Examples:

- `foga build python` changes the build selection for one invocation
- `foga test native` changes the test selection for one invocation
- `foga build --target native_tests` overrides configured native targets
- `foga test --runner unit` narrows the selected runners
- `foga deploy --target pypi` narrows the selected deploy targets

## Migration From Repo-Specific Scripts

Repositories adopting `foga` usually already have shell scripts, Make targets,
or CI snippets for build and test commands. The migration goal is not to delete
everything immediately. Start by moving the stable workflow definition into
`foga.yml`.

Suggested migration path:

1. Inventory the commands your repository already uses for build, test, deploy,
   and cleanup.
2. Map each stable workflow to a built-in backend first:
   `python -m build` -> `python-build`, `pytest` -> `pytest`,
   `tox -e <env>` -> `tox`, `cmake` or `ctest` -> native backends.
3. Keep repo-specific scripts only for logic that is genuinely project-specific.
4. Wrap small prep or cleanup steps with hooks instead of copying full shell
   scripts into YAML.
5. Replace CI shell fragments with `foga` commands once dry-run output and
   local execution are stable.
6. Remove obsolete scripts only after the `foga` workflow is trusted.

Concrete before-and-after examples:

- `scripts/build_wheel.sh` that only runs `python -m build` usually becomes
  `build.python.backend: python-build`
- `scripts/test_unit.sh` that only wraps `pytest tests -m unit -v` usually
  becomes a named `pytest` runner with `path`, `marker`, and `args`
- platform-specific environment setup usually belongs in a profile
- a short docs-copy step around integration tests usually belongs in hooks

Good candidates to keep outside `foga`:

- long project bootstrap flows
- commands that provision external infrastructure
- heavy orchestration that is better expressed in Python or shell than YAML

## Example Config

[`examples/qupled/foga.yml`](examples/qupled/foga.yml) demonstrates:

- both native and Python build workflows
- multiple named test runners
- pre/post hooks for integration tests
- MPI and platform-specific profiles

Use it as a reference when authoring a new config, but keep your own config as
small as possible at first.

## Repository Development

If you are developing this repository itself, install it in editable mode with
the development dependencies:

```bash
pip install -e .[dev]
```

For day-to-day validation of changes in this repository, the standard checks
are:

```bash
ruff check .
pytest
python -m build
```

### Devcontainer

The repository includes a devcontainer in
[`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json). When
opened in a compatible environment, it installs:

- Python 3.11
- `foga` in editable mode with the `dev` extra, including `ruff`
- common native-tooling dependencies used by package workflows:
  `build-essential`, `clang`, `cmake`, `ninja-build`, `pkg-config`, and `gdb`
- GitHub CLI (`gh`) for authenticated GitHub API and repository operations
- Codex via `npm`
