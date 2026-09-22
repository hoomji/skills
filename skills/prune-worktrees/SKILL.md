---
name: prune-worktrees
description: Remove git worktrees and branches whose content is fully subsumed by a target branch (usually main or develop) - safe cleanup after branches get picked up, squash-merged, or rebased elsewhere so a plain ancestor check misses them. Use for "clean up my worktrees", "prune merged branches", "worktree cleanup", "delete stale branches", or when `git worktree list` has piled up. Do NOT use to abort or force through an in-progress merge/rebase (see resolving-merge-conflicts), and do not run it as a matter of routine - only when asked.
---

# Prune worktrees

Deletes worktrees and branches, so every verdict below is proved, never assumed. A branch is **subsumed** when every file its unique commits touch is byte-identical between the branch and the target - the leading word for the rest of this skill. `git merge-base --is-ancestor` alone under-detects this: a branch picked up, squash-merged, or rebased into the target keeps unique commits whose *content* landed even though the commits themselves didn't.

## Step 1: Confirm the target branch

Ask if not obvious from context: which branch is the integration target (`main`, `develop`, ...)? Fetch **all** of origin fresh (`git fetch --prune origin`) before anything else - a stale local copy makes every subsequent verdict wrong, and a target-only fetch leaves `branch -r --contains` blind to salvage and feature refs, so it reports pushed work as unpushed (measured 2026-09-22: 44 "unpushed" on one host before a full fetch).

## Step 2: Enumerate the candidates

`git worktree list --porcelain` for worktrees, `git branch -vv` for branches without one. Every entry gets a verdict before anything is touched; skip nothing. Read the porcelain form: the human form prints `origin/HEAD -> origin/develop` as three tokens, which shifts every column after it and turns a dirty count into a `->`.

Also walk the worktree **folder** itself. Entries that `git worktree list` does not know are one of: a stale registration (`git worktree prune` clears it), a plain directory or report file a lane left behind (residue, list it), or a directory whose `.git` file points at a different repo (another repo's worktree parked here - run every check and the removal from *that* repo). On a remote host, run the survey as one script over the host's shell wrapper, and skip per-worktree `du` when the host is loaded: the wrapper dies mid-script with no error and the survey looks complete.

Untracked residue that every lane leaves (`.beads.gate.lock`, `.opencode/`, `node_modules`) is not dirt; filter it before counting.

**Detached HEADs are candidates too**, and `git branch -vv` never shows them. They are usually throwaway merge probes, so they look free to sweep - and a detached HEAD is exactly where an unreachable commit hides.

**A worktree someone is writing is not a candidate.** Where agents run concurrently, build the protected set first and exclude it from every later step: any worktree an agent currently holds, plus anything touched recently (`find <wt>/.git -maxdepth 0 -newermt '-3 hours'`). A clean subsumed verdict on a tree an agent is mid-edit in is a verdict about the past.

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

**Detached HEAD, no branch to subsume-test.** Ask the only question that matters - does any remote already have this commit?

```
git -C <worktree> branch -r --contains HEAD
```

Non-empty → the commit is on a remote → subsumed. Empty → it exists nowhere else; salvage it in step 4 before removing.

**On a remote ref but not subsumed.** A branch whose HEAD some origin ref already contains (`git branch -r --contains HEAD` non-empty) yet whose touched-file diff is not empty is preserved without being landed. Its worktree is removable - the commits live on origin - and its local branch stays. Record it as *removed, branch kept*, a third verdict beside subsumed and kept.

Scope the test to the worktree, per worktree. `git log --all --not --remotes` looks like the same question and is not: it is **repo-global**, so it returns an identical count for every worktree you run it in. A constant that never varies across candidates is the tell that a probe is answering a different question than the one asked.

Every subsumed verdict must cite what was checked (which command, what it returned) - "looks old" or "probably fine" is not a verdict.

**Ahead-of-remote is not evidence of anything.** `git log origin/<branch>..<branch>` counts commits the remote branch lacks, which includes every commit the target merged *into* a stale local branch - two candidates once read 99 and 106 commits ahead while `git log <target>..<branch> --no-merges` returned **0** for both. Compare against the target, never against the branch's own remote.

## Step 4: Salvage anything that exists nowhere else

**Pushing is not reaping.** A salvage ref is additive - a new ref under `salvage/`, never a write to anyone's branch and never a touch of the working tree - so it is safe on a tree that is dirty, mid-merge, or being written right now. None of the gates that guard *removal* belong on it.

That asymmetry is the whole point. Gate removal on idleness and cleanliness, as step 3 does; gate preservation on nothing:

```
git -C <worktree> push origin HEAD:refs/heads/salvage/<name>-$(git -C <worktree> rev-parse --short HEAD)
```

Pass `--no-verify`: a pre-push hook that runs the test suite guards branch pushes, and a salvage ref is not one - measured 2026-09-22, a `make test-fast-parallel` hook returned 127 and the salvage was reported unsalvageable for three days. When several hosts push into one origin, prefix the ref with the host (`salvage/dell-<name>-<sha>`) so two hosts' same-named worktrees never collide.

Run it on every candidate step 3 found unsubsumed, including the ones you are about to leave alone. "Leave it and report it" is the right call for removal and a ratchet for preservation: unsubsumed trees only accumulate, each one holding commits no remote has, until someone deletes one by hand and finds out what was in it.

Skip a candidate only when `git branch -r --contains HEAD` is already non-empty - it is on a remote, so there is nothing to save.

## Step 5: Remove only what step 3 cleared

For each subsumed candidate:
```
git worktree remove <path>                 # plain first: git's own refusal is the dirty check
git worktree remove --force <path>         # only for a tree step 3 already cleared whose dirt is filtered residue or an in-progress merge
git branch -d <branch>                     # -D if step 3's ancestor check said no but the diff check said subsumed anyway
git push origin --delete <branch>          # if a matching remote ref exists
```
Leave every uncleared candidate on disk exactly as it is - report it with the reason (which check failed and how) instead of removing it. Its commits are already safe on a salvage ref from step 4; that is preservation, not a removal decision, and it changes nothing about the tree. Never fall back to force-deleting an unverified candidate just to finish the sweep.

## Step 6: Report

One line per candidate: kept or removed, why, and its salvage ref if step 4 made one. A worktree with real, non-subsumed changes is a finding to hand back to the user, not a blocker to route around.
