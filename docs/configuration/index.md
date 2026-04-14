# Configuration Overview

`foga` expects a root-level YAML mapping. The main top-level sections are:

- `project`: required project metadata
- `build`: optional build workflows
- `test`: optional test workflows
- `format`: optional format workflows
- `lint`: optional lint workflows
- `deploy`: optional deployment workflows
- `clean`: optional cleanup targets
- `profiles`: optional named overrides applied on top of the base config

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

test:
  default: python
  runners:
    unit:
      backend: pytest
      path: tests

format:
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]

lint:
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]

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

### `test`

`test.runners` is a mapping keyed by runner name. Each runner chooses a backend
such as `pytest`, `tox`, or `ctest`.

`test.default` may be `cpp`, `python`, or `all`.

`test` is optional, but `test.runners` is the important nested section when you
want `foga test` to run anything.

### `deploy`

`deploy.targets` is a mapping keyed by target name. Each target currently uses
the `twine` backend to upload matched artifacts.

`deploy` is optional. Configure it only if you want `foga deploy`.

### `format`

`format.targets` is a mapping keyed by target name. Each target chooses a
backend such as `ruff-format`, `black`, or `clang-format`.

`format.default` may be `cpp`, `python`, or `all`.

`format` is optional, but `format.targets` is the important nested section when
you want `foga format` to run anything.

### `lint`

`lint.targets` is a mapping keyed by target name. Each target chooses a backend
such as `ruff-check` or `clang-tidy`.

`lint.default` may be `cpp`, `python`, or `all`.

`lint` is optional, but `lint.targets` is the important nested section when you
want `foga lint` to run anything.

### `clean`

`clean.paths` is a simple list of repository-relative paths that `foga clean`
removes.

`clean` is optional.

```{toctree}
:maxdepth: 1
:hidden:

backends
profiles-and-hooks
```
