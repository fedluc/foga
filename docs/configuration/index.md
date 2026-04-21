# Configuration Overview

`foga` expects a root-level YAML mapping with these top-level sections.

Use this page to find the top-level structure and the role of each section.
Use [Backends](backends.md) for exact backend fields and
[Profiles And Hooks](profiles-and-hooks.md) for override and escape-hatch
behavior.

Required sections:

- `project`: project metadata

Optional sections:

- `build`: build workflows
- `test`: test workflows
- `docs`: docs workflows
- `format`: format workflows
- `lint`: lint workflows
- `install`: installation workflows
- `deploy`: deployment workflows
- `clean`: cleanup targets
- `profiles`: named overrides applied on top of the base config

## Example shape

```yaml
project:
  name: demo

build:
  default: all
  cpp:
    backend: cmake
    source_dir: cpp
    build_dir: build
  python:
    backend: python-build
    launcher: ["uv", "run"]

test:
  default: python
  default_runners: [unit]
  runners:
    unit:
      backend: pytest
      path: tests

docs:
  default_targets: [python-api]
  targets:
    python-api:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html

format:
  default_targets: [python-style]
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]

lint:
  default_targets: [python-style]
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]

install:
  default_targets: [editable]
  targets:
    editable:
      backend: pip
      path: .
      editable: true

deploy:
  default_targets: [pypi]
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

## How to read this reference

- Search this page by top-level section name such as `build`, `test`, or
  `install` when you need the container shape.
- Search [Backends](backends.md) by backend name such as `pytest`, `cmake`,
  `pip`, or `twine` when you need the exact configurable fields.
- Search [Profiles And Hooks](profiles-and-hooks.md) when you need override
  rules, hook behavior, or the boundary between built-in workflows and custom
  scripts.

## Top-level sections

### `project`

`project.name` is required and identifies the configured project in validation
output.

### `build`

`build` defines up to two workflow kinds:

- `build.cpp` for C++ build tooling
- `build.python` for Python package builds

`build.default` may be `cpp`, `python`, or `all`.

When `build.default` is omitted, `foga build` runs all configured build kinds
for backward compatibility.

`build` itself is optional, but `foga build` only does useful work when at
least one build workflow is configured.

Backend-backed entries may also set `launcher` to prepend a command prefix such
as `["uv", "run"]` or `["pipx", "run"]`.

### `test`

`test.runners` is a mapping keyed by runner name. Each runner chooses a backend
such as `pytest`, `tox`, or `ctest`.

`test.default` may be `cpp`, `python`, or `all`.

`test.default_runners` may list one or more configured runner names. `foga`
uses them only when `--runner` is omitted, after resolving the active test
kind.

`test` is optional, but `test.runners` is the important nested section when you
want `foga test` to run anything.

Each runner may also set `launcher` to prepend a command prefix.

### `docs`

`docs.targets` is a mapping keyed by target name. Each target chooses a backend
such as `sphinx`, `mkdocs`, or `doxygen`.

`docs` is optional, but `docs.targets` is the important nested section when you
want `foga docs` to run anything.

`docs.default_targets` may list one or more configured target names. `foga`
uses them only when `--target` is omitted.

Each docs target may also set `launcher` to prepend a command prefix.

### `format`

`format.targets` is a mapping keyed by target name. Each target chooses a
backend such as `ruff-format`, `black`, or `clang-format`.

`format.default` may be `cpp`, `python`, or `all`.

`format.default_targets` may list one or more configured target names. When
`format.default` is also set, each default target must belong to that kind.

`format` is optional, but `format.targets` is the important nested section when
you want `foga format` to run anything.

Each format target may also set `launcher` to prepend a command prefix.

### `lint`

`lint.targets` is a mapping keyed by target name. Each target chooses a backend
such as `ruff-check`, `pylint`, or `clang-tidy`.

`lint.default` may be `cpp`, `python`, or `all`.

`lint.default_targets` may list one or more configured target names. When
`lint.default` is also set, each default target must belong to that kind.

`lint` is optional, but `lint.targets` is the important nested section when you
want `foga lint` to run anything.

Each lint target may also set `launcher` to prepend a command prefix.

### `install`

`install.targets` is a mapping keyed by target name. Each target chooses a
backend such as `pip`, `uv`, `poetry`, `npm`, `apt-get`, `brew`, or `yum`.

`install` is optional, but `install.targets` is the important nested section
when you want `foga install` to run anything.

`install.default_targets` may list one or more configured target names. `foga`
uses them only when `--target` is omitted.

Each install target may also set `launcher` to prepend a command prefix. This
is the intended way to add `sudo` or a container runner for system package
installers.

### `deploy`

`deploy.targets` is a mapping keyed by target name. Each target currently uses
the `twine` backend to upload matched artifacts.

`deploy` is optional. Configure it only if you want `foga deploy`.

`deploy.default_targets` may list one or more configured target names. `foga`
uses them only when `--target` is omitted.

Each deploy target may also set `launcher` to prepend a command prefix.

### `clean`

`clean.paths` is a simple list of repository-relative paths that `foga clean`
removes.

`clean` is optional.

## Reference map

- [Backends](backends.md): exact fields for every supported backend
- [Profiles And Hooks](profiles-and-hooks.md): profile merge behavior and hook
  constraints
- [CLI Reference](../cli.md): command-line selection, dry-run, and inspect
  behavior

```{toctree}
:maxdepth: 1
:hidden:

backends
profiles-and-hooks
```
