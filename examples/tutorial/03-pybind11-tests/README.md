# 03-pybind11-tests

This example keeps the mixed C++/Python project shape from the previous step
and adds both test workflows and Python linting.

The `generator: Ninja` entries tell `foga` to pass `-G Ninja` during the CMake
configure step for both the C++ build workflow and the `ctest` preparation
workflow.

## What You Learn

- how to add testing workflows to a mixed Python and C++ example
- how to run Python tests and C++ tests through one CLI
- how to add formatting and linting checks as part of the same workflow
- how to inspect and clean a more complete example once validation is in place

## Local prerequisites

- Python 3.10+
- `foga`
- a C++ compiler
- CMake
- Ninja

## Run in Docker

From the repository root:

```bash
python examples/tutorial/run-tutorial.py 03-pybind11-tests
```

Once the container starts, install the system packages required by the example:

```bash
foga install --target system
```

## Run locally

Install the prerequisites above and work from this directory.

## Commands to run

```bash
foga validate
foga install --target dev
foga build cpp
./build-cpp/hello_cli
foga build python
foga test
foga format --dry-run
foga lint
foga inspect test
foga clean
```
