---
name: pr-review-loop
description: Coordinate a low-noise pull request review loop across agents using GitHub as the handoff surface. Use when one agent should review a PR directly on GitHub and another agent should implement published review comments without relaying feedback manually in chat.
---

# PR Review Loop

Use this skill when review and implementation should happen in separate agent threads, with GitHub PR comments as the source of truth.

## When To Use It

- A reviewer agent should inspect an existing pull request and publish comments on GitHub.
- An implementer agent should read published PR feedback, apply fixes, push updates, and report what changed.
- The user wants to avoid copying comments back and forth between agents.

## Core Rule

GitHub is the handoff surface. Review comments should be published on the PR, and implementation should respond to the published review state rather than chat transcripts.

## Reviewer Workflow

1. Review the PR directly on GitHub, not in chat.
2. Complete a full pass before publishing feedback.
3. Submit one consolidated final review per pass unless the PR changes mid-review.
4. Prefer one canonical comment per issue. Do not duplicate the same feedback across files.
5. Include concrete requested changes, and suggested patches when practical.
6. If no issues are found, approve the PR and note any residual risks briefly.

## Reviewer Comment Rules

- Prefix every comment with one of:
  - `[blocking]`
  - `[non-blocking]`
  - `[nit]`
- Treat `blocking` as correctness, regression, security, contract, or meaningful maintainability issues.
- Treat `non-blocking` as worthwhile fixes that should usually be addressed in the current PR.
- Treat `nit` as optional polish, preferences, or micro-cleanups.
- Avoid speculative comments unless the assumption is stated explicitly.
- Avoid style-only comments already enforced by formatting or linting unless they affect readability materially.

## Reviewer Comment Format

Each substantive comment should contain:

1. Problem
2. Why it matters
3. Requested change

Keep comments short and actionable.

## Implementer Workflow

1. Read the published PR review comments from GitHub.
2. Prioritize `blocking`, then `non-blocking`, then trivial `nit` comments.
3. Ignore resolved threads unless a new commit reopens the issue.
4. Apply the requested fixes, run the relevant verification, and push updates.
5. Summarize which comments were addressed and which were intentionally left unresolved.
6. If a comment is incorrect or based on a false assumption, explain that clearly in the implementation summary or PR reply.

## Prompt Templates

Use the templates in [references/prompts.md](references/prompts.md) as the default prompt text for:

- the reviewer agent
- the implementer agent
- follow-up review passes

## Stopping Conditions

- Reviewer: stop after publishing the review.
- Implementer: stop after pushing fixes and summarizing the result.
- Do not continue into another review round automatically unless the user asks.
