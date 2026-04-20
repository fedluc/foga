# pybind11

This example shows how to run `foga` against a real upstream repository inside
Docker.

What it includes:

- [`Dockerfile`](Dockerfile): provisions a build environment similar to the
  devcontainer used during development here
- [`foga.yml`](foga.yml): example `foga` configuration for `pybind11`
- [`run-in-docker.py`](run-in-docker.py): helper that builds the image and runs
  `foga` inside the container

The Docker image clones `pybind11` at pinned commit
`288913638bb2da563f1c39e7d07071c2f21bfb25`, installs the latest released
`foga` from PyPI, and copies in the example configuration.

Typical usage:

```bash
examples/pybind11/run-in-docker.py
examples/pybind11/run-in-docker.py foga inspect --profile tidy-relaxed build
examples/pybind11/run-in-docker.py foga build --profile release cpp
```

The default command is a narrower build:

```bash
foga build --profile cpptest cpp
```

Use this example when you want a self-contained demonstration of `foga` on a
well-known C++/Python project without requiring a pre-existing local checkout.
