# Tutorial examples

These examples are designed as a small ladder instead of a single large
reference project.

Read them in order:

1. [`01-python-only`](01-python-only/README.md): pure Python package with build
   and install workflows in a containerized example environment.
2. [`02-pybind11-hello`](02-pybind11-hello/README.md): adds a tiny `pybind11`
   module and shows native dependency installation through `foga install` and
   `apt-get` inside Docker.
3. [`03-pybind11-tests`](03-pybind11-tests/README.md): extends the mixed project
   with Python tests, C++ tests, and Python lint and format targets.
4. [`04-pybind11-profiles`](04-pybind11-profiles/README.md): adds profile-driven
   debug and release C++ build modes to the tested mixed project.

Run them from the repository root with the cross-platform launcher:

```bash
python run-example.py python-only
python run-example.py pybind11-hello
python run-example.py pybind11-tests
python run-example.py pybind11-profiles
```

Those commands build an example-specific Docker image and run the example in a
container by default, so the host machine does not need the example toolchain.
If you already have the dependencies and explicitly want a local run, use
`python run-example.py --mode host <name>`.

Once these examples feel familiar, move to the larger real-world references in
[`examples/qupled`](../qupled/README.md) and
[`examples/pybind11`](../pybind11/README.md).
