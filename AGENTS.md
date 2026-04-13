# Repository Guidelines

## Project Structure & Module Organization

Application code lives under `src/foga/`. Keep CLI entrypoints in `src/foga/cli.py`, shared config handling in `src/foga/config.py`, execution helpers in `src/foga/executor.py`, and backend-specific command builders in `src/foga/adapters/`. Tests live in `tests/` and currently cover config loading, adapter behavior, and CLI routing. Example user configuration lives in `examples/qupled/foga.yml` and `examples/pybind11/`. Use `README.md` for end-user setup. Track unfinished product work in GitHub issues and milestones.

## Build, Test, and Development Commands

Set up a local environment with:

```bash
pip install -e .[dev]
```

Format the code with:

```bash
ruff format .
```

Run the test suite with:

```bash
pytest
```

Lint the code with:

```bash
ruff check .
```

Validate packaging metadata with:

```bash
python -m build
```

Exercise the CLI during development with commands such as `foga validate`, `foga build --profile mpi`, and `foga deploy --dry-run`. When using the devcontainer, `.devcontainer/post-create.sh` installs the same editable development environment automatically.

Shared Python implementation guidance lives in `skills/python-development/`. Use that skill when editing Python code, tests, packaging metadata, or developer-tooling configuration in this repository.
Shared GitHub execution guidance lives in `skills/github-issue-workflow/`. Use that skill when starting work from GitHub issues or when the task should end with an opened pull request.
Shared PR review coordination guidance lives in `skills/pr-review-loop/`. Use that skill when one agent should review a PR on GitHub and another agent should implement the published comments without relaying them manually in chat.

## Coding Style & Naming Conventions

Target Python 3.10+ and use 4-space indentation. Follow existing module boundaries instead of adding large multi-purpose files. Prefer descriptive snake_case for functions, variables, and test names; keep class names in PascalCase. Match the repository’s current style: small focused functions, straightforward control flow, and minimal comments unless behavior is non-obvious. Run `ruff format .` and `ruff check .` for formatting and linting, and keep diffs consistent with surrounding code.

## Testing Guidelines

Use `pytest` for all tests. Add new tests in `tests/` with filenames named `test_<area>.py` and test functions named `test_<behavior>()`. Cover both happy paths and invalid configuration or command-generation cases. Run `ruff format .`, `ruff check .`, and `pytest` before merging. Run `python -m build` when packaging metadata or install behavior changes. If you change CLI behavior, add or update CLI-facing tests before merging.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `Add devcontainer bootstrap and development docs`. Keep commit titles concise and specific.

Before creating commits or changing git settings, check `.codex/` for repository-local git configuration instructions or other custom workflow notes.

Codex identity: use the repository's configured bot account for repository-local commits, branch pushes, pull request creation, and PR comments or reviews unless the user explicitly asks otherwise.

Development flow: work locally on a dedicated branch. One subprocess implements the change, and a separate subprocess reviews the local diff before any GitHub interaction. Address review findings locally before pushing or opening a pull request.

Pull request flow: after the PR is open, the human user is the reviewer. The human reviews on GitHub, leaves comments, and Codex resumes local development to address that feedback. Repeat the local edit plus internal review loop until the human is satisfied, then the human approves and merges.

When picking up work from GitHub issues, always create a dedicated branch before making changes and open a pull request when the work is complete. Pull requests should explain the user-facing change, note any config or CLI behavior differences, and list the verification performed, for example `ruff format .`, `ruff check .`, `pytest`, `python -m build`, or a representative `foga ... --dry-run` command. Include sample output only when it clarifies behavior. After opening the PR, stop and wait for user feedback instead of continuing automatically.

## Configuration Notes

`foga` expects a root-level `foga.yml`. When adding new configuration fields or adapter behavior, update `README.md` and the examples in `examples/qupled/foga.yml` and `examples/pybind11/` so the documented workflow stays accurate.
