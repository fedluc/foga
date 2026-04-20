# pybind11

This example shows how to run `foga` against a real upstream repository inside
Docker.

What it includes:

- [`examples/pybind11/Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/pybind11/Dockerfile):
  provisions a build environment similar to the devcontainer used during
  development here
- [`examples/pybind11/foga.yml`](https://github.com/fedluc/foga/blob/main/examples/pybind11/foga.yml): example
  `foga` configuration for `pybind11`
- [`examples/pybind11/run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/pybind11/run-in-docker.py): helper
  that builds the image and opens a shell or runs a one-shot command in the container

The Docker image clones `pybind11` at pinned commit
`288913638bb2da563f1c39e7d07071c2f21bfb25`, installs the latest released
`foga` from PyPI, copies in the example configuration, and lets `foga install`
provision the default Python and system build dependencies inside the image.

Typical usage:

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

Docs use a dedicated install target. `foga docs` installs the Sphinx
dependencies in a pre-hook and then builds the upstream documentation:

```bash
foga docs
```

The generated site ends up in `docs/.build/html`.

You can still use the helper for one-shot commands when needed:

```bash
examples/pybind11/run-in-docker.py foga inspect install
examples/pybind11/run-in-docker.py foga docs
```

Use this example when you want a self-contained, containerized demonstration of
`foga` on a well-known upstream C++/Python project without requiring a
pre-existing local checkout.
