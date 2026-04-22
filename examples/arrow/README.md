# arrow

This example shows `foga` driving a real upstream mixed C++/Python project with
system packages, a native CMake build, a PyArrow install, pytest-based tests,
and Sphinx documentation.

What it includes:

- [`Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/arrow/Dockerfile): clones Apache Arrow in Docker, installs a released
  `foga`, and prepares the base environment
- [`foga.yml`](https://github.com/fedluc/foga/blob/main/examples/arrow/foga.yml): a working `foga` configuration for the Arrow checkout
- [`run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/arrow/run-in-docker.py): helper that builds the image and opens
  a shell or runs a one-shot command in the container

This example pins Arrow to commit
`36c8c9a24aec70fb41441c6a1a2a28b777d351e3`
(`apache-arrow-24.0.0.dev-318-g36c8c9a24a`) so the demo remains reproducible.

Typical usage:

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

The docs path is intentionally heavier. `foga docs` rebuilds Arrow C++ with a
docs-specific profile and reinstalls `docs-env` in pre-hooks before Sphinx
runs:

```bash
foga docs
```

Why this example matters:

- it shows `foga` coordinating a nontrivial upstream project instead of only a
  toy repository
- it keeps system setup, native build, Python install, tests, docs, and cleanup
  in one config
- it exercised real integration edges, including system package gaps, absolute
  paths for temp-directory builds, and conservative parallelism for Docker


Use this example when you want a credible, containerized demonstration of
`foga` on a large real-world codebase.
