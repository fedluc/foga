# 04-pybind11-profiles

This example keeps the tested mixed C++/Python project shape and adds
profile-driven build modes for the C++ side.

It shows:

- a default debug-oriented C++ build
- a `release` profile with a separate build directory and `Release` flags
- matching `ctest` runs for both build modes
- the same Python package, tests, and linting flow as the previous step

Files:

- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`cpp/`](cpp)
- [`src/hello_bindings`](src/hello_bindings)
- [`tests/`](tests)
- [`run-foga`](run-foga)

Typical usage:

```bash
./run-foga
./run-foga inspect --profile release build cpp
./run-foga test --profile release cpp
```
