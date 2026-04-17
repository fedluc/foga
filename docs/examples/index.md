# Examples

The repository includes both staged tutorial examples and larger real-world
reference configurations.

## Start here

- [Tutorial examples](tutorials.md): four runnable examples that ramp up from a
  pure-Python package to mixed C++/Python workflows with tests and profiles

## Real-world examples

- [qupled](qupled.md): C++ CMake build, Python packaging, pytest suites,
  a `ctest` C++ test runner, and MPI-related profiles
- [pybind11](pybind11.md): pinned containerized example that provisions an
  upstream repository in Docker and runs `foga` against it

Use the tutorial set when you are learning `foga` for the first time. Use the
real-world examples when you want denser reference material for an existing
repository.

```{toctree}
:maxdepth: 1
:hidden:

tutorials
qupled
pybind11
```
