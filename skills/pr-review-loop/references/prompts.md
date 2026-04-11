# Prompt Templates

## Reviewer Agent

Use this when asking another agent to review an existing PR:

```text
Review PR #<number> directly on GitHub and publish your feedback there, not in chat.

Protocol:
- Complete one full pass before publishing feedback.
- Submit one consolidated review for this pass unless the PR changes while you are reviewing it.
- Prefix every comment with [blocking], [non-blocking], or [nit].
- Only use [blocking] for real correctness, regression, security, contract, or important maintainability issues.
- Avoid duplicate comments for the same issue.
- For each substantive comment, state:
  1. Problem
  2. Why it matters
  3. Requested change
- If you find no issues, approve the PR and add a brief residual-risk note instead of inventing comments.
```

## Implementer Agent

Use this when asking the implementation agent to address feedback:

```text
Read all currently published review comments on PR #<number> and address them.

Rules:
- Use GitHub as the source of truth, not chat summaries.
- Prioritize [blocking], then [non-blocking].
- Ignore [nit] comments unless they are trivial or clearly worth including.
- Ignore resolved threads unless there is a new unresolved follow-up.
- Push fixes to the same branch.
- Summarize:
  - which comments you addressed
  - any comments you intentionally left unresolved
  - the verification you ran
```

## Follow-Up Review Pass

Use this when asking the reviewer to review an updated PR:

```text
Review the latest state of PR #<number> directly on GitHub and publish one final review for this pass.

Focus only on:
- unresolved prior concerns
- regressions introduced by the latest commits
- new issues in the updated diff

Do not repeat comments that are already resolved.
If no further issues remain, approve the PR.
```
