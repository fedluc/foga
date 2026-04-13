# Releasing foga

This document describes the maintainer workflow for publishing `foga` to PyPI.

Publishing is automated through [`.github/workflows/publish.yml`](.github/workflows/publish.yml).
The workflow runs when a Git tag matching `v*` is pushed, for example `v0.2.0`.

## Prerequisites

Before the first release, make sure PyPI trusted publishing is configured:

- create the `foga` project on PyPI if it does not already exist
- configure a PyPI Trusted Publisher for this GitHub repository
- point the trusted publisher at the `Publish` workflow and the `pypi`
  environment

The workflow uses GitHub OIDC, so no long-lived PyPI API token is required.

## Release Checklist

1. Make sure the intended release changes are merged to `main`.
2. Update the version in [`pyproject.toml`](pyproject.toml).
3. Run the standard verification commands locally:

```bash
python -m pytest
python -m build
```

4. Commit the version bump on a normal branch and merge it to `main`.
5. Create a release tag from the release commit:

```bash
git checkout main
git pull --ff-only origin main
git tag v0.2.0
git push origin v0.2.0
```

6. Watch the `Publish` workflow in GitHub Actions.
7. Confirm the release appears on PyPI.

## Versioning

Use semantic version tags that match the package version in `pyproject.toml`.

Examples:

- package version `0.2.0` -> Git tag `v0.2.0`
- package version `1.0.1` -> Git tag `v1.0.1`

Do not create a tag whose version differs from `pyproject.toml`.

## What The Workflow Does

When a matching tag is pushed, the workflow:

1. checks out the tagged commit
2. installs the project with development dependencies
3. runs `ruff check .`
4. runs `pytest`
5. runs `python -m build`
6. uploads the built distributions between jobs
7. publishes the distributions to PyPI

The workflow also supports manual dispatch if a maintainer needs to rerun it.

## Verifying A Release

After the workflow completes:

- check the GitHub Actions run for the tagged release
- confirm the package version is visible on PyPI
- optionally install the new version in a clean environment:

```bash
pip install --upgrade foga==0.2.0
foga --help
```

## If A Release Fails

If the workflow fails before publishing:

- fix the problem on a branch
- merge the fix to `main`
- delete and recreate the tag only if the package was not published

If the package was already published to PyPI:

- do not try to overwrite the same version
- prepare a new patch release instead, for example `0.2.1`
- update `pyproject.toml`, tag the new version, and publish again
