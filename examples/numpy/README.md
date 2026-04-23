# numpy

This example shows `foga` driving a real upstream Python/native project inside
Docker, with a separate Meson native build, Python packaging, pytest, and
Sphinx docs.

## What this example contains

- [`Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/numpy/Dockerfile):
  provisions the container image and clones NumPy
- [`foga.yml`](https://github.com/fedluc/foga/blob/main/examples/numpy/foga.yml):
  the working `foga` configuration for the NumPy checkout
- [`run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/numpy/run-in-docker.py):
  helper that builds the image and opens a shell or runs a one-shot command

The example pins NumPy to tag `v2.4.4` to keep the demo reproducible.

## Typical workflow

Start the example container:

```bash
examples/numpy/run-in-docker.py
```

Once inside the container:

```bash
foga validate
foga build cpp
foga build python
foga test
```

Build the upstream documentation with:

```bash
foga docs
```

## What this example demonstrates

- a clear separation between the native build workflow and the Python packaging
  workflow
- `build.cpp` using the `meson` backend independently from `build.python`
- pre-hooks installing the test and docs environments before pytest or Sphinx
  runs

`foga build` also works because this example sets `build.default: all`.

## When to use this example

Use `numpy` when you want to understand how `foga` can model a native build and
Python packaging as separate workflows in the same repository.
