# Configuration Overview

## Required sections

- `project`: project metadata

## Optional sections

- `build`: build workflows
- `test`: test workflows
- `docs`: docs workflows
- `format`: format workflows
- `lint`: lint workflows
- `install`: installation workflows
- `deploy`: deployment workflows
- `clean`: cleanup targets
- `profiles`: named overrides applied on top of the base config

## How to read this reference

- Search [Top-level sections](top-level.md) when you need the container shape
  and a short YAML example for `build`, `test`, `install`, or another
  top-level key.
- Search [Backends](backends.md) by backend name such as `pytest`, `cmake`,
  `pip`, or `twine` when you need the exact configurable fields and a minimal
  backend example.
- Search [Profiles And Hooks](profiles-and-hooks.md) when you need override
  rules, hook behavior, or the boundary between built-in workflows and custom
  scripts, with short examples for both features.

```{toctree}
:maxdepth: 1
:hidden:

top-level
backends
profiles-and-hooks
```
