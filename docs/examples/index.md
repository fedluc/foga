# Examples

The repository organizes examples into guided tutorials and larger real-world
reference configurations.

The examples are meant to answer two different questions:

- "How do I start writing `foga.yml` without getting lost?"
- "What does `foga` look like in a repository with real dependencies and more
  than one workflow?"

## Start here

- [Tutorial examples](tutorials.md): guided examples that start small and add
  one idea at a time while you learn `foga`

## Real-world examples

- [arrow](arrow.md): Apache Arrow in Docker with system dependencies, native
  builds, Python installs, pytest, and Sphinx docs. This is the heaviest
  example and shows `foga` coordinating a large upstream project.
- [numpy](numpy.md): NumPy in Docker with a separate Meson native build,
  Python packaging, pytest, and docs. This is the best example when you need
  to understand how `foga` can model a native build independently from Python
  packaging.
- [qupled](qupled.md): C++ CMake build, Python packaging, pytest suites,
  a `ctest` C++ test runner, and MPI-related profiles. This is the clearest
  single-file reference when you want one config that mixes Python and C++
  workflows.
- [pybind11](pybind11.md): pinned containerized example that provisions an
  upstream repository in Docker and runs `foga` against it. This is useful
  when you want a realistic upstream checkout without the weight of Arrow.

Use the tutorial set when you are learning `foga` for the first time. Use the
real-world examples when you want denser reference material for an existing
repository shape.

```{toctree}
:maxdepth: 1
:hidden:

tutorials
arrow
numpy
qupled
pybind11
```
