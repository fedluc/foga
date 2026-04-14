# Configuration Overview

`foga` expects a root-level YAML mapping. The main top-level sections are:

- `project`: required project metadata
- `build`: optional build workflows
- `test`: optional test workflows
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
