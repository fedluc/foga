# Profiles And Hooks

## Profiles

Profiles let one repository express environment-specific differences without
copying the entire config. Apply them with `--profile <name>`.

Example:

```yaml
profiles:
  mpi:
    build:
      cpp:
        configure_args:
          - -DBUILD_CPP_TESTS=OFF
          - -DUSE_MPI=ON
      python:
        env:
          USE_MPI: "ON"
```

Use profiles for:

- CI versus local development
- MPI versus non-MPI builds
- platform-specific environment variables
- release-only deployment settings

Profile merge rules are intentionally conservative:

- profile overrides may replace values and extend nested mappings
- they must preserve the container type of existing paths
- they cannot change the backend identifier of an already configured workflow

## Hooks

Hooks are the supported escape hatch when a workflow needs a small amount of
custom orchestration around a built-in backend command.

Hook shape:

```yaml
test:
  runners:
    integration:
      backend: pytest
      path: tests
      hooks:
        pre:
          - ["python3", "tools/prepare_integration.py"]
        post:
          - ["python3", "tools/cleanup_integration.py"]
```

Supported behavior:

- only `hooks.pre` and `hooks.post` are supported
- each hook entry must be a non-empty command array
- hooks run directly without shell parsing
- hooks execute around the generated backend command

Intentionally unsupported:

- shell strings such as `"make build && make test"`
- per-hook mappings such as `cwd`, `shell`, `argv`, or inline `env`
- turning the config file into a generic task runner

If logic is complex, keep it in a project script and call that script from a
hook.
