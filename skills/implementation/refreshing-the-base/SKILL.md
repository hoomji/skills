---
name: refreshing-the-base
description: Measure what moved on the integration branch since a branch was cut, and settle every counter-decision before writing code. Use before starting implementation, when resuming a branch or worktree that has been open a while, when a plan was written against code that may have moved, or when asked whether a branch is up to date.
---

# Refreshing the base

Work written against a stale base can be finished, tested, green, and still wrong. In Gateway-LLM a branch cut at `develop@946bf0a` shipped a `/v1/models` route for a named provider. `develop` had moved 100 commits, and one of them (`c45db49`, "The model catalog becomes ours") had **deleted** `/v1/models` from the gateway and added a test asserting the gateway must never serve it. The same branch also re-fixed an OpenRouter proxy path that `5eb189b` had already fixed. Both were invisible from inside the branch: the tests passed, the types checked, and the text-level merge conflicted in only two files.

Refreshing the base is the pass that finds that before the code is written, not at merge review.

## Drift, and the two kinds of it

**Drift** is everything that landed on the integration branch since the merge-base. Only the drift that intersects your planned change matters — the **blast radius** — and inside it there are two kinds:

- A **textual conflict** is drift git can see. Two edits to the same lines. Git names it, `resolving-merge-conflicts` handles it, and the worst case is an hour.
- A **counter-decision** is drift git cannot see: a change on the base that deletes, forbids, reverses, or already performs what you are about to build. It produces no conflict marker, which is exactly what makes it expensive — it surfaces in review, or in production, as a reviewer asking why you re-added the thing they removed.

Counter-decisions are the whole reason for this pass. A clean `git rebase` is not evidence of their absence.

## Tells of a counter-decision

Read the intersecting commits for these, in order of how loudly they speak:

- **A guard** — a test, lint, or schema asserting the *absence* of the thing you plan to add. The strongest possible signal: someone paid to make this permanent.
- **A deletion** — the file, route, export, column, or flag your plan builds on is gone.
- **A stated decision** — an ADR, spec, or commit body saying which way the choice went. Commit subjects in this house state intent ("The model catalog becomes ours"), so read them as claims, not labels.
- **A rename** — the thing still exists under another name, and your plan cites the dead one.
- **The fix already landed** — someone else solved your problem. Duplicated work is drift too, and it merges silently.

## Steps

1. **Name the integration branch and measure the drift.** Read the branch from the repo rather than assuming `main`:

   ```bash
   gh repo view --json defaultBranchRef -q .defaultBranchRef.name
   git fetch origin
   BASE=origin/develop            # whatever the repo actually merges into
   git merge-base HEAD $BASE
   git log --oneline $(git merge-base HEAD $BASE)..$BASE | wc -l
   git diff --stat $(git merge-base HEAD $BASE)..$BASE | tail -1
   ```

   Done when the merge-base SHA, the commit count, and the changed-file count are written down. Zero commits ends the pass: say so and start implementing.

2. **Cut the drift to the blast radius.** List the files your plan will touch — from the spec, the ticket, or the diff already in the working tree — and intersect them with what moved:

   ```bash
   git diff --name-only $(git merge-base HEAD $BASE)..$BASE > /tmp/drifted
   git diff --name-only $(git merge-base HEAD $BASE) HEAD           # or the plan's file list
   ```

   Widen by concept, not just by path: a plan that adds a route also has a blast radius in the router, the OpenAPI document, and the test that enumerates routes. Grep the base for the identifiers your plan introduces — route paths, exported names, config keys — because a counter-decision often lives in a file your plan never names.

   Done when every intersecting file is listed with the commits that moved it.

3. **Read those commits for the tells.** One verdict per intersecting commit, and quote the evidence:

   ```bash
   git log --oneline $(git merge-base HEAD $BASE)..$BASE -- <path>
   git show <sha> --stat
   ```

   Mark each **compatible**, **textual conflict**, or **counter-decision**. Print the quoted line, guard test name, or commit subject that earned the verdict — a verdict with no citation is a guess.

   Done when every commit in the blast radius carries a verdict and its citation.

4. **Settle every counter-decision before writing code.** A counter-decision is a question about intent, and intent belongs to whoever made the decision. Three honest outcomes: the plan is **withdrawn** (the base already did it, or decided against it), the plan is **reshaped** to live alongside the decision, or the human **overrules** it. Reshaping needs the same evidence as a review would demand — say why the decision does not cover your case, in one sentence, in the plan.

   Do not resolve one by deleting the guard. A guard removed to make room for the change you were told not to make is the failure this pass exists to prevent, wearing a green test suite.

   Done when every counter-decision has one of those three outcomes recorded, and none is still open.

5. **Move onto the current base, then prove it.** Rebase a branch nobody else has pulled; merge when the branch is shared or the drift is large enough that one merge commit reads better than fifty replays. Hand real conflicts to `resolving-merge-conflicts`.

   ```bash
   git rebase $BASE            # or: git merge $BASE
   git merge-base --is-ancestor $BASE HEAD && echo current
   ```

   Then run the repo's checks — including the ones the drift brought with it, since a new guard is only meaningful once it has actually run against your branch.

   Done when `--is-ancestor` reports current and the repo's checks pass, with the output shown.

## When the base cannot be taken

Sometimes refreshing is genuinely blocked: the drift is a half-landed migration, or the base is red. Then say the base is stale, name the counter-decisions found, and let the human choose — and put both in the PR body so the reviewer inherits the finding rather than discovering it. A PR that names its own stale base is a decision waiting for an owner. One that hides it is a trap.
