# Backends

Every backend-backed workflow entry also accepts an optional `launcher` field.
`launcher` must be a non-empty command array such as `["uv", "run"]` or
`["pipx", "run"]`. `foga` prepends that launcher to each generated backend
command for the configured entry.

## Build backends

### `cmake`

`build.cpp.backend: cmake` generates a configure step and one or more
`cmake --build` steps. Its fields mean:

- `source_dir`: source tree passed to `cmake -S`
- `build_dir`: build tree passed to `cmake -B` and reused for `cmake --build`
- `generator`: optional generator name such as `Ninja`
- `launcher`: optional command prefix prepended to configure and build steps
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the build step
- `targets`: default C++ targets to build when the CLI does not override
  them
- `env`: environment variables added to the generated commands
- `hooks`: pre/post commands run around the C++ workflow

### `meson`

`build.cpp.backend: meson` generates a `meson setup` step and one or more
`meson compile` steps. Its fields mean:

- `command`: optional Meson command array, defaulting to `["meson"]`
- `source_dir`: source tree passed to `meson setup`
- `build_dir`: build tree passed to `meson setup` and reused for
  `meson compile -C`
- `launcher`: optional command prefix prepended to setup and compile steps
- `setup_args`: extra flags appended to the setup step
- `compile_args`: extra flags appended to the compile step
- `targets`: default C++ targets to compile when the CLI does not override
  them
- `env`: environment variables added to the generated commands
- `hooks`: pre/post commands run around the C++ workflow

### `python-build`

`build.python.backend: python-build` runs `python3 -m build` with optional
extra `args`, plus optional `env` and `hooks`.

`foga` intentionally does not allow overriding the full build command for this
backend. Use `args` for extra flags.

Its fields mean:

- `launcher`: optional command prefix prepended to the build command
- `args`: extra flags appended to `python3 -m build`
- `env`: environment variables added to the build command
- `hooks`: pre/post commands run around the Python package build

## Test backends

### `pytest`

This backend runs `pytest`. Its fields mean:

- `path`: test path passed to `pytest`; this is required for the `pytest`
  backend
- `marker`: optional `pytest -m` selector
- `launcher`: optional command prefix prepended to the runner command
- `args`: extra flags appended after the base pytest command
- `env`: environment variables added to the runner command
- `hooks`: pre/post commands run around the runner

### `tox`

This backend runs `tox -e <env>`. Its fields mean:

- `tox_env`: environment name passed to `tox -e`; this is required for the
  `tox` backend
- `launcher`: optional command prefix prepended to the runner command
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
- `launcher`: optional command prefix prepended to configure, build, and test
  steps
- `configure_args`: extra flags appended to the configure step
- `build_args`: extra flags appended to the C++ build step
- `target`: optional build target compiled before tests run
- `args`: extra flags appended to the final `ctest` command
- `env`: environment variables added to generated commands
- `hooks`: pre/post commands run around the C++ test workflow

## Docs backends

### `sphinx`

`docs.targets.<name>.backend: sphinx` runs `sphinx-build`. Its fields mean:

- `source_dir`: source tree passed to `sphinx-build`; this is required
- `build_dir`: output tree passed to `sphinx-build`; this is required
- `builder`: optional Sphinx builder name such as `html` or `dirhtml`
- `launcher`: optional command prefix prepended to the docs command
- `args`: extra flags appended after the positional arguments
- `env`: environment variables added to the docs command
- `hooks`: pre/post commands run around the docs workflow

### `mkdocs`

`docs.targets.<name>.backend: mkdocs` runs `mkdocs build`. Its fields mean:

- `config_file`: MkDocs config file passed as `--config-file`; this is required
- `build_dir`: optional site output directory passed as `--site-dir`
- `launcher`: optional command prefix prepended to the docs command
- `args`: extra flags appended after the base command
- `env`: environment variables added to the docs command
- `hooks`: pre/post commands run around the docs workflow

### `doxygen`

`docs.targets.<name>.backend: doxygen` runs `doxygen`. Its fields mean:

- `config_file`: Doxygen config file passed to `doxygen`; this is required
- `launcher`: optional command prefix prepended to the docs command
- `args`: extra flags appended after the config file
- `env`: environment variables added to the docs command
- `hooks`: pre/post commands run around the docs workflow

## Format backends

### `black`

`format.targets.<name>.backend: black` runs `black` on the configured paths.
Its fields mean:

- `paths`: literal paths or glob patterns resolved before `black` runs; this is required
- `launcher`: optional command prefix prepended to the formatter command
- `args`: extra flags appended before the paths
- `env`: environment variables added to the formatter command
- `hooks`: pre/post commands run around the formatter

