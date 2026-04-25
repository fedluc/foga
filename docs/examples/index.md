# Examples

The example set has two distinct jobs:

- the tutorial track teaches `foga` incrementally, starting from the smallest
  useful config and adding one concept at a time
- the real-world examples show `foga` working against larger or more realistic
  repositories, including upstream checkouts and mixed Python/C++ workflows

## Choose an example path

Start with the [tutorial examples](tutorials.md) when you are learning the
configuration model and want a sequence you can read in order.

Jump to the real-world examples when you already understand the basics and want
to see how `foga` maps onto a more complete repository shape.

## Tutorial track

- [Tutorial examples](tutorials.md): the guided path through incremental
  adoption, from a pure Python project to mixed Python/C++ builds, testing, and
  profiles

## Real-world references

- [arrow](arrow.md): Apache Arrow in Docker with system dependencies, a native
  CMake build, Python installs, pytest, and Sphinx docs.
- [numpy](numpy.md): NumPy in Docker with a separate Meson native build, Python
  packaging, pytest, and docs.
- [pybind11](pybind11.md): pybind11 in Docker with native builds, tests, docs,
  and profile-driven C++ builds.
- [qupled](qupled.md): a full repository already using `foga` across its
  workflows.

```{toctree}
:maxdepth: 1
:hidden:

tutorials
arrow
numpy
pybind11
qupled
```
