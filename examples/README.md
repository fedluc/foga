# Examples

This directory contains runnable `foga` configurations that cover both guided
tutorials and real-world reference projects.

## Tutorial examples

- [`tutorial`](tutorial/README.md): four examples that ramp up from a
  pure-Python package to a mixed C++/Python project with tests, linting, and
  profile-based build modes.

## Real-world reference examples

- [`qupled`](qupled/README.md): C++ CMake build, Python packaging, pytest
  suites, and a `ctest` C++ test runner with MPI-related profiles.
- [`pybind11`](pybind11/README.md): pinned containerized example that provisions
  the upstream project in Docker and runs `foga` against it.
