# pybind11

This example shows how to run `foga` against a pinned upstream repository in
Docker without the weight of the Arrow example.

## What this example contains

- [`Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/pybind11/Dockerfile):
  provisions the container image and clones `pybind11`
- [`foga.yml`](https://github.com/fedluc/foga/blob/main/examples/pybind11/foga.yml):
  the working `foga` configuration for the upstream checkout
- [`run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/pybind11/run-in-docker.py):
  helper that builds the image and opens a shell or runs a one-shot command

The Docker image clones `pybind11` at pinned commit
`288913638bb2da563f1c39e7d07071c2f21bfb25` to keep the example reproducible.

## Typical workflow

Start the example container:

```bash
examples/pybind11/run-in-docker.py
```

Once inside the container:

```bash
foga validate
foga build cpp
foga build --profile release cpp
foga test
```

Build the upstream documentation with:

```bash
foga docs
```

You can also use the helper for one-shot commands:

```bash
examples/pybind11/run-in-docker.py foga inspect install
examples/pybind11/run-in-docker.py foga docs
```

## What this example demonstrates

- a self-contained Docker workflow for a real upstream C++/Python project
- `foga install` provisioning default Python and system build dependencies
- a lighter upstream demonstration than Arrow, while still exercising builds,
  tests, docs, and profiles

## When to use this example

Use `pybind11` when you want a realistic upstream example in Docker without the
setup cost and size of the Arrow demo.
