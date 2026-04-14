# pybind11

This example shows how to run `foga` against a real upstream repository inside
Docker.

What it includes:

- [`examples/pybind11/Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/pybind11/Dockerfile):
  provisions a build environment similar to the devcontainer used during
  development here
- [`examples/pybind11/foga.yml`](https://github.com/fedluc/foga/blob/main/examples/pybind11/foga.yml): example
  `foga` configuration for `pybind11`
- [`examples/pybind11/run-foga`](https://github.com/fedluc/foga/blob/main/examples/pybind11/run-foga): helper
  that builds the image and runs `foga` inside the container

The Docker image clones `pybind11` at pinned commit
`288913638bb2da563f1c39e7d07071c2f21bfb25`, prepares its `.venv`, installs
`foga==0.1.0` from PyPI, and copies in the example configuration.

Typical usage:

```bash
examples/pybind11/run-foga
examples/pybind11/run-foga foga inspect --profile tidy-relaxed build
examples/pybind11/run-foga foga build --profile release cpp
```

The default command is a narrower build:

```bash
foga build --profile cpptest cpp
```

Use this example when you want a self-contained demonstration of `foga` on a
well-known C++/Python project without requiring a pre-existing local checkout.
It also shows a profile-level launcher override for wrapper-based tool
execution.
