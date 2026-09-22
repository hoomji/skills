---
name: gc-city-cleanup
description: Clean up a stopped or calm Gas City across every host — leftover processes, runtime-dir growth, the jsonl-archive push loop, rig worktrees on Ryzen/Dell/GTX, a dirty shared checkout, and gc doctor flags — measured by a before/after register. Use after `gc stop`, when the user asks to clean up the city, when disk or `.gc/runtime` has grown, or when `gc doctor` shows failures that a restart did not clear.
---

# City cleanup

A cleanup is a **sweep**: every host, every shape, each verdict proved by a probe, and the
result measured twice. Store churn is one shape among six; measured 2026-09-22 the store was
clean (0 step beads, 47-bead hot list) and everything that moved lived elsewhere.

Auto mode denies bulk deletes, process kills, rebase surgery and pushes from this session.
When a denial lands, keep sweeping and collect the exact command into one **handoff block**
at the end of the report for the owner to paste; never re-phrase a denied command to slip it
through.

## 1. Register before

Take the six-row register from [`gc-reclaim-register`](../gc-reclaim-register/SKILL.md) plus
its disk rows. Take it *before* any `gc` call that can start a managed dolt: after `gc stop`,
the first `gc status` or `gc bd` boots the server, so a 1-minute uptime afterwards is your
own probe, not a bounce.

Done when every row has a before value and the fleet table from
`dispatch/audit-fleet-load.sh` is in the draft.

## 2. Sweep the six shapes

Probe each shape on every host. A shape with nothing to reclaim gets a one-line PASS with its
probe value, never silence.

| Shape | Probe | Repair |
|---|---|---|
| Store churn / size | [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 1 | that skill; [`gc-dolt-disk-reclaim`](../gc-dolt-disk-reclaim/SKILL.md) when `.beads/dolt` > 2 GB |
| Leftover processes | `ps -eo pid,ppid,etimes,rss,args \| grep -E 'codex-linux-sandbox\|convoy control\|opencode'`; PPID 1 with a `--command-cwd` naming a removed worktree is an orphan | `kill <pid>`; [`gc-host-health`](../gc-host-health/SKILL.md) for CPU burners |
| Runtime growth | `du -sh .gc/runtime/*` | see below |
| Rig worktrees | survey per host (below) | `prune-worktrees` (`~/.claude/skills/prune-worktrees/SKILL.md`) verdicts |
| Shared checkout dirt | `git -C <rig> status --porcelain` on the integration branch | stash pattern below |
| Doctor flags | `gc doctor --check-timeout 4m -v` | table in step 4 |

**Runtime growth** has two known offenders, both under `.gc/runtime`:

- `session-reconciler-trace/segments/<yyyy>/<mm>/<dd>/` — day folders; `head.json` names only
  the current segment, so folders older than two days are droppable (859 MB → 219 MB).
- `packs/core/jsonl-archive/` — a git repo the daemon pushes every 15 minutes. `gc doctor`
  saying "N consecutive push failure(s) … non-fast-forward" means an abandoned interactive
  rebase inside it (`.git/rebase-merge` present, a 200 MB `patch`). Every commit is a full
  snapshot, so local is always freshest: `git rebase --abort`, then
  `git merge -X ours origin/main`, then let the next export push. The doctor counter resets
  only after that push succeeds.

**Rig worktrees on a remote host** run through `dispatch/<host>.sh sh '<script>'`. Two traps:
skip `du` per worktree on Dell (its load makes the wrapper die mid-script with no error), and
run a full `git fetch --prune origin` before any `branch -r --contains` (a develop-only fetch
reports salvaged branches as unpushed). Worktrees under the rig folder whose `.git` file points
at another repo (`~/src/gascity`) are that repo's worktrees; remove them from there.

**Shared checkout dirt** is lane output written to the rig's integration checkout instead of a
worktree. When the workflow bead is gone and `git log --all -S<marker> -- <path>` finds the
content on no ref, preserve it as a named stash on that branch
(`git stash push -u -m "<bead> outputs stranded on develop <date>"`), following the stash the
mayor left there on 2026-09-17. A lane-created `.env` with keys moves outside the repo
(`~/projects/<repo>.env.stranded-<date>`) rather than into the stash, and the `.gitignore`
widening that hid it goes back in the stash with the rest.

Done when every shape has a verdict per host and every removal cites the probe that cleared
it.

## 3. Register after

Re-take every row. Report churn rows that moved and disk rows that moved as two lists, and
name any surviving symptom as unexplained rather than attributing it to what you cleared.

## 4. Doctor flags: who owns the fix

`gc doctor --fix` handles `codex-hooks-drift` and `hold-label-routed-to`. The rest sort by
owner; state the owner beside each flag in the report instead of retrying it.

| Flag | Owner | Why |
|---|---|---|
| `formula-requirements` (deprecated `contract = "graph.v2"`) | upstream packs | every file is under `~/.gc/cache/repos/<sha>/{gascity,bmad}/formulas`, pinned to upstream main |
| `provider-parity` (dsh has no resume flag) | owner decision | `dsh` documents `--resume` only for the tui profile; untested on `minimal` |
| `provider-catalog-local-readiness` (claude, antigravity) | by design | role agents pin flash providers |
| `order-firing-current`, `agent-sessions`, `orphan-sessions` | `gc start` | clear within minutes of a restart |
| `nudge-unconfirmed` | owner (denied here) | `find .gc/sessions -name nudge-unconfirmed.log ! -newermt <today> -delete`; today's two belong to live sessions |
| `jsonl-archive` | step 2 runtime repair | counter resets on the next successful export |
| `order-tracking-retention` | already set | `[beads.policies.order_tracking].delete_after_close = "24h"` |

Done when every flag in the final doctor run carries an owner, `--fix` has run once, and the
handoff block lists every denied command verbatim.

## 5. Record

Comment the register on the bead whose title carries the stale number
(the retitle rule in [`gc-reclaim-register`](../gc-reclaim-register/SKILL.md)), and on
`ci-bqw6bn` for doctor findings. Salvage refs and kept worktrees go into a memory row so the
next sweep knows what was preserved on purpose.
