# CLI Reference

## Validate

Use `foga validate` to catch malformed config early:

```bash
foga validate                              # Validate the default ./foga.yml
foga --config path/to/foga.yml validate    # Validate a specific config file
```

This is the first command to run after editing the configuration.

## Build

Use `foga build` to run configured build workflows:

```bash
foga build --dry-run                                # Preview all configured build workflows
foga build python --dry-run                         # Preview only the Python package build
foga build native --target native_tests --dry-run   # Preview one native target explicitly
foga build all --profile mpi --dry-run              # Preview builds with the mpi profile applied
```

## Test

Use `foga test` to run one or more configured test runners:

```bash
foga test --dry-run                            # Preview all configured test workflows
foga test python --runner unit --dry-run       # Preview only the Python runner named "unit"
foga test native --dry-run                     # Preview only native test workflows
foga test --profile mpi --dry-run              # Preview test commands with the mpi profile
```

## Deploy

Use `foga deploy` to run deployment targets:

```bash
foga deploy --target pypi --dry-run    # Preview the pypi upload command
```

## Clean

Use `foga clean` to remove configured generated paths:

```bash
foga clean   # Remove the paths listed under clean.paths
```

## Inspect

Use `foga inspect` to print the resolved configuration without executing
commands:

```bash
foga inspect                                     # Print the full resolved config
foga inspect --profile mpi                       # Inspect after applying mpi
foga inspect build native --target native_tests  # Inspect native build selection
foga inspect test python --runner unit           # Inspect the selected test runner
foga inspect deploy --target pypi                # Inspect one deploy target
foga inspect --full build native                 # Show the full document for build
```

Top-level `foga inspect` prints the full resolved config. Command-specific
inspection prints a concise summary plus the relevant config fragment unless
`--full` is set.

## Dry-run

Dry-run mode is the safest way to adopt `foga` in an existing repository.

Available dry-run commands:

- `foga build --dry-run`
- `foga test --dry-run`
- `foga deploy --dry-run`

Dry-run output shows the planned commands without executing them. Use it to
verify:

- the selected profile
- target or runner filtering
- generated backend arguments
- hook ordering
- working assumptions before changing CI or repository scripts

## Override precedence

`foga` resolves configuration in this order:

1. Base `foga.yml`
2. Selected profile overrides from `profiles.<name>`
3. CLI overrides for the active command

CLI overrides are execution-scoped. They do not rewrite the config file.
