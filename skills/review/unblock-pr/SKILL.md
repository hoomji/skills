---
name: unblock-pr
description: "Address every unresolved review comment on a PR and get its CI green."
disable-model-invocation: true
argument-hint: "PR number or URL (defaults to the current branch's PR)"
---

# Unblock PR

Clear a PR's blockers: every unresolved review thread settled, every red check green. Stop short of merging — the PR is left ready for its author to land.

## 1. Build the work list

Get the real state from `gh`. What a reviewer meant is in their comment; what a check failed on is in its log.

Resolve the PR from `$ARGUMENTS`, or from the current branch (`gh pr view --json number,headRefName,baseRefName`).

**Unresolved threads** — inline threads where `isResolved` is false:

```bash
gh api graphql -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:100) { nodes {
          isResolved isOutdated path line
          comments(first:20) { nodes { author { login } body } }
        } }
      }
    }
  }' -F owner=OWNER -F repo=REPO -F pr=N
```

...plus the top-level review bodies that query misses, human and bot alike: `gh pr view N --json reviews,comments`.

**Red checks** — `gh pr checks N` for which ones, then the log of each: `gh run view <run-id> --log-failed`.

Done when every unresolved thread and every red check is on the list, each carrying the quote or log line it comes from.

## 2. Work each item

**A thread**: make the change it asks for. Where you judge the comment wrong, leave the code and record why — a reasoned decline settles a thread; silence does not.

**A red check**: fix the cause its log points at. Every test and lint rule stays at least as strict as you found it — a check turns green because the code got right. Where the same failure reproduces on the base branch (`gh run list --branch <base>`, or run the check in a worktree at `origin/<base>`), it is pre-existing: record that and leave it.

Done when every item on the list has an outcome — fixed, declined with a reason, or pre-existing.

## 3. Commit and push

Commit in logical chunks, each naming the thread or check it settles, and push to the PR branch. Then `gh pr checks N --watch` until the run finishes.

Reviewers hear back from you in this chat, not on the PR: the replies and the merge belong to the author.

## 4. Report

One line per item, in list order:

```
- @reviewer "use the shared client" → fixed, src/foo.ts:41
- @bot "unused import" → not fixed, it's used by the type-only re-export
- check `unit-tests` → fixed, the mock was missing the new arg
- check `e2e` → pre-existing failure on the base branch, left alone
```

Done when every thread is fixed or answered and every required check is green.
