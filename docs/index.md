# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with native C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, deploy, inspect, and
cleanup workflows.

## What foga does

`foga` gives a project one entrypoint for the common tasks that usually end up
split across Makefiles, shell scripts, CI snippets, and README notes:

- build Python packages and native artifacts from one config file
- run Python and native test workflows through one CLI
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

The repository includes example configurations derived from real projects:

- [`qupled`](examples/qupled.md): mixed Python/C++ project with native CMake
  builds, Python packaging, pytest suites, and profile overrides
- [`pybind11`](examples/pybind11.md): pinned containerized example that runs
  `foga` against an upstream repository inside Docker

## Install

Install `foga` as a normal user with:

```bash
pip install foga
```
