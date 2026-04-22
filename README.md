<p align="center">
  <img src="https://raw.githubusercontent.com/fedluc/foga/main/assets/foga.svg" alt="foga" width="400">
</p>

`foga` is a Python package and CLI for developers maintaining Python packages
with C or C++ bindings. It replaces ad-hoc repository scripts with a
single YAML configuration file `foga.yml` that orchestrates build, test, docs, format, lint,
install, deploy, inspect, and cleanup workflows.

## Install

```bash
pip install foga
```

## Quick start

Start from one of the examples if you want a
working baseline quickly. The [tutorial examples](examples/tutorial/README.md) are the best starting point for
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

Full documentation available at <https://fedluc.github.io/foga/>