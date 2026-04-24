# 03-pybind11-tests

This example keeps the mixed C++/Python project shape from the previous step
and adds both test workflows and Python linting.

The `generator: Ninja` entries tell `foga` to pass `-G Ninja` during the CMake
configure step for both the C++ build workflow and the `ctest` preparation
workflow.

## What You Learn

- how to add testing workflows to a mixed Python and C++ example
- how to run Python tests and C++ tests through one CLI
- how to add linting checks as part of the same workflow
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

## Run locally

Install the prerequisites above and work from this directory.

## Steps to execute

Follow these steps to execute the tutorial:

1. Validate the configuration before doing any work:

   ```bash
   foga validate
   ```

   This checks that the build, test, format, and lint workflows declared in
   `foga.yml` are valid. Run it first so users catch configuration issues before
   they start installing tools or running jobs.

2. Inspect the test workflow:

   ```bash
   foga inspect test
   ```

   This prints the resolved test configuration, including the Python `pytest`
   runner and the C++ `ctest` runner. It gives users a clear picture of what
   `foga test` will execute later.

3. Install the configured dependencies:

   ```bash
   foga install
   ```

   This installs all configured install targets for this example. In practice,
   that means the system toolchain from the `system` target and the editable
   Python environment plus `pytest` and `ruff` from the `dev` target. After
   this step, the example is ready for native builds, tests, and Python
   code-quality checks.

4. Build the standalone C++ executable:

   ```bash
   foga build cpp
   ```

   This configures and builds the native `hello_cli` target into `build-cpp/`.
   It keeps the executable workflow explicit before the tutorial moves on to the
   Python and test layers.

5. Run the C++ executable directly:

   ```bash
   ./build-cpp/hello_cli
   ```

   This confirms that the native binary runs correctly on its own. It is a good
   checkpoint before adding test execution on top.

6. Build the Python package:

   ```bash
   foga build python
   ```

   This produces the Python package artifact and compiled extension for the
   bindings. It prepares the Python side so the test workflow can exercise it.

7. Run all tests through one command:

   ```bash
   foga test
   ```

   This runs both configured test runners: Python unit tests via `pytest` and
   C++ tests via `ctest`. It demonstrates the main point of this tutorial: one
   `foga` command can coordinate both ecosystems.

8. Run lint checks:

   ```bash
   foga lint
   ```

   This executes the configured `ruff check` target against the Python sources
   and tests. It shows how style and static checks can live next to build and
   test commands in the same config.

9. Clean generated artifacts:

   ```bash
   foga clean
   ```

   This removes the build directories, distributions, and tool caches created
   during the tutorial. It gives users a clean workspace and shows how the
   example defines its cleanup policy in `foga.yml`.

10. Build the C++ executable again from a clean state:

   ```bash
   foga build cpp
   ```

   This reruns the native build after `foga clean` has removed the generated
   artifacts. Users can see that the C++ workflow starts again from fresh,
   recreating `build-cpp/` instead of reusing the previous build output.
