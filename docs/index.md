# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, docs, format, lint,
install, deploy, inspect, and cleanup workflows.

The problem `foga` is trying to solve is familiar: repository workflows often
get split across shell scripts, Make targets, CI snippets, and README notes.
That makes local development, CI, and release automation drift apart over time.
`foga` keeps the stable workflow definition in `foga.yml`, uses built-in
backends for common tools, and leaves only the project-specific edges in hooks
or scripts.

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
- Looking for command behavior: read [CLI Reference](cli.md)
- Working on this repository: read [Development](development.md)

## Platforms and limitations

`foga` itself is a Python CLI, but repository workflows depend on the tools and
package managers available on the machine where they run. Based on the current
examples and CI setup:

- Ubuntu/Linux is the main documented path and the platform exercised in CI
- some examples and profiles include macOS-specific behavior, especially for
  Homebrew-based toolchains
- system package backends such as `apt-get`, `brew`, and `yum` are
  intentionally platform-specific
- Windows is not currently documented or covered by CI in this repository

Another intentional limitation is scope: `foga` is meant to describe stable
repository workflows, not to replace every ad-hoc bootstrap or infrastructure
script you may have.
