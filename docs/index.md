# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, install, deploy,
inspect, and cleanup workflows.

## What foga does

`foga` gives a project one entrypoint for the common tasks that usually end up
split across Makefiles, shell scripts, CI snippets, and README notes:

- build Python packages and C++ artifacts from one config file
- run Python and C++ test workflows through one CLI
- install local packages and external dependencies through one CLI
- switch environment-specific settings with named profiles
- inspect the resolved config before running anything
- keep escape hatches explicit through structured hooks

## Start here

- New to `foga`: read [Getting Started](getting-started.md)
- Defining `foga.yml`: read [Configuration Overview](configuration/index.md)
- Looking for concrete reference configs: read [Examples](examples/index.md)
- Working on this repository: read [Development](development.md)

```{toctree}
:maxdepth: 2
:hidden:

getting-started
configuration/index
cli
examples/index
development
```

## Example projects

The repository includes two kinds of examples:

- [Tutorial examples](examples/tutorials.md): four staged examples that start
  with a pure-Python package and build up to mixed C++/Python workflows with
  tests, linting, and profiles
- [`qupled`](examples/qupled.md): mixed Python/C++ project with C++ CMake
  builds, Python packaging, pytest suites, and profile overrides
- [`pybind11`](examples/pybind11.md): pinned containerized example that runs
  `foga` against an upstream repository inside Docker

## Install

Install `foga` as a normal user with:

```bash
pip install foga
```
