# numpy

This example shows how to use `foga` to build, test, and document NumPy, the
core array-computing library for Python. It keeps the Meson native build,
Python packaging, pytest, and Sphinx docs in one working configuration.

The example pins NumPy to tag `v2.4.4` to keep the demo reproducible.

## Typical workflow

Start the example container:

```bash
examples/numpy/run-in-docker.py
```

Once inside the container:

1. Validate the configuration before running any workflow:

   ```bash
   foga validate
   ```

2. Build the native and Python artifacts:

   ```bash
   foga build cpp
   foga build python
   ```

3. Run the tests:

   ```bash
   foga test
   ```

4. Build the documentation:

   ```bash
   foga docs
   ```

## What this example demonstrates

- a clear separation between the native build workflow and the Python packaging
  workflow
- `build.cpp` using the `meson` backend independently from `build.python`
- pre-hooks installing the test and docs environments before pytest or Sphinx
  runs

`foga build` also works because this example sets `build.default: all`.
