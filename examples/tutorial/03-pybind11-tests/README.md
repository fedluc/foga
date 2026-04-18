# 03-pybind11-tests

This example keeps the mixed C++/Python project shape from the previous step
and adds both test workflows and Python linting.

## What You Learn

- how to add testing workflows to a mixed Python and C++ example
- how to run Python tests and C++ tests through one CLI
- how to add formatting and linting checks as part of the same workflow
- how to inspect and clean a more complete example once validation is in place

## Start the example

```bash
./run-example.sh
```

## Inside the container

Run these commands to verify the example:

```bash
foga validate
foga install --target system
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
