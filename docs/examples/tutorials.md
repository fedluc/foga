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
   keeps the mixed project shape from the previous example but adds profiles for
   debug and release C++ builds.

## How to run them

Each tutorial directory is self-contained. You can copy one folder anywhere,
run its `run-example.sh` script, and then use the interactive container session
as the example workspace.

The script always rebuilds the Docker image with `--no-cache` and starts a
fresh container in `/workspace/example`, so users do not need any local Python
or C++ toolchain beyond Docker itself.

The per-example README lists the concrete `foga` commands to run once the shell
opens.

## After the tutorials

Once the tutorial examples make sense, move on to the real-world examples:

- [qupled](qupled.md)
- [pybind11](pybind11.md)
