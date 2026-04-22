# Repository Guidelines

## Project Structure & Module Organization

* Application code lives under `src/foga/`.

  * `src/foga/cli/` contains CLI entrypoints and command wiring
  * `src/foga/config/` contains configuration loading, parsing, and models
  * `src/foga/executor.py` contains command execution orchestration
  * `src/foga/adapters/` contains backend-specific command builders

* Tests live in `tests/` and cover config loading, adapter behavior, and CLI
routing.

* Examples live under `examples/`, especially:

## Development Commands

Set up the environment:

```bash
pip install -e .[dev]
```

Common tasks:

```bash
ruff format .
ruff check .
pytest
python -m build
```

Exercise the CLI during development:

```bash
foga validate
foga build --profile mpi
foga deploy --dry-run
```

## Skills & Source of Truth

This repository relies on shared skills. Use them.

* `python-development`
  Use for changes to Python code, tests, packaging, or tooling.
  This is the source of truth for coding style, testing expectations,
  docstrings, and verification.

* `github-issue-workflow`
  Use when starting from GitHub issues or when the task should end with an
  opened pull request.
  This is the source of truth for branching, issue pickup, and PR flow.

* `pr-review-loop`
  Use when implementing or coordinating GitHub PR review feedback.

If a task matches a skill, follow the skill unless this file gives a
repository-specific override. Repository-specific coding, testing, and GitHub
workflow rules live in these local skill files rather than being repeated here.

## Engineering Principles

### Think Before Coding

Do not jump straight into implementation.

Before writing code:

- state assumptions explicitly
- call out uncertainty instead of guessing
- present multiple interpretations if they exist
- ask questions when requirements are unclear
- identify simpler alternatives and say them out loud
- push back if something seems overengineered or unnecessary

If something is unclear, stop and ask rather than proceeding with a guess.

### Simplicity First

Write the minimum code required to solve the problem.

- do not add features that were not requested
- do not introduce abstractions for single-use cases
- do not add configurability without a real need
- do not handle impossible or irrelevant edge cases
- prefer straightforward, readable solutions over clever ones

Continuously ask:

> Is this the simplest solution a senior engineer would accept?

If not, simplify.
