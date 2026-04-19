# Tutorial examples

These examples are meant to be read in order. Each one gives you one new idea
to absorb before you move on to denser reference material.

## Progressive example ladder

1. [`01-python-only`](https://github.com/fedluc/foga/blob/main/examples/tutorial/01-python-only/README.md)
   gives you the smallest end-to-end project shape to copy when you are just
   starting.
2. [`02-pybind11-hello`](https://github.com/fedluc/foga/blob/main/examples/tutorial/02-pybind11-hello/README.md)
   shows how to add a first native extension without changing the overall
   workflow shape too much.
3. [`03-pybind11-tests`](https://github.com/fedluc/foga/blob/main/examples/tutorial/03-pybind11-tests/README.md)
   grows that mixed setup into a more realistic development workflow with
   testing and code quality checks.
4. [`04-pybind11-profiles`](https://github.com/fedluc/foga/blob/main/examples/tutorial/04-pybind11-profiles/README.md)
   shows how to keep one base config while the project starts to need distinct
   build modes.

## How to run them

You can run the tutorials in two ways:

1. In Docker, which only requires Docker and Python and avoids installing the
   example-specific tools on your machine. From the repository root, run
   `python examples/tutorial/run-example.py --list` to see the available
   examples, then run `python examples/tutorial/run-example.py <example-name>`.
2. Locally, after installing the prerequisites listed in the README for the
   tutorial you want to run.

The helper rebuilds the selected Docker image with `--no-cache` and opens a
shell in `/workspace/example`.

The per-example README lists the concrete `foga` commands to run once the
environment is ready.

## After the tutorials

Once the tutorial examples make sense, move on to the real-world examples:

- [qupled](qupled.md)
- [pybind11](pybind11.md)
