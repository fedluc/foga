# Examples

The repository includes concrete `foga` configurations derived from real
projects.

## Available examples

- [qupled](qupled.md): C++ CMake build, Python packaging, pytest suites,
  a `ctest` C++ test runner, and MPI-related profiles
- [pybind11](pybind11.md): pinned containerized example that provisions an
  upstream repository in Docker and runs `foga` against it

Use these examples as references when authoring a new `foga.yml`, but keep your
own config smaller than the examples on the first pass.

```{toctree}
:maxdepth: 1
:hidden:

qupled
pybind11
```
