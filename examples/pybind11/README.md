# pybind11

This example shows how to use `foga` to build, test, and document pybind11,
the C++ bindings library for exposing native code to Python.

The Docker image clones `pybind11` at pinned commit `2889136` to keep the
example reproducible.

## Typical workflow

Start the example container:

```bash
examples/pybind11/run-in-docker.py
```

Once inside the container:

1. Validate the configuration before running any workflow:

   ```bash
   foga validate
   ```

2. Build the default C++ target, then rebuild it with the `release` profile:

   ```bash
   foga build cpp
   foga build --profile release cpp
   ```

3. Run the some tests:

   ```bash
   foga test
   ```

4. Build the documentation through the configured docs workflow:

   ```bash
   foga docs
   ```

## What this example demonstrates

- a self-contained Docker workflow for a real upstream C++/Python project
- `foga install` provisioning default Python and system build dependencies
- a lighter upstream demonstration than Arrow, while still exercising builds,
  tests, docs, and profiles
