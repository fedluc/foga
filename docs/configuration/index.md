# Configuration Overview

`foga.yml` describes repeatable repository workflows. Each top-level workflow
section, such as `build`, `test`, or `docs`, declares one or more configured
workflows. Each workflow chooses a backend, and the backend determines the
fields that are valid for that workflow.

Profiles apply named overrides on top of the base configuration. Hooks add
small pre- or post-commands around generated backend commands when a project
needs custom orchestration.

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

- Read [Top-level sections](top-level.md) for the shape of each major
  `foga.yml` section and short YAML examples.
- Read [Backends](backends.md) for backend-specific fields and examples.
- Read [Profiles and hooks](profiles-and-hooks.md) for override behavior and
  supported customization points.

Use `foga validate` after editing `foga.yml`, and `foga inspect` when you need
to see the resolved configuration after profiles and defaults are applied.

```{toctree}
:maxdepth: 1
:hidden:

top-level
backends
profiles-and-hooks
```
