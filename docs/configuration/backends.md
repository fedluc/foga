# Backends

## Build backends

### `cmake`

`build.cpp.backend: cmake` generates a configure step and one or more
`cmake --build` steps. Its fields mean:

- `source_dir`: source tree passed to `cmake -S`
- `build_dir`: build tree passed to `cmake -B` and reused for `cmake --build`
- `generator`: optional generator name such as `Ninja`
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the build step
- `targets`: default C++ targets to build when the CLI does not override
  them
- `env`: environment variables added to the generated commands
- `hooks`: pre/post commands run around the C++ workflow

### `python-build`

`build.python.backend: python-build` runs `python3 -m build` with optional
extra `args`, plus optional `env` and `hooks`.

`foga` intentionally does not allow overriding the full build command for this
backend. Use `args` for extra flags.

Its fields mean:

- `args`: extra flags appended to `python3 -m build`
- `env`: environment variables added to the build command
- `hooks`: pre/post commands run around the Python package build

## Test backends

### `pytest`

This backend runs `pytest`. Its fields mean:

- `path`: test path passed to `pytest`; this is required for the `pytest`
  backend
- `marker`: optional `pytest -m` selector
- `args`: extra flags appended after the base pytest command
- `env`: environment variables added to the runner command
- `hooks`: pre/post commands run around the runner

### `tox`

This backend runs `tox -e <env>`. Its fields mean:

- `tox_env`: environment name passed to `tox -e`; this is required for the
  `tox` backend
- `args`: extra flags appended after `tox -e <env>`
- `env`: environment variables added to the runner command
- `hooks`: pre/post commands run around the runner

### `ctest`

This backend can configure and build C++ tests before running `ctest`. Its
fields mean:

- `build_dir`: build tree used by `ctest --test-dir`; this is required
- `source_dir`: optional source tree; when present, `foga` also runs a CMake
  configure step before testing
- `generator`: optional generator name for the configure step
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the C++ build step
- `target`: optional build target compiled before tests run
- `args`: extra flags appended to the final `ctest` command
- `env`: environment variables added to generated commands
- `hooks`: pre/post commands run around the C++ test workflow

## Deploy backends

### `twine`

This backend runs `twine upload`. Its fields mean:

- `artifacts`: glob patterns resolved relative to the project root; this is
  required and must match built package files
- `repository`: optional Twine repository name passed as `--repository`
- `repository_url`: optional explicit upload URL passed as `--repository-url`
- `args`: extra flags appended before artifact paths
- `env`: environment variables added to the upload command
- `hooks`: pre/post commands run around the upload step
