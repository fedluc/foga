<p align="center">
  <img src="https://raw.githubusercontent.com/fedluc/foga/main/assets/foga.svg" alt="foga" width="400">
</p>

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file that drives build, test, docs, format, lint,
install, deploy, inspect, and cleanup workflows.

`foga` is an opinionated tool for repository workflows that would otherwise end
up split across helper scripts, CI snippets, and README notes. Keep the stable
workflow definition in `foga.yml`, use built-in backends for common tools, use
`launcher` when a command should run through a wrapper such as `uv run`, and
keep genuinely project-specific orchestration in small hooks or scripts.

## Install

```bash
pip install foga
```

## Quick start

Start from one of the examples rather than from a blank file if you want a
working baseline quickly. The tutorial examples are the best starting point for
new users, and the larger reference examples show how `foga` looks in more
realistic repositories.

After you have created `foga.yml`, validate and inspect before you run anything
for real:

```bash
foga validate
foga inspect
foga build --dry-run
foga test --dry-run
```

For runnable examples that build up gradually, start with
[`examples/tutorial/`](examples/tutorial/) or the
[Examples guide](docs/examples/tutorials.md). Each tutorial README lists the
local prerequisites, and this repository also includes
`examples/tutorial/run-tutorial.py` if you want to run the tutorials with only
Docker and Python instead of installing the example-specific tools locally.

### Drafting `foga.yml` with agents

Use Codex or another agentic tool to draft `foga.yml` from the repository's
existing build, test, docs, and deploy commands, and ask it to map those
workflows to built-in `foga` backends first. If the tool supports local
skills, use [`skills/foga-config-authoring/SKILL.md`](skills/foga-config-authoring/SKILL.md)
to produce the initial config or a first draft. Then verify the result with
`foga validate`, `foga inspect`, and dry-run commands before replacing scripts
or CI jobs.

## Platform notes

`foga` itself is a normal Python CLI, but repository workflows are only as
portable as the tools they invoke. Based on the current examples and CI:

- Linux is the main documented path, and CI runs on Ubuntu
- macOS is supported by some configs and profiles, especially where Homebrew is
  the expected package manager
- system package installers such as `apt-get`, `brew`, and `yum` are
  intentionally platform-specific backends
- Windows is not documented or exercised in CI today

The practical limitation is that `foga` standardizes workflow shape, not the
underlying toolchain availability on every machine.

## Documentation

- Docs site: <https://fedluc.github.io/foga/>
- Docs source: [`docs/`](docs/)
- Example configs: [`examples/`](examples/)

Start with:

- [Getting Started](docs/getting-started.md)
- [Configuration Overview](docs/configuration/index.md)
- [CLI Reference](docs/cli.md)
- [Examples](docs/examples/index.md)
