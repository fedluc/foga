# 02-pybind11-hello

This example adds a tiny `pybind11` module while keeping the standalone C++
build separate from the Python package build.

It shows:

- a small shared C++ greeting implementation
- a standalone CMake executable built through `build.cpp`
- a Python package built through `build.python`
- a simple smoke test driven by the `run-foga` helper

Files:

- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`cpp/`](cpp)
- [`src/hello_bindings`](src/hello_bindings)
- [`run-foga`](run-foga)

Typical usage:

```bash
./run-foga
./run-foga build cpp
./run-foga build python
```
