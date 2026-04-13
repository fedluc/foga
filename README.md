<p align="center">
  <img src="assets/foga.svg" alt="foga" width="280">
</p>

# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with native C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, deploy, inspect, and
cleanup workflows.

## What foga does

- build Python packages and native artifacts from one config file
- run Python and native test workflows through one CLI
- switch environment-specific settings with named profiles
- inspect the resolved config before running anything
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
foga deploy --target pypi --dry-run
```

## Documentation

- Docs site: <https://fedluc.github.io/foga/>
- Docs source: [`docs/`](docs/)
- Example configs: [`examples/`](examples/)

Start with:

- [Getting Started](docs/getting-started.md)
- [Configuration Overview](docs/configuration/index.md)
- [CLI Reference](docs/cli.md)
- [Examples](docs/examples/index.md)

## Development

```bash
pip install -e .[dev,docs]
ruff check .
pytest
python -m build
sphinx-build -W --keep-going -b html docs docs/_build/html
```
