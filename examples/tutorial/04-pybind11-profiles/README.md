# 04-pybind11-profiles

This example keeps the tested mixed C++/Python project shape and adds
profile-driven build modes for the C++ side.

It shows:

- a default debug-oriented C++ build
- a `release` profile with a separate build directory and `Release` flags
- matching `ctest` runs for both build modes
- a Dockerfile that installs `foga` through `uv sync` and native tooling through
  `foga install --target system`

Files:

- [`Dockerfile`](Dockerfile)
- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`cpp/`](cpp)
- [`src/hello_bindings`](src/hello_bindings)
- [`tests/`](tests)
- [`run_example.py`](run_example.py)

Typical usage from the repository root:

```bash
python run-example.py pybind11-profiles
python run-example.py pybind11-profiles --list-steps
python run-example.py pybind11-profiles build-release test-release
```
