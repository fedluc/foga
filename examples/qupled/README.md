# qupled

This example shows a mixed Python/C++ project with:

- a standalone native CMake build
- a separate Python package build
- multiple pytest runners split by marker
- a `ctest` runner for native C++ tests
- profile overrides for MPI and macOS Homebrew OpenMP paths

Files:

- [`foga.yml`](foga.yml)

Use this example when you want to see a config that combines Python workflows,
native workflows, hooks for test fixture staging, and real profile overrides.
