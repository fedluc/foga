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
python examples/tutorial/run-tutorial.py 02-pybind11-hello
```

## Run locally

Install the prerequisites above and work from this directory.

## Steps to execute

Follow these steps to execute the tutorial:

1. Validate the configuration before doing any work:

   ```bash
   foga validate
   ```

   This checks that `foga.yml` is valid and that both the C++ and Python
   workflows can be resolved by `foga`. Run it first so configuration problems
   show up before any install or build step.

2. Inspect the C++ build workflow:

   ```bash
   foga inspect build cpp
   ```

   This shows the resolved CMake-based build configuration for the `cpp`
   target, including the source directory, build directory, generator, and
   target name. It helps users understand what `foga build cpp` is going to do.

3. Install the system toolchain required for the native build:

   ```bash
   foga install --target system
   ```

   This installs the OS-level packages declared in `foga.yml`, including the
   compiler toolchain, CMake, and Ninja. Users get the native build tools
   needed for `foga build cpp`, without having to install each package by hand.

4. Install the development environment:

   ```bash
   foga install --target dev
   ```

   This installs the Python package in editable mode together with the build
   dependencies declared in `pyproject.toml`. After this step, users have the
   Python side of the project ready for local iteration.

5. Build the standalone C++ executable:

   ```bash
   foga build cpp
   ```

   This configures and builds the native `hello_cli` target into `build-cpp/`.
   It demonstrates that `foga` can drive the C++ workflow separately from the
   Python packaging workflow.

6. Run the C++ executable directly:

   ```bash
   ./build-cpp/hello_cli
   ```

   This lets users confirm that the native binary works on its own before they
   move to the Python bindings. It makes the separation between the C++ and
   Python deliverables concrete.

7. Build the Python package:

   ```bash
   foga build python
   ```

   This uses the Python build backend to create the package artifact in `dist/`
   and the wheel build directory. It shows the second half of the mixed project
   layout: packaging the bindings for Python users.

8. Run the Python entrypoint:

   ```bash
   hello-demo
   ```

   This executes the console script that calls into the compiled extension
   module. Users should see the Python command invoke the same greeting logic
   through the bindings, which confirms that the Python package and native code
   are wired together correctly.
