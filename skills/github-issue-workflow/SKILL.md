---
name: github-issue-workflow
description: Pick up repository work directly from GitHub issues and carry it through the full branch-and-PR flow. Use when Codex should inspect open GitHub issues, choose the newest open issue to work on, create a dedicated branch, implement the change, push the branch, open a pull request, and then stop and wait for user review comments instead of continuing automatically.
---

# GitHub Issue Workflow

Use this skill when work should start from the GitHub backlog rather than from an inline user request.

## Workflow

1. Inspect open issues with `gh` and choose the newest open issue by creation time unless the user names a different issue.
2. Read the selected issue carefully and inspect the relevant code before editing anything.
3. Fetch the latest remote state and start from the most recent `origin/main` unless the user explicitly instructs otherwise.
4. Create a fresh branch from that up-to-date mainline for the issue before making changes.
5. Implement the change, run the required verification, and commit the work.
6. Push the branch and open a pull request that references the issue.
7. Stop after the PR is open and wait for the user's comments.

## Branch and PR Rules

- Never do issue work directly on `main`.
- Create one branch per issue.
- Start that branch from the latest remote `main` (`origin/main`) unless the user explicitly asks to work from a different base.
- Use a branch name that includes the issue number and a short slug.
- Keep the PR scoped to the selected issue.
- Include a concise PR summary, the verification run, and a closing reference such as `Closes #<issue>`.
- Do not merge the PR yourself unless the user explicitly asks.

## Issue Selection Policy

- Default to the newest open issue, not the oldest.
- If labels or milestones make it clear that a different issue should take priority, mention that conflict before proceeding.
- If the newest issue is blocked, say why and move to the next viable open issue.
- If there are no open issues, report that clearly and stop.

## Execution Rules

- Use `gh` for issue and PR operations.
- Fetch and sync with the latest remote `main` before creating the work branch unless the user explicitly says not to.
- Use the repository's Python skill and repo guidance for implementation, formatting, linting, testing, and build checks.
- Before opening the PR, ensure the local branch contains only changes for the chosen issue.
- After opening the PR, provide the PR number and link, summarize the change, summarize verification, and wait for review comments.

## References

- Read [references/github-commands.md](references/github-commands.md) for the standard command sequence and PR checklist used by this skill.
