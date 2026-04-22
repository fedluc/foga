# Getting Started

## Install

Install `foga` with

```bash
pip install foga
```

## Minimal config

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

If you want a runnable repository to copy from instead of starting from a blank
file, use the [tutorial examples](examples/tutorials.md). They follow the same
incremental adoption path and include working project files.

## Adoption workflow

The usual workflow for adopting `foga` in a repository is:

1. Create `foga.yml` with your project name and at least one build or test
   workflow.
2. Run `foga validate` until the configuration passes.
3. Run `foga inspect` to check the merged effective config, or a command-specific
   inspect such as `foga inspect test` to preview the resolved workflow and
   planned commands.
4. Use a dry-run command such as `foga build --dry-run` or
   `foga test --dry-run` when you want the execution-oriented preview of the
   exact commands that would run.
5. Run the real command once the plan looks right.
6. Add profiles only after the base config is working.

That sequence keeps adoption incremental. You do not need to encode every
project script on day one.

These examples assume you are running `foga` from a project root that already
contains `foga.yml`:

```bash
foga validate                  # Check that foga.yml is well-formed
foga inspect                   # Print the resolved configuration
foga inspect format            # Inspect selected format config and commands
foga build --dry-run           # Show planned build commands without executing
foga test --dry-run            # Show planned test commands without executing
foga docs --dry-run            # Show planned docs commands without executing
foga format --dry-run          # Show planned format commands without executing
foga lint --dry-run            # Show planned lint commands without executing
foga install --dry-run         # Show planned install commands without executing
foga deploy --target pypi --dry-run # Preview the deploy command
```

### Authoring with agents

Agentic tools can help draft `foga.yml` quickly when you already have build,
test, docs, or deploy scripts in a repository.

Recommended approach:

1. Give the agent the current commands or CI snippets that already work.
2. Ask it to map those commands to built-in `foga` backends before it reaches
   for hooks.
3. If your tool supports local skills, use [`skills/foga-config-authoring/SKILL.md`](https://github.com/fedluc/foga/blob/main/skills/foga-config-authoring/SKILL.md) to produce the initial config or a first draft.
4. Review the result with `foga validate`, `foga inspect`, and dry-run output.

That keeps the generated config close to the structure `foga` actually expects.

## Practical limitations

`foga` works best for repeatable repository workflows. It is a worse fit for:

- long one-time bootstrap flows
- infrastructure provisioning
- large shell pipelines that depend on shell parsing
- commands that are so project-specific that a small script is clearer than YAML

Use hooks for small orchestration steps. Keep genuinely complex logic in a
project script and call that script from `foga`.
