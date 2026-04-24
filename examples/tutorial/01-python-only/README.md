# 01-python-only

This is the smallest runnable `foga` example in the repository.

## What You Learn

- how to start from a minimal `foga` project
- how to validate a config before running workflows
- how to build and install a Python package through `foga`

## Local prerequisites

- Python 3.10+
- `foga`

## Run in Docker

From the repository root:

```bash
python examples/tutorial/run-tutorial.py 01-python-only
```

## Run locally

Install the prerequisites above and work from this directory.

## Steps to execute

Follow these steps to execute the tutorial:

1. Validate the configuration before doing any work:

   ```bash
   foga validate
   ```

   This checks that `foga.yml` is valid and that the example can be resolved by
   `foga`. Run it first so users get fast feedback if the configuration is
   broken.

2. Inspect the resolved configuration:

   ```bash
   foga inspect
   ```

   This prints the resolved `foga` configuration so users can see how `foga`
   interprets the example after validation succeeds. It helps them connect the
   tutorial files to the workflows they are about to run.

3. Install the development environment:

   ```bash
   foga install --target dev
   ```

   This installs the project in editable mode from `.` together with the Python
   dependencies declared in `pyproject.toml`. After this step, the
   `vector-demo` command should be available in the active environment.

4. Build the package artifact:

   ```bash
   foga build
   ```

   This runs the configured Python build backend and produces a distributable
   package in `dist/`. It shows the difference between an editable development
   install and the packaged output users would publish or ship.

5. Run the example application:

   ```bash
   vector-demo
   ```

   This executes the console script exposed by the package. Users should see the
   centered-norm output, which confirms that the package, its dependencies, and
   the installed entrypoint all work together.
