---
name: github-issue-workflow
description: Carry repository work through the GitHub branch-and-PR flow. Use when Codex should start from a GitHub issue, continue from an existing branch, or open a pull request for completed work, while keeping branch setup, verification, push, PR creation, and stop conditions consistent.
---

# GitHub PR Workflow

Use this skill when work involves GitHub issues, branches, pushes, or pull
requests. It supports two paths:

- Issue-driven work: choose or use a GitHub issue, create a scoped branch,
  implement, push, and open a PR.
- Existing-branch PR work: verify the current branch, push it, and open or
  update a PR without inventing an issue reference.

## Choose the Path

- If the user names an issue or asks to pick up issue work, use the issue-driven
  path.
- If the user asks to open a PR for the current branch or already-completed
  work, use the existing-branch PR path.
- If the intent is ambiguous, inspect the current branch and recent commits. Ask
  only when it is still unclear whether to start new issue work or open a PR for
  existing work.

## Issue-Driven Work

1. Inspect open issues with `gh` and choose the newest open issue by creation
   time unless the user names a different issue.
2. Read the selected issue carefully and inspect the relevant code before
   editing anything.
3. Fetch the latest remote state and start from the most recent `origin/main`
   unless the user explicitly instructs otherwise.
4. Create a fresh branch from that up-to-date mainline before making changes.
5. Implement the change, run the required verification, and commit the work.
6. Push the branch and open a pull request that references the issue.
7. Stop after the PR is open and wait for the user's comments.

Useful commands:

```bash
gh issue list --state open --search "sort:created-desc" --limit 20
gh issue view <issue-number>
git fetch origin
git checkout main
git merge --ff-only origin/main
git checkout -b issue-<number>-<short-slug>
```

## Existing-Branch PR Work

1. Confirm the worktree is clean or understand any unstaged changes before
   opening the PR.
2. Confirm the branch is not `main`.
3. Inspect the commit range against the intended base, usually `origin/main`.
4. Run or cite the verification required by the changed files.
5. Push the branch and open a PR, or report the existing open PR if one already
   exists.
6. Stop after the PR is open and wait for the user's comments.

Useful commands:

```bash
git status -sb
git diff --stat origin/main...HEAD
gh pr list --head <branch> --state open
git push -u origin <branch>
```

## Branch and PR Rules

- Check `.codex` for repository-local git instructions before changing git state.
- Never do issue work directly on `main`.
- For issue-driven work, create one branch per issue.
- Start new issue branches from the latest remote `main` (`origin/main`) unless
  the user explicitly asks to work from a different base.
- Use a branch name that includes the issue number and a short slug if available.
- Keep each PR scoped to one coherent unit of work.
- Include a concise PR summary and the verification run.
- Include a closing reference such as `Closes #<issue>` only when the PR really
  resolves a GitHub issue.
- Use the repository's configured bot account for commits, pushes, pull
  requests, and PR comments unless the user explicitly asks otherwise.
- Do not merge the PR yourself unless the user explicitly asks.

## Issue Selection Policy

- If a user specifies an issue number or title, use that issue. Report if the
  issue is not open or cannot be found, and stop.
- Default to the newest open issue, not the oldest.
- If labels or milestones make it clear that a different issue should take
  priority, mention that conflict before proceeding.
- If the newest issue is blocked, say why and move to the next viable open issue.
- If there are no open issues, report that clearly and stop.

## Execution Rules

- Use `gh` for issue and PR operations.
- Fetch and sync with the latest remote `main` before creating the work branch
  unless the user explicitly says not to.
- Use the repository's Python skill and repo guidance for implementation,
  formatting, linting, testing, and build checks.
- Use `docs/development.md` as the source of truth for routine verification
  commands; do not maintain a separate command list in this skill.
- Perform a local review pass before opening a PR when the change is substantial.
- Before opening the PR, ensure the local branch contains only changes intended
  for that PR.
- Before creating a PR, check whether one already exists for the branch.
- Write the PR body with:
  - a concise summary
  - verification commands and results
  - an issue-closing reference only when applicable
- After opening the PR, provide the PR number and link, summarize the change,
  summarize verification, and wait for review comments.
