# 02-pybind11-hello

This example adds a tiny `pybind11` module while keeping the standalone C++
build separate from the Python package build.

It shows:

- a small shared C++ greeting implementation
- a standalone CMake executable built through `build.cpp`
- a Python package built through `build.python`
- a Dockerfile that installs `foga` through `uv sync` and native tooling through
  `foga install --target system`

Files:

- [`Dockerfile`](Dockerfile)
- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`cpp/`](cpp)
- [`src/hello_bindings`](src/hello_bindings)
- [`run_example.py`](run_example.py)

Typical usage from the repository root:

```bash
python run-example.py pybind11-hello
python run-example.py pybind11-hello --list-steps
python run-example.py pybind11-hello build-cpp build-python
```
