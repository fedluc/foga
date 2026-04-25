# Tutorial examples

The tutorial track is the fastest way to learn how `foga.yml` grows from a
minimal config into a more complete workflow definition. Read these examples in
order. Each step adds one new idea without changing the overall project shape
more than necessary.

## Tutorial ladder

1. [`01-python-only`](https://github.com/fedluc/foga/blob/main/examples/tutorial/01-python-only/README.md)
   starts with the smallest runnable `foga` project: validate a config, install
   development dependencies, and build a Python package.
2. [`02-pybind11-hello`](https://github.com/fedluc/foga/blob/main/examples/tutorial/02-pybind11-hello/README.md)
   adds a first native extension and separates the C++ build from the Python
   package build.
3. [`03-pybind11-tests`](https://github.com/fedluc/foga/blob/main/examples/tutorial/03-pybind11-tests/README.md)
   adds Python and C++ test workflows together with formatting and linting.
4. [`04-pybind11-profiles`](https://github.com/fedluc/foga/blob/main/examples/tutorial/04-pybind11-profiles/README.md)
   adds profile-driven build modes so one base config can express more than one
   workflow variant.

## How to run the tutorials

Docker is the easiest way to run the tutorial examples because it avoids
installing example-specific toolchains on your machine.

From the repository root:

```bash
python examples/tutorial/run-tutorial.py --list
python examples/tutorial/run-tutorial.py 01-python-only
```

You can also run a tutorial locally after installing the prerequisites listed
in the README for that specific example.

## After the tutorials

Once the tutorial sequence makes sense, move on to the real-world examples
based on the kind of repository you want to model:

- [arrow](arrow.md) for the heaviest upstream, containerized demonstration
- [numpy](numpy.md) for a clear split between native and Python build workflows
- [pybind11](pybind11.md) for a lighter Docker-based C++/Python example with
  builds, tests, docs, and profiles
- [qupled](qupled.md) for a live repository already using `foga` across its
  workflows
