# numpy

This example shows `foga` driving a real upstream Python/native project with a
separate Meson native build, Python packaging, pytest-based tests, and Sphinx
documentation.

What it includes:

- [`examples/numpy/Dockerfile`](https://github.com/fedluc/foga/blob/main/examples/numpy/Dockerfile):
  clones NumPy in Docker, installs `foga` from the current checkout, and
  prepares the base environment
- [`examples/numpy/foga.yml`](https://github.com/fedluc/foga/blob/main/examples/numpy/foga.yml): a
  working `foga` configuration for the NumPy checkout
- [`examples/numpy/run-in-docker.py`](https://github.com/fedluc/foga/blob/main/examples/numpy/run-in-docker.py): helper
  that builds the image and opens a shell or runs a one-shot command in the
  container

This example pins NumPy to tag `v2.4.4` so the demo remains reproducible.

Typical usage:

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

`build.cpp` uses the `meson` backend to compile NumPy's native extension tree
in `build-foga` independently from the Python packaging workflow. Inside the
example container, the Docker image prepends a `meson` wrapper on `PATH` that
forwards to NumPy's vendored Meson entrypoint, because upstream NumPy requires
that patched Meson build.

`build.python` still uses `python-build` for wheels and sdists, so the example
shows how `foga` can separate a native build workflow from the Python package
build even when the upstream project is tightly integrated.

`foga test` installs the `test-env` target in a pre-hook so `pytest` and the
editable package are available before the test runner starts. `foga docs`
installs the docs environment in a pre-hook and then builds the upstream docs.

Why this example matters:

- it shows a first-class Meson-based `build.cpp` workflow instead of only
  CMake-based native builds
- it demonstrates a repository where the native build and Python packaging
  workflows are intentionally separate
- it captures a real upstream edge case, where NumPy requires its vendored
  Meson rather than the stock `meson` executable

Use this example when you want a credible, containerized demonstration of
`foga` on a widely used upstream Python/native codebase.
