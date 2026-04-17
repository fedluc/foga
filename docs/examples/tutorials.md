# Tutorial examples

These examples are meant to be read in order. Each one adds one new idea
without forcing you to absorb a large real-world repository first.

## Progressive example ladder

1. [`01-python-only`](https://github.com/fedluc/foga/blob/main/examples/tutorial/01-python-only/README.md)
   shows a minimal Python package with custom dependencies, a package build, a
   development install, and pytest-based tests.
2. [`02-pybind11-hello`](https://github.com/fedluc/foga/blob/main/examples/tutorial/02-pybind11-hello/README.md)
   adds a tiny `pybind11` module and separates the standalone C++ build from the
   Python package build.
3. [`03-pybind11-tests`](https://github.com/fedluc/foga/blob/main/examples/tutorial/03-pybind11-tests/README.md)
   extends the mixed project with Python tests, C++ tests, and Python linting
   and formatting targets.
4. [`04-pybind11-profiles`](https://github.com/fedluc/foga/blob/main/examples/tutorial/04-pybind11-profiles/README.md)
   keeps the tested mixed project shape but adds profiles for debug and release
   C++ builds.

## How to run them

Each tutorial directory includes a `run-foga` helper. From the repository root:

```bash
examples/tutorial/01-python-only/run-foga
examples/tutorial/02-pybind11-hello/run-foga
examples/tutorial/03-pybind11-tests/run-foga
examples/tutorial/04-pybind11-profiles/run-foga
```

You can also pass an explicit `foga` command through the helper, for example:

```bash
examples/tutorial/04-pybind11-profiles/run-foga inspect --profile release build cpp
```

## After the tutorials

Once the tutorial examples make sense, move on to the real-world examples:

- [qupled](qupled.md)
- [pybind11](pybind11.md)
