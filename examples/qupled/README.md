# qupled

This example shows a mixed Python/C++ project with:

- a standalone C++ CMake build
- a separate Python package build
- multiple pytest runners split by marker
- a `ctest` runner for C++ tests
- profile overrides for MPI and macOS Homebrew OpenMP paths

Files:

- [`foga.yml`](foga.yml)

Use this example when you want to see a config that combines Python workflows,
C++ workflows, hooks for test fixture staging, and real profile overrides.
