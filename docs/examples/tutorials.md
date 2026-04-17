# Tutorial examples

These examples are meant to be read in order. Each one adds one new idea
without forcing you to absorb a large real-world repository first.

## Progressive example ladder

1. [`01-python-only`](https://github.com/fedluc/foga/blob/main/examples/tutorial/01-python-only/README.md)
   shows a minimal Python package with custom dependencies, a package build, and
   a development install in an isolated container workflow.
2. [`02-pybind11-hello`](https://github.com/fedluc/foga/blob/main/examples/tutorial/02-pybind11-hello/README.md)
   adds a tiny `pybind11` module and shows how `foga install` can drive
   `apt-get` installation of native build tooling during a Docker image build.
3. [`03-pybind11-tests`](https://github.com/fedluc/foga/blob/main/examples/tutorial/03-pybind11-tests/README.md)
   extends the mixed project with Python tests, C++ tests, and Python linting
   and formatting targets.
4. [`04-pybind11-profiles`](https://github.com/fedluc/foga/blob/main/examples/tutorial/04-pybind11-profiles/README.md)
   keeps the tested mixed project shape but adds profiles for debug and release
   C++ builds.

## How to run them

Run the tutorial examples from the repository root with one cross-platform
launcher:

```bash
python run-example.py python-only
python run-example.py pybind11-hello
python run-example.py pybind11-tests
python run-example.py pybind11-profiles
```

Those commands build the example-specific Docker image from the example
directory and execute the example's `run_example.py` walkthrough script in a
container by default. Each example installs `foga` from PyPI through its own
`pyproject.toml` and `uv sync`, so the image no longer depends on a copy of
this repository. To inspect the named walkthrough steps for one example, run:

```bash
python run-example.py pybind11-profiles --list-steps
```

To run specific guided steps instead of the full walkthrough, pass the step
names after the example name:

```bash
python run-example.py pybind11-profiles build-release test-release
```

If you intentionally want to run an example directly on the current machine, use
`--mode host`:

```bash
python run-example.py --mode host pybind11-tests lint
```

## After the tutorials

Once the tutorial examples make sense, move on to the real-world examples:

- [qupled](qupled.md)
- [pybind11](pybind11.md)
