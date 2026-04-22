# Tutorial examples

Start with these examples when you want a smaller path into `foga` before
reading the denser reference projects.

Read them in order:

1. [`01-python-only`](01-python-only/README.md): the smallest end-to-end
   project shape in the repository.
2. [`02-pybind11-hello`](02-pybind11-hello/README.md): the first step from pure
   Python into a mixed Python/C++ project.
3. [`03-pybind11-tests`](03-pybind11-tests/README.md): the same mixed project
   shape extended with tests and code quality checks.
4. [`04-pybind11-profiles`](04-pybind11-profiles/README.md): the same project
   shape extended with profile-specific build behavior.

## Running the tutorials

Use `python examples/tutorial/run-tutorial.py --list` to see the available tutorial examples,
then run `python examples/tutorial/run-tutorial.py <example-name>` from the
repository root to start a Docker container that will be used to run the example. If you prefer to avoid Docker,
you can also run the examples in directly on your machine, in this case you have to install the prerequisites 
that are listed in the README of each tutorial required to run each example
