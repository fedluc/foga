# Getting Started

## Install for development

If you are evaluating `foga` in a local checkout, install it in editable mode:

```bash
pip install -e .[dev]
```

Lint during development with:

```bash
ruff check .
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

## First commands

These examples assume you are running `foga` from a project root that contains
`foga.yml`:

```bash
foga validate                  # Check that foga.yml is well-formed
foga inspect                   # Print the resolved configuration
foga build --dry-run           # Show planned build commands without executing
foga test --dry-run            # Show planned test commands without executing
foga format --dry-run          # Show planned format commands without executing
foga lint --dry-run            # Show planned lint commands without executing
foga deploy --target pypi --dry-run # Preview the deploy command
```

## Adoption workflow

The usual workflow for adopting `foga` in a repository is:

1. Create `foga.yml` with your project name and at least one build or test
   workflow.
2. Run `foga validate` until the configuration passes.
3. Run `foga inspect` to check the merged effective config.
4. Use `foga build --dry-run`, `foga test --dry-run`, `foga format --dry-run`,
   `foga lint --dry-run`, or `foga deploy --dry-run` to inspect generated
   commands before execution.
5. Run the real command once the plan looks right.
6. Add profiles only after the base config is working.

That sequence keeps adoption incremental. You do not need to encode every
project script on day one.
