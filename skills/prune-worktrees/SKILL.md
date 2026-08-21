---
name: prune-worktrees
description: Remove git worktrees and branches whose content is fully subsumed by a target branch (usually main or develop) - safe cleanup after branches get picked up, squash-merged, or rebased elsewhere so a plain ancestor check misses them. Use for "clean up my worktrees", "prune merged branches", "worktree cleanup", "delete stale branches", or when `git worktree list` has piled up. Do NOT use to abort or force through an in-progress merge/rebase (see resolving-merge-conflicts), and do not run it as a matter of routine - only when asked.
---

# Prune worktrees

Deletes worktrees and branches, so every verdict below is proved, never assumed. A branch is **subsumed** when every file its unique commits touch is byte-identical between the branch and the target - the leading word for the rest of this skill. `git merge-base --is-ancestor` alone under-detects this: a branch picked up, squash-merged, or rebased into the target keeps unique commits whose *content* landed even though the commits themselves didn't.

## Step 1: Confirm the target branch

Ask if not obvious from context: which branch is the integration target (`main`, `develop`, ...)? Fetch it fresh (`git fetch origin <target>`) before anything else - a stale local copy makes every subsequent verdict wrong.

## Step 2: Enumerate the candidates

`git worktree list` for worktrees, `git branch -vv` for branches without one. Every entry gets a verdict before anything is touched; skip nothing.

## Step 3: Verify subsumption, per candidate

Run in order, cheapest first, and stop at the first that decides it:

1. **Ancestor check.** `git merge-base --is-ancestor <branch> <target>`. Ancestor → subsumed, done.
2. **Touched-file diff.** Not an ancestor doesn't mean not subsumed - it means check harder:
   ```
   mb=$(git merge-base <target> <branch>)
   files=$(git diff --name-only "$mb" "<branch>")
   git diff <target> <branch> -- $files
   ```
   Empty output → every file the branch's own commits changed already matches the target's current content → subsumed. A non-empty `--stat` from comparing whole trees is expected and irrelevant here (the target has moved on in files the branch never touched); only the touched-file diff decides it.
3. **Working-tree state**, worktrees only. `git -C <worktree> status --porcelain=v1`. Uncommitted changes don't override a subsumed verdict by themselves - diff those specific paths against the target the same way. Untracked build output (`node_modules`, `dist`) is never evidence either way; ignore it. An unresolved merge/rebase (`UU` entries) with an otherwise-subsumed tip is abandoned scratch state, not new work - subsumed still stands, unless the conflicting file's target-side content doesn't already contain what the working copy was trying to add.

Every subsumed verdict must cite what was checked (which command, what it returned) - "looks old" or "probably fine" is not a verdict.

## Step 4: Remove only what step 3 cleared

For each subsumed candidate:
```
git worktree remove [--force] <path>       # --force only for an in-progress-merge worktree already found subsumed in step 3
git branch -d <branch>                     # -D if step 3's ancestor check said no but the diff check said subsumed anyway
git push origin --delete <branch>          # if a matching remote ref exists
```
Leave everything not cleared exactly as it is - report it with the reason (which check failed and how) instead of touching it. Never fall back to force-deleting an unverified candidate just to finish the sweep.

## Step 5: Report

One line per candidate: kept or removed, and why. A worktree with real, non-subsumed changes is a finding to hand back to the user, not a blocker to route around.
