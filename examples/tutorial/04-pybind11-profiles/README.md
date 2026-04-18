# 04-pybind11-profiles

This example keeps the mixed C++/Python project shape from the previous example
and adds profile-driven build modes for the C++ side.

## What You Learn

- how to use profiles to switch between debug and release C++ builds
- how to keep one example config while varying build and test behavior by profile
- how to compare default and release workflows from the same tutorial
- how to grow a validated example without duplicating the whole setup

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
foga build python
foga build cpp
foga build --profile release cpp
foga test
foga test --profile release cpp
foga format --dry-run
foga lint
foga inspect --profile release build cpp
foga clean
```
