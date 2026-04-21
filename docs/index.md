# foga

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, docs, format, lint,
install, deploy, inspect, and cleanup workflows.

The problem `foga` is trying to solve is familiar: repository workflows often
get split across shell scripts, Make targets, CI snippets, and README notes.
That makes local development, CI, and release automation drift apart over time.
`foga` keeps the stable workflow definition in one place and lets the CLI
resolve, inspect, and run that definition consistently.

## What foga does

`foga` gives a project one entrypoint for the common tasks that usually end up
split across Makefiles, shell scripts, CI snippets, and README notes:

- build Python packages and C++ artifacts from one config file
- run Python and C++ test workflows through one CLI
- install local packages and external dependencies through one CLI
- switch environment-specific settings with named profiles
- inspect the resolved config before running anything
- keep escape hatches explicit through structured hooks

## How it works

The usual `foga` shape is:

1. Define the stable workflows in `foga.yml`
2. Choose built-in backends for common tools like `pytest`, `python-build`,
   `cmake`, `meson`, `sphinx`, or `twine`
3. Add `launcher` when the tool should run through a wrapper such as `uv run`
4. Keep genuinely project-specific setup or cleanup in small hooks or scripts
5. Use `validate`, `inspect`, and dry-run commands before switching CI or
   developer workflows over to `foga`

That gives readers a single source of truth without pretending every repository
should become a generic YAML task runner.

## Start here

- New to `foga`: read [Getting Started](getting-started.md)
- Defining `foga.yml`: read [Configuration Overview](configuration/index.md)
- Looking for concrete reference configs: read [Examples](examples/index.md)
- Looking for command behavior: read [CLI Reference](cli.md)
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

## Getting started quickly

Install `foga`:

```bash
pip install foga
```

Start with a minimal config:

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

Then run:

```bash
foga validate
foga inspect
foga build --dry-run
foga test --dry-run
```

If you are using Codex or another agentic tool to help write `foga.yml`, give
it the repository's current scripts or CI commands and ask it to map them to
the built-in backends first. If your environment provides a dedicated
config-authoring skill, use that. Then verify the generated config with
`validate`, `inspect`, and dry-run output before you trust it.

## Example projects

The repository includes two kinds of examples:

- [Tutorial examples](examples/tutorials.md): staged starting points that help
  you learn `foga` one step at a time before you adapt it to a larger project
- [`qupled`](examples/qupled.md): mixed Python/C++ project with C++ CMake
  builds, Python packaging, pytest suites, and profile overrides
- [`pybind11`](examples/pybind11.md): pinned containerized example that runs
  `foga` against an upstream repository inside Docker

The examples are reference material, not filler. The tutorial ladder shows how
to adopt `foga` incrementally, while the larger examples show what the config
looks like once a repository has multiple workflows, system dependencies, and
profile-specific behavior.

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

## Reference map

- [Getting Started](getting-started.md): first config, first commands, and
  adoption flow
- [Examples](examples/index.md): guided and real-world examples, with context
  on why each one matters
- [Configuration Overview](configuration/index.md): top-level config structure
  and where to find backend-specific options
- [CLI Reference](cli.md): command behavior and dry-run/inspect usage
