<p align="center">
  <img src="https://raw.githubusercontent.com/fedluc/foga/main/assets/foga.svg" alt="foga" width="400">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Linux-documented%20%7C%20CI-2ea44f" alt="Linux documented and exercised in CI">
  <img src="https://img.shields.io/badge/macOS-documented-2ea44f" alt="macOS documented">
  <a href="https://github.com/fedluc/foga/actions/workflows/ci.yml">
    <img src="https://github.com/fedluc/foga/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/fedluc/foga/actions/workflows/docs.yml">
    <img src="https://github.com/fedluc/foga/actions/workflows/docs.yml/badge.svg" alt="Docs">
  </a>
  <a href="https://pypi.org/project/foga/">
    <img src="https://img.shields.io/pypi/v/foga" alt="PyPI version">
  </a>
</p>

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. These repositories often accumulate shell scripts, Make
targets, CI snippets, and project notes for each workflow. `foga` centralizes
that workflow definition in one `foga.yml` file and exposes it through one CLI.

## Install

```bash
pip install foga
```

## Quick start

Start from one of the examples if you want a working baseline quickly. The
[tutorial examples](examples/tutorial/README.md) are the best starting point
for new users, and the larger reference examples show how `foga` looks in more
realistic repositories.

For reference, a minimal `foga.yml` for a project called `demo` that contains
both python and C++ code can look like this:

```yaml
project:
  name: demo

build:
  python:
    backend: python-build
  cpp:
      backend: cmake
      source_dir: cpp
      build_dir: build-cpp

test:
  runners:
    unit:
      backend: pytest
      path: tests
```

After you have created `foga.yml`, validate before you run anything
for real:

```bash
foga validate
foga build --dry-run
foga build cpp --dry-run
foga test --dry-run
```

## Documentation

Full documentation with examples available at <https://fedluc.github.io/foga/>
