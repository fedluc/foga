# Examples

The repository organizes examples into guided tutorials and larger real-world
reference configurations.

## Start here

- [Tutorial examples](tutorials.md): guided examples that start small and add
  one idea at a time while you learn `foga`

## Real-world examples

- [arrow](arrow.md): Apache Arrow in Docker with system dependencies, native
  builds, Python installs, pytest, and Sphinx docs
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
arrow
qupled
pybind11
```
