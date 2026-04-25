# arrow

This example shows how to use `foga` to build, test, and document Apache
Arrow, the columnar data platform. It combines system package installation, a
native CMake build, Python installs, pytest, and Sphinx docs in one working
configuration.

The example pins Arrow to commit `36c8c9a` (`apache-arrow-24.0.0.dev-318-g36c8c9a24a`)
to keep the demo reproducible.

## Typical workflow

Start the example container:

```bash
examples/arrow/run-in-docker.py
```

Once inside the container:

1. Validate the configuration before running any workflow:

   ```bash
   foga validate
   ```

2. Build the Arrow C++ targets:

   ```bash
   foga build cpp
   ```

3. Install the Python test environment and run tests:

   ```bash
   foga install --target test-env
   foga test
   ```

4. Build the arrow documentation through the configured docs workflow:

   ```bash
   foga docs
   ```

## What this example demonstrates

- one config coordinating system setup, native build, Python install, tests,
  docs, and cleanup
- a credible upstream integration instead of a toy repository
- heavier docs handling, where `foga docs` rebuilds Arrow C++ with a docs
  profile and reinstalls `docs-env` in pre-hooks before running Sphinx
