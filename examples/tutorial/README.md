# Tutorial examples

These examples are designed as a small ladder instead of a single large
reference project.

Read them in order:

1. [`01-python-only`](01-python-only/README.md): pure Python package with build,
   install, and test workflows.
2. [`02-pybind11-hello`](02-pybind11-hello/README.md): adds a tiny `pybind11`
   module and keeps the standalone C++ build separate from the Python package
   build.
3. [`03-pybind11-tests`](03-pybind11-tests/README.md): extends the mixed project
   with Python tests, C++ tests, and Python lint and format targets.
4. [`04-pybind11-profiles`](04-pybind11-profiles/README.md): adds profile-driven
   debug and release C++ build modes to the tested mixed project.

Each directory includes a `run-foga` helper that uses the repository's local
`foga` checkout:

```bash
examples/tutorial/01-python-only/run-foga
examples/tutorial/02-pybind11-hello/run-foga
examples/tutorial/03-pybind11-tests/run-foga
examples/tutorial/04-pybind11-profiles/run-foga
```

Once these examples feel familiar, move to the larger real-world references in
[`examples/qupled`](../qupled/README.md) and
[`examples/pybind11`](../pybind11/README.md).