### `ruff-format`

`format.targets.<name>.backend: ruff-format` runs `ruff format` on the
configured paths. Its fields mean:

- `paths`: literal paths or glob patterns resolved before `ruff format` runs; this is required
- `launcher`: optional command prefix prepended to the formatter command
- `args`: extra flags appended before the paths
- `env`: environment variables added to the formatter command
- `hooks`: pre/post commands run around the formatter

### `clang-format`

`format.targets.<name>.backend: clang-format` runs `clang-format -i` on the
configured paths. Its fields mean:

- `paths`: literal paths or glob patterns resolved before `clang-format` runs; this is required
- `launcher`: optional command prefix prepended to the formatter command
- `args`: extra flags appended after `-i` and before the paths
- `env`: environment variables added to the formatter command
- `hooks`: pre/post commands run around the formatter

## Lint backends

### `ruff-check`

`lint.targets.<name>.backend: ruff-check` runs `ruff check` on the configured
paths. Its fields mean:

- `paths`: paths passed to `ruff check`; this is required
- `launcher`: optional command prefix prepended to the lint command
- `args`: extra flags appended before the paths
- `env`: environment variables added to the lint command
- `hooks`: pre/post commands run around the linter

### `pylint`

`lint.targets.<name>.backend: pylint` runs `pylint` on the configured paths.
Its fields mean:

- `paths`: paths passed to `pylint`; this is required
- `launcher`: optional command prefix prepended to the lint command
- `args`: extra flags appended before the paths
- `env`: environment variables added to the lint command
- `hooks`: pre/post commands run around the linter

### `clang-tidy`

`lint.targets.<name>.backend: clang-tidy` runs `clang-tidy` on the configured
paths. Its fields mean:

- `paths`: paths passed to `clang-tidy`; this is required
- `launcher`: optional command prefix prepended to the lint command
- `args`: extra flags appended before the paths
- `env`: environment variables added to the lint command
- `hooks`: pre/post commands run around the linter

## Install backends

### `pip`

`install.targets.<name>.backend: pip` runs `python3 -m pip install`. Its fields
mean:

- `path`: optional local path to install, commonly `.`
- `packages`: optional package names or specifiers appended after the command
- `editable`: optional boolean that adds `-e`; requires `path`
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended before packages or paths
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

### `uv`

`install.targets.<name>.backend: uv` runs `uv sync` for uv-managed projects.

Its fields mean:

- `groups`: optional dependency groups passed as repeated `--group` flags
- `extras`: optional extras passed as repeated `--extra` flags
- `install_project`: optional boolean that controls whether the local project is
  installed; `false` adds `--no-install-project`
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended after `uv sync`
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

The `uv` backend only supports project sync options. `path`, `packages`, and
`editable` are not supported.

Example:

```yaml
install:
  targets:
    dev-python:
      backend: uv
      groups: ["dev"]
      extras: ["test", "docs"]
      install_project: false
```

### `poetry`

`install.targets.<name>.backend: poetry` runs `poetry install`.

- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended after `poetry install`
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

`poetry` does not use `path`, `packages`, or `editable`.

### `npm`

`install.targets.<name>.backend: npm` runs `npm install`.

- `packages`: optional package names appended after `npm install`
- `path`: optional local package path appended after the command
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended before packages or paths
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

### `apt-get`

`install.targets.<name>.backend: apt-get` runs `apt-get install`.

- `packages`: package names passed to `apt-get install`; this is required
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended before packages, such as `-y`
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

### `brew`

`install.targets.<name>.backend: brew` runs `brew install`.

- `packages`: package names passed to `brew install`; this is required
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended before packages
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

### `yum`

`install.targets.<name>.backend: yum` runs `yum install`.

- `packages`: package names passed to `yum install`; this is required
- `launcher`: optional command prefix prepended to the install command
- `args`: extra flags appended before packages
- `env`: environment variables added to the install command
- `hooks`: pre/post commands run around the install target

## Deploy backends

### `twine`

This backend runs `twine upload`. Its fields mean:

- `artifacts`: glob patterns resolved relative to the project root; this is
  required and must match built package files
- `repository`: optional Twine repository name passed as `--repository`
- `repository_url`: optional explicit upload URL passed as `--repository-url`
- `launcher`: optional command prefix prepended to the upload command
- `args`: extra flags appended before artifact paths
- `env`: environment variables added to the upload command
- `hooks`: pre/post commands run around the upload step
