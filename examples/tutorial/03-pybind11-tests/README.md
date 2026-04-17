# 03-pybind11-tests

This example keeps the mixed C++/Python project shape from the previous step
and adds both test workflows and Python linting.

It shows:

- Python tests for the `pybind11` module
- C++ tests driven through `ctest`
- Python `ruff format` and `ruff check` targets
- a Dockerfile that installs the native build toolchain through `foga install`

Files:

- [`Dockerfile`](Dockerfile)
- [`foga.yml`](foga.yml)
- [`pyproject.toml`](pyproject.toml)
- [`cpp/`](cpp)
- [`src/hello_bindings`](src/hello_bindings)
- [`tests/`](tests)
- [`run-foga`](run-foga)

Typical usage from the repository root:

```bash
python run-example.py pybind11-tests
python run-example.py pybind11-tests test
python run-example.py pybind11-tests lint
```
