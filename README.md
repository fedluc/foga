<p align="center">
  <img src="https://raw.githubusercontent.com/fedluc/foga/main/assets/foga.svg" alt="foga" width="400">
</p>

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, docs, format, lint,
install, deploy, inspect, and cleanup workflows.

## What foga does

- build Python packages and C++ artifacts from one config file
- run Python and C++ test workflows through one CLI
- run Python and C++ format and lint workflows through one CLI
- generate Python and C++ documentation through one CLI
- install local packages and external dependencies through one CLI
- switch environment-specific settings with named profiles
- inspect the resolved config and planned commands before running anything
- keep escape hatches explicit through structured hooks

## Install

```bash
pip install foga
```

## Minimal example

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

## Quick start

```bash
foga validate
foga inspect
foga build --dry-run
foga test --dry-run
foga docs --dry-run
foga format --dry-run
foga lint --dry-run
foga install --dry-run
foga deploy --target pypi --dry-run
```

Python lint targets can use `ruff-check` or `pylint`, and C++ lint targets can
use `clang-tidy`.

## Documentation

- Docs site: <https://fedluc.github.io/foga/>
- Docs source: [`docs/`](docs/)
- Example configs: [`examples/`](examples/)

Start with:

- [Getting Started](docs/getting-started.md)
- [Configuration Overview](docs/configuration/index.md)
- [CLI Reference](docs/cli.md)
- [Examples](docs/examples/index.md)
