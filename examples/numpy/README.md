# numpy

This example shows `foga` driving a real upstream Python/native project with a
separate Meson native build, Python packaging, pytest-based tests, and Sphinx
documentation.

What it includes:

- [`Dockerfile`](Dockerfile): clones NumPy in Docker, installs a released
  `foga` from this checkout, and prepares the base environment
- [`foga.yml`](foga.yml): a working `foga` configuration for the NumPy checkout
- [`run-in-docker.py`](run-in-docker.py): helper that builds the image and
  opens a shell or runs a one-shot command in the container

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

`foga build` also works because this example sets `build.default: all`.

`build.cpp` uses the `meson` backend to compile NumPy's native extension tree in
`build-foga` independently from the Python packaging workflow. Inside the
example container, the Docker image prepends a `meson` wrapper on `PATH` that
forwards to NumPy's vendored Meson entrypoint, because upstream NumPy requires
that patched Meson build. `build.python` still uses `python-build` for wheels
and sdists, so you can exercise the native and Python build paths separately
when needed.

`foga test` installs the `test-env` target in a pre-hook so `pytest` and the
editable package are available before the test runner starts.

Docs use a dedicated install target. `foga docs` installs the Sphinx
dependencies in a pre-hook and then builds the upstream documentation:

```bash
foga docs
```

The generated site ends up in `doc/build/html`.

Use this example when you want a credible, containerized demonstration of
`foga` on a widely used upstream Python/native codebase.
