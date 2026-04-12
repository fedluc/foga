# GitHub Commands

Use this reference for the standard issue-to-PR command flow in this repository.

## Select the Issue

Prefer the newest open issue by creation time:

```bash
gh issue list --state open --search "sort:created-desc" --limit 20
```

Read the selected issue in full before starting:

```bash
gh issue view <issue-number>
```

## Create the Branch

Start from the latest remote `main` and create a dedicated issue branch:

```bash
git fetch origin
git checkout main
git merge --ff-only origin/main
git checkout -b issue-<number>-<short-slug>
```

## Implement and Verify

Use the repository verification baseline unless the issue calls for something narrower first:

```bash
ruff format .
ruff check .
pytest
python -m build
```

If one of these is not relevant, say so in the PR.

## Commit and Push

Keep commits scoped to the issue and push the branch before opening the PR:

```bash
git push -u origin issue-<number>-<short-slug>
```

## Open the PR

Open a pull request that references the issue:

```bash
gh pr create --fill --body "## Summary
- <change 1>
- <change 2>

## Verification
- <command 1>
- <command 2>

Closes #<issue-number>"
```

## Stop Condition

After the PR is open:

- report the issue number and PR link
- summarize the implementation and verification
- wait for the user's comments
- do not start a second issue automatically
