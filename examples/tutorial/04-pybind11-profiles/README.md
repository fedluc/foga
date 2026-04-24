# 04-pybind11-profiles

This example keeps the mixed C++/Python project shape from the previous example
and adds profile-driven build modes for the C++ side.

## What You Learn

- how to use profiles to switch between debug and release C++ builds
- how to keep one example config while varying build and test behavior by profile
- how to compare default and release workflows from the same tutorial
- how to grow a validated example without duplicating the whole setup

## Local prerequisites

- Python 3.10+
- `foga`
- a C++ compiler
- CMake
- Ninja

## Run in Docker

From the repository root:

```bash
python examples/tutorial/run-tutorial.py 04-pybind11-profiles
```

## Run locally

Install the prerequisites above and work from this directory.

## Steps to execute

Follow these steps to execute the tutorial:

1. Validate the configuration before doing any work:

   ```bash
   foga validate
   ```

   This checks that the base workflows and the `release` profile overrides are
   all valid. Run it first so users know the profile-aware configuration is
   consistent before building anything.

2. Inspect the release C++ build workflow:

   ```bash
   foga inspect --profile release build cpp
   ```

   This shows how the `release` profile changes the `cpp` build target, such as
   the build directory and CMake arguments. It gives users a concrete view of
   what profile selection changes before they compare builds.

3. Install the configured dependencies:

   ```bash
   foga install
   ```

   This installs all configured install targets for this example. That gives
   users both the system-level native build tools from the `system` target and
   the editable Python environment with the development dependencies from the
   `dev` target. After this step, the tutorial is ready for profile-specific
   builds, tests, and linting.

4. Build the Python package:

   ```bash
   foga build python
   ```

   This creates the Python package artifact and compiled extension inputs for
   the bindings side of the example. It keeps the Python packaging workflow
   separate from the profile-specific C++ builds.

5. Build the default C++ configuration:

   ```bash
   foga build cpp
   ```

   This builds the default `cpp` target, which in this tutorial uses the debug
   configuration and writes into `build-cpp-debug/`. It gives users a baseline
   to compare with the release profile.

6. Build the release C++ configuration:

   ```bash
   foga build --profile release cpp
   ```

   This applies the `release` profile and builds the same target into
   `build-cpp-release/` with release-oriented CMake settings. Running it after
   the default build makes the profile switch easy to see.

7. Run the default test workflow:

   ```bash
   foga test
   ```

   This runs the tutorial’s default test setup, including the Python tests and
   the C++ tests configured for the default profile. It shows that the example
   still behaves like the previous tutorial when no profile override is chosen.

8. Run the release C++ tests:

   ```bash
   foga test --profile release cpp
   ```

   This executes only the C++ test runner under the `release` profile, using
   the release-specific test build directory and configure arguments. It is the
   clearest way to compare debug and release behavior from one config.

9. Clean generated artifacts:

   ```bash
   foga clean
   ```

   This removes the debug and release build directories, distributions, and
   tool caches created during the tutorial. It leaves the example ready for
   another pass from a clean state.
