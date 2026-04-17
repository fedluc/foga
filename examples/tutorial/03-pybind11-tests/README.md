# 03-pybind11-tests

This example keeps the mixed C++/Python project shape from the previous step
and adds both test workflows and Python linting.

It shows:

- Python tests for the `pybind11` module
- C++ tests driven through `ctest`
- Python `ruff format` and `ruff check` targets
- one `run-foga` helper that exercises install, build, test, and lint

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
./run-foga test
./run-foga lint
```
