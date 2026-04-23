# arrow

This example shows `foga` driving a large upstream mixed C++/Python repository
inside Docker. It combines system package installation, a native CMake build,
Python installs, pytest, and Sphinx docs in one working configuration.

## What this example contains

- [`Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/arrow/Dockerfile):
  provisions the container image and clones Apache Arrow
- [`foga.yml`](https://github.com/fedluc/foga/blob/main/examples/arrow/foga.yml):
  the working `foga` configuration for the Arrow checkout
- [`run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/arrow/run-in-docker.py):
  helper that builds the image and opens a shell or runs a one-shot command

The example pins Arrow to commit
`36c8c9a24aec70fb41441c6a1a2a28b777d351e3`
(`apache-arrow-24.0.0.dev-318-g36c8c9a24a`) to keep the demo reproducible.

## Typical workflow

Start the example container:

```bash
examples/arrow/run-in-docker.py
```

Once inside the container:

```bash
foga validate
foga build cpp
foga install --target test-env
foga test
```

Build the upstream documentation with:

```bash
foga docs
```

## What this example demonstrates

- one config coordinating system setup, native build, Python install, tests,
  docs, and cleanup
- a credible upstream integration instead of a toy repository
- heavier docs handling, where `foga docs` rebuilds Arrow C++ with a docs
  profile and reinstalls `docs-env` in pre-hooks before running Sphinx

## When to use this example

Use `arrow` when you want the heaviest, most demanding upstream demonstration
in the repository.
