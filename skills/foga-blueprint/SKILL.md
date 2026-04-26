---
name: foga-blueprint
description: Draft, review, or update `foga.yml` workflow blueprints for a repository. Use when Codex should inspect an existing project, identify its real build, test, docs, format, lint, install, or deploy workflows, map them to supported foga backends, and produce a validated configuration without assuming the foga source tree is present.
---

# Foga Blueprint

Use this skill to translate an existing repository's workflows into a working
`foga.yml`.

## Source of Truth

First determine where the skill is running.

### Inside the foga repository

When the local checkout contains the foga implementation and docs, treat that
checkout as authoritative for:

- current schema
- supported backends
- examples
- CLI behavior

Use local code, local documentation, examples, and CLI help before published
documentation. The checkout may include unreleased changes.

### Outside the foga repository

When the foga source tree is not available:

- Do not assume repo-local foga files or examples exist.
- Treat the published documentation as the schema and behavior source of truth:
  https://fedluc.github.io/foga/
- Use the installed `foga` CLI, when present, to validate and inspect the file.
- If docs and CLI are unavailable, say the config is a best-effort draft.
- Identify any fields that still need verification.

## Supported Backends

Check whether the target repository already uses a supported backend. Confirm
how that workflow is invoked before adding it to `foga.yml`.

- Build: `cmake`, `meson`, `python-build`
- Test: `ctest`, `pytest`, `tox`
- Docs: `doxygen`, `mkdocs`, `sphinx`
- Format: `black`, `clang-format`, `ruff-format`
- Lint: `clang-tidy`, `pylint`, `ruff-check`
- Install: `apt-get`, `brew`, `npm`, `pip`, `poetry`, `uv`, `yum`
- Deploy: `twine`

## Workflow

1. Inspect the repository's existing workflows:
   - build
   - test
   - docs
   - format
   - lint
   - install
   - deploy
   - CI
   - release
2. Identify the real commands users already rely on.
3. Keep separate workflows separate when the repository treats them separately.
4. Map each workflow to the narrowest supported foga backend.
5. Do not infer a backend from language or project type alone.
6. Use built-in backend fields for:
   - arguments
   - paths
   - environment
   - launchers
7. Add hooks only for small setup or cleanup steps that a backend cannot
   express directly.
8. Add profiles only for real environment variants:
   - platform-specific settings
   - local versus CI behavior
   - release mode
   - optional feature sets
9. Validate and inspect the generated config with the available foga CLI.

## Authoring Rules

### Scope and Paths

- Prefer a small base config that users can run immediately.
- Add optional workflows after the base build and test path is clear.
- Keep paths relative to the repository root that will contain `foga.yml`.

### Backend Mapping

- Choose the backend that represents the behavior users rely on.
- Do not choose a backend only because it wraps the command.
- Preserve wrappers when they provide:
  - isolation
  - environment setup
  - matrix behavior
  - a documented entry point
- Use backend fields only where that backend supports them.
- Do not translate tool-native option names into new foga keys.

### Builds and Tests

- For native builds and tests, model the real sequence the project uses.
- If testing needs configure or build work first:
  - include only the required prerequisite work
  - avoid unrelated build steps
- Do not make tests reconfigure or rebuild unless the test command requires it.
- Use explicit build targets only when users intentionally select stable named
  targets.
- Prefer foga-owned build directories, such as `build-foga`.
- Use a project build directory only when the project documents it for this
  workflow.
- For Python packages with native extensions:
  - include `build.python` when it is needed to create the package
  - include the native build backend when it is also required
  - do not drop the Python package build because the native build is complex

### Environment and Installation

- Keep environment variables close to the workflow that needs them.
- Use profiles when values vary by mode.
- Do not use profiles just to group unrelated workflow types.
- Do not encode full bootstrap flows in hooks when the environment already
  handles them.
- Prefer install targets over repeated package-manager commands in hooks.
- Keep dependency installation targets compact and role-based.
- Prefer:
  - requirements files
  - editable local installs
  - documented system packages
- Avoid expanding long dependency inventories from:
  - lock files
  - CI jobs
  - generated metadata
- For pip-style install targets, include at least one install subject:
  - `packages`
  - `path`
- Put requirements-file flags in `args`.
- Do not create a pip target that only has `args: ["-r", "..."]`.

### Hooks

- Put hook commands under `hooks.pre` or `hooks.post`.
- Each hook entry must be a non-empty list of strings.
- Example:

```yaml
hooks:
  pre:
    - ["foga", "install", "--target", "test-env"]
```

- Do not use:
  - shell strings
  - mappings such as `{argv: [...]}`
  - `pre_hooks`
  - `post_hooks`
  - `cd ... && ...`
  - other unsupported shortcut keys

## Validation

- Run `foga validate` against the generated file when the CLI is available.
- Run `foga inspect` to confirm resolved configuration and profile merges.
- Use dry-run commands for configured workflows when the CLI supports them.
- Explain remaining assumptions, including:
  - external system packages
  - credentials
  - platform-specific tools
  - workflows that could not be verified locally
