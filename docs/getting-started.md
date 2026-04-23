# Getting Started

This guide shows how to create a minimal `foga.yml`, validate it, preview the
commands it would run, and then run configured workflows.

## Install

Install `foga` with

```bash
pip install foga
```

Then check what version you installed with `foga --version`. 

## Create the first config

You can start with a small hand-written config, or ask an agent to draft one
from commands your project already uses.

### Start from a minimal config

Add a root-level `foga.yml` file to your project and start with a small
configuration:

```yaml
project:
  name: demo

build:
  python:
    backend: python-build

test:
  runners:
    unit:
      backend: pytest
      path: tests
```

This config declares the project name, a Python package build using the
`python-build` backend, and a pytest runner named `unit`.

If you want a runnable repository to copy from instead of starting from a blank
file, use the [tutorial examples](examples/tutorials.md). They follow an
incremental adoption path and include working project files.

### Start with an agent

If your repository already has working build, test, docs, or deploy commands,
an agent can draft the first `foga.yml` for you. Give it the current commands,
Make targets, CI snippets, or README instructions that already work, then ask
it to map them to built-in `foga` backends before using hooks.

If your tool supports local skills, use the provided
[`foga-config-authoring` skill](https://github.com/fedluc/foga/blob/main/skills/foga-config-authoring/SKILL.md)
to produce the initial config or a first draft.

After the draft is generated, review it with `foga validate`, `foga inspect`,
and dry-run output before replacing existing project workflows.

## Validate and preview

After you have a `foga.yml`, use this sequence to adopt `foga` incrementally:

1. Run `foga validate` until the configuration passes.
2. Run `foga inspect` to check the merged effective config, or a command-specific
   inspect such as `foga inspect test` to preview the resolved workflow and
   planned commands.
3. Use a dry-run command such as `foga build --dry-run` or
   `foga test --dry-run` when you want the execution-oriented preview of the
   exact commands that would run.
4. Run the real command once the plan looks right.
5. Add profiles only after the base config is working.

That sequence keeps adoption incremental. You do not need to encode every
project script on day one.

From the project root that contains `foga.yml`, start with these commands:

```bash
foga validate          # Check that foga.yml is well-formed
foga inspect           # Print the resolved configuration
foga build --dry-run   # Show planned build commands without executing
foga test --dry-run    # Show planned test commands without executing
```

Use [CLI Usage](cli.md) for the full command set, including docs,
format, lint, install, deploy, and clean workflows.

## Practical limitations

`foga` works best for repeatable repository workflows. It is a worse fit for:

- long one-time bootstrap flows
- infrastructure provisioning
- large shell pipelines that depend on shell parsing
- commands that are so project-specific that a small script is clearer than YAML

Use hooks for small orchestration steps. Keep genuinely complex logic in a
project script and call that script from `foga`.

## Next steps

- Read the [Configuration Overview](configuration/index.md) to understand the
  available `foga.yml` sections.
- Use the [Examples](examples/index.md) when you want complete reference
  configurations.
- Use [CLI Usage](cli.md) when you need command options and filtering
  behavior.
