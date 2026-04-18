# 01-python-only

This is the smallest runnable `foga` example in the repository.

## What You Learn

- how to start from a minimal `foga` project
- how to validate a config before running workflows
- how to build and install a Python package through `foga`
- how to exercise the example in an isolated container without touching the host

## Start the example

```bash
./run-example.sh
```

## Inside the container

Run these commands to verify the example:

```bash
foga validate
foga build
foga install --target dev
vector-demo
foga inspect
```
