# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. These projects often accumulate a separate tool or
script for each workflow: one for Python packaging, one for native builds, one
for tests, another for documentation, and more scattered across Make targets,
CI snippets, shell scripts, and README notes.

`foga` centralizes those workflows in a single `foga.yml` file and exposes them
through one command-line interface. Built-in backends cover common tools for
builds, tests, documentation, installs, deploys, and cleanup, while hooks and
scripts remain available for project-specific behavior.

## What foga does

Use `foga` to define and run the repository workflows that usually spread
across local scripts, CI jobs, and project notes:

- build Python packages and C++ artifacts from one config file
- run Python and C++ test workflows through one CLI
- generate documentation with configured docs backends
- install local packages and external dependencies through one CLI
- run format, lint, deploy, and cleanup workflows from the same config
- switch environment-specific settings with named profiles
- inspect the resolved config before running anything
- keep escape hatches explicit through structured hooks

## Start here

- New to `foga`: read [Getting Started](getting-started.md)
- Defining `foga.yml`: read [Configuration Overview](configuration/index.md)
- Looking for concrete reference configs: read [Examples](examples/index.md)
- Looking for command behavior: read [CLI Usage](cli.md)
- Working on this repository: read [Development](development.md)

```{toctree}
:maxdepth: 2
:hidden:

getting-started
configuration/index
examples/index
cli
development
```

## Platforms and limitations

`foga` itself is a Python CLI, but repository workflows depend on the tools and
package managers available on the machine where they run.

- Linux and macOS are the primary documented platforms
- system package backends such as `apt-get`, `brew`, and `yum` are
  platform-specific and depend on the tools available on the host machine
- Windows is not currently documented or covered by CI in this repository

Another intentional limitation is scope: `foga` is meant to describe stable
repository workflows, not to replace every ad-hoc bootstrap or infrastructure
script you may have.
