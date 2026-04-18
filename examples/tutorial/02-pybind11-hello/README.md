# 02-pybind11-hello

This example adds a tiny `pybind11` module while keeping the standalone C++
build separate from the Python package build.

## What You Learn

- how to manage a mixed Python and C++ example with one `foga` config
- how to install native build tools through `foga`
- how to build the C++ and Python sides separately
- how to move from a pure Python example to a simple binding workflow

## Start the example

```bash
./run-example.sh
```

## Inside the container

Run these commands to verify the example:

```bash
foga validate
foga install --target system
foga build cpp
./build-cpp/hello_cli
foga build python
foga install --target dev
hello-demo
foga inspect build cpp
```
