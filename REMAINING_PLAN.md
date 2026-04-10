# Remaining Work for `devkit`

This file captures the parts of the original implementation plan that are still incomplete after the current prototype.

## Current State

Implemented already:

- Standalone `devkit` Python package and CLI
- Root `devkit.yml` config loading
- Basic profile merging
- Built-in command generation for:
  - CMake native builds
  - `python -m build`
  - `pytest`
  - `tox`
  - `ctest`
  - Twine uploads
- Example config derived from the `qupled` workflow
- Initial tests for config parsing, adapter command construction, and CLI routing
- Devcontainer bootstrap for Python and native-tooling dependencies

The current state is a working vertical slice, not a fully finished v1.

## Remaining Product Work

### 1. CLI surface and workflow polish

- Add `devkit inspect` or equivalent command for showing the resolved configuration, active profile, and selected runners/targets.
- Improve `validate` so it reports actionable validation errors and highlights missing required fields more clearly.
- Improve command help text and CLI UX around:
  - profile selection
  - runner/target selection
  - dry-run behavior
  - failure reporting

### 2. Internal adapter contracts

- Refactor the current adapter functions into explicit stable internal contracts for:
  - build backends
  - test backends
  - deploy backends
- Make the adapter boundary more intentional so adding future built-in backends does not require editing CLI flow logic directly.
- Define shared result/error structures where helpful instead of returning only raw command specs.

### 3. Config model and validation

- Strengthen config validation beyond basic type checks:
  - clearer field-path diagnostics
  - backend-specific semantic validation
  - better validation for profile overrides
- Decide and implement explicit precedence rules between:
  - base config
  - profile overrides
  - CLI overrides
- Tighten the “escape hatch” model so hooks/custom commands stay structured and predictable.
- Consider whether validation should remain manual or move to a schema/model library.

### 4. Build/test/deploy workflow semantics

- Implement stronger artifact handoff between workflow stages.
  - Example: explicit wheel artifact discovery and passing artifact paths into later stages.
- Decide how much stage dependency logic should be built in.
  - Example: whether `deploy` can require or verify prior build outputs.
- Improve native test preparation flow so CTest-style runners are modeled as first-class native test stages rather than only command expansion.
- Clarify how Python build and native build should interact when both are configured.

### 5. Deploy model depth

- Expand deploy support beyond minimal Twine upload command generation.
- Improve handling for:
  - repository aliases vs repository URLs
  - artifact selection failures
  - dry-run semantics
  - credentials expectations and environment variable conventions
- Keep the model extensible for future non-PyPI deployment targets without implementing external plugins yet.

## Remaining Quality Work

### 6. End-to-end test coverage

- Add a fixture project that can be exercised through the real `devkit` CLI end to end.
- Cover at least:
  - build flow
  - test flow
  - deploy flow in dry-run or mocked form
- Add a regression-style fixture based on `qupled` expectations to prove the current abstraction covers the original use case.

### 7. CI for this repository

- Add CI to run the test suite automatically.
- At minimum:
  - install the package
  - run `pytest`
  - optionally run a config validation smoke test against the example config

### 8. Documentation

- Expand the README into proper user-facing documentation for:
  - config layout
  - profiles
  - supported backends
  - hooks / escape hatches
  - dry-run usage
- Add a migration note for people moving from repo-specific scripts like `qupled/dev` to `devkit`.

## Suggested Resume Order

1. Refactor adapter contracts and config validation first.
2. Add `inspect` and improve CLI ergonomics.
3. Implement stronger workflow semantics and artifact handoff.
4. Add end-to-end fixture tests.
5. Add CI and improve docs.

## Constraints Chosen So Far

- Project/package/CLI name: `devkit`
- Default config file: `devkit.yml`
- Profiles: basic named profiles, not advanced matrix composition
- First-class v1 backends:
  - CMake
  - `python -m build`
  - `pytest`
  - `tox`
  - `ctest`
  - Twine
- Local developer workflow is prioritized first; CI should reuse the same commands
- No external plugin system in v1
