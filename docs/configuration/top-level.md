# Top-level sections

## `project`

`project.name` is required and identifies the configured project in validation
output.

Example:

```yaml
project:
  name: demo
```

## `build`

`build` defines the C++ and Python build workflows. Use `build.cpp` for native
builds, `build.python` for package builds, and `build.default` when one kind
should be selected by default.

Example:

```yaml
build:
  default: all
  python:
    backend: python-build
```

## `test`

`test.runners` is a mapping keyed by runner name. Each runner chooses a backend
such as `pytest`, `tox`, or `ctest`.

Example:

```yaml
test:
  default_runners: [unit]
  runners:
    unit:
      backend: pytest
      path: tests
```

## `docs`

`docs.targets` is a mapping keyed by target name. Use `docs.default_targets`
when `foga docs` should choose one or more targets automatically.

Example:

```yaml
docs:
  targets:
    site:
      backend: sphinx
      source_dir: docs
      build_dir: docs/_build/html
```

## `format`

`format.targets` declares formatter targets. `format.default` and
`format.default_targets` control what runs when the CLI does not select a
specific kind or target.

Example:

```yaml
format:
  default_targets: [python-style]
  targets:
    python-style:
      backend: ruff-format
      paths: ["src", "tests"]
```

## `lint`

`lint.targets` declares linter targets. `lint.default` and
`lint.default_targets` work the same way as the `format` section.

Example:

```yaml
lint:
  default_targets: [python-style]
  targets:
    python-style:
      backend: ruff-check
      paths: ["src", "tests"]
```

## `install`

`install.targets` declares installation targets for local packages, dependency
sync tools, or system package managers. `install.default_targets` controls what
`foga install` runs by default.

Example:

```yaml
install:
  default_targets: [editable]
  targets:
    editable:
      backend: pip
      path: .
      editable: true
```

## `deploy`

`deploy.targets` declares publish or upload targets. Use
`deploy.default_targets` when `foga deploy` should select a target without an
explicit `--target`.

Example:

```yaml
deploy:
  default_targets: [pypi]
  targets:
    pypi:
      backend: twine
      artifacts: ["dist/*"]
```

## `clean`

`clean.paths` lists repository-relative paths that `foga clean` removes.

Example:

```yaml
clean:
  paths: ["build", "dist"]
```

## `profiles`

`profiles` defines named overrides that apply on top of the base config. Use
them for environment-specific differences without copying the full file.

Example:

```yaml
profiles:
  release:
    build:
      python:
        args: ["--wheel"]
```
