# 02-pybind11-hello

This example adds a tiny `pybind11` module while keeping the standalone C++
build separate from the Python package build.

## What You Learn

- how to manage a mixed Python and C++ example with one `foga` config
- how to install native build tools through `foga`
- how to build the C++ and Python sides separately
- how to move from a pure Python example to a simple binding workflow

## Local prerequisites

- Python 3.10+
- `foga`
- a C++ compiler
- CMake
- Ninja

## Run in Docker

From the repository root:

```bash
python examples/tutorial/run-example.py 02-pybind11-hello
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
hello-demo
foga inspect build cpp
```
