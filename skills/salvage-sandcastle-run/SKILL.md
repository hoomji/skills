---
name: salvage-sandcastle-run
description: Salvage a finished, killed, or stalled Sandcastle run — recover uncommitted work, reconcile rubber-stamped issue closures, and get the branch green.
disable-model-invocation: true
---

# Salvage a Sandcastle Run

A run ends looking finished. `gh issue list` shows its issues closed as completed, the branch has merge commits, and the console said how many branches merged. Treat that as a wreck to go over, not a delivery: the loop's own reporting overstates what landed, and the value left behind is in what it could not do.

Three kinds of debris, each with its own pass below:

- an **orphan** — an implementer's work sitting uncommitted in its worktree, invisible to `git log`
- a **rubber stamp** — an issue closed `COMPLETED` without its acceptance criteria being met
- a **blind spot** — code the sandbox edited but could not execute, so no in-sandbox gate touched it

Run the passes in order. Pass 2 starts CI, which takes minutes, so it comes before the slow reconciliation work.

## 1. Build the ledger

Reconstruct what the run attempted, from the durable record rather than from scrollback.

```bash
grep -A2 '<plan>' .sandcastle/logs/<branch>-planner.log | grep -oE '"id": "[0-9]+"'
ls -lt .sandcastle/logs/sandcastle-issue-*-implementer.log | head -20
```

The planner log holds every iteration's `<plan>` JSON; log mtimes tell you which belong to this run. Read how the run ended: `All done.` or `No unblocked issues to work on. Exiting.` means it exited on its own, and anything else means it was interrupted or is still alive (`docker ps`, `ps aux | grep main.mts`).

An iteration that merged fewer branches than it planned is the signal that matters — the missing issue's implementer produced no commits.

**Done when:** every issue id in this run's `<plan>` blocks carries exactly one verdict — merged, produced-no-commits, or still-running.

## 2. Push the branch and start CI

```bash
git push --no-verify origin <branch>
gh run list --branch <branch> --limit 10
```

`--no-verify` because the LFS pre-push hook exits 2 without `git-lfs`. CI is the only gate that sees the blind spots, so start it before the reconciliation work rather than after.

**Done when:** a fresh run exists for the branch head.

## 3. Salvage the orphans

For every issue that produced no commits, its work is still on disk:

```bash
for w in .sandcastle/worktrees/sandcastle-issue-*; do
  echo "== $w"; git -C "$w" status --short | grep -v cassettes
done
```

An implementer that stalled late often has a coherent, gate-passing change with only the commit missing — commit it on its branch and merge it. One that stalled early has scaffolding worth reading and discarding. Which it is only comes out of reading the diff.

Stall diagnosis: repeated `Agent idle for N minutes` in the implementer log, usually inside `yarn test:unit`. That is a stall, not a permissions problem — the work is normally salvageable.

**Done when:** every worktree whose branch holds no commit is either committed and merged, or discarded with the reason recorded on its issue.

## 4. Undo the rubber stamps

The merger closes every issue it merges with `gh issue close --comment "Completed by Sandcastle"`, whether or not the acceptance criteria were met. The implementer's own comment is the honest record — the one that reports its gate output and walks the ACs one at a time, naming in its own words what it could not do.

For each issue the run closed, read both — where they disagree, the implementer is right:

```bash
gh issue view <n> --json state,stateReason,comments \
  --jq '"\(.state)/\(.stateReason)", (.comments[] | "--- \(.createdAt)\n\(.body)")'
```

Compare the implementer's account against the issue's acceptance criteria. Where an AC is genuinely open, reopen the issue, or relabel it for a human. `triaging-sandcastle-issues` decides which of those two it is, and carries the labelling mechanics — an AC the sandbox structurally cannot satisfy needs its labels changed, not another run at it.

**Done when:** every issue the run closed either has all its acceptance criteria met, or is reopened or relabelled with the gap named in a comment.

## 5. Read CI green

Reds landing here are the blind spots — a sandbox that ran `yarn test:unit` green still never touched anything needing `k6`, `git-lfs`, or a live stack.

```bash
gh run list --branch <branch> --limit 10 --json name,conclusion,databaseId
gh run view <id> --log-failed
```

The reliable tell is in the implementer's own summary: an "I edited this but could not run it" note is a prediction of exactly which job goes red. When one does, fix the break and make the same class fail loudly rather than silently — a rewrite that quietly matches nothing surfaces as a bare nonzero exit code with nothing naming the cause.

**Done when:** every check on the branch head is green, or its red has a named cause and a filed issue.

## 6. Sweep

```bash
yarn install --immutable   # containers leave node_modules Linux-only; jest cannot start until this runs
docker ps -a | grep sandcastle
git worktree list
```

`node_modules` is the one that bites: the containers install Linux swc bindings into the tree they were copied from, so the first local `jest` after a run dies on `Failed to load native binding`.

**Done when:** `jest` starts locally, no sandcastle containers remain, and `git status` is clean apart from the cassette LFS pointers.
