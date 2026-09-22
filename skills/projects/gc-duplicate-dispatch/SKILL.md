---
name: gc-duplicate-dispatch
description: Find and settle work beads carrying more than one molecule root or input convoy, so two lanes never run one job. Use before slinging a bead that may already be in flight, when provider quota burns faster than the lane count explains, when two lanes commit to one branch, or when a sling reports success and nothing ever attaches.
---

# Duplicate dispatch

`gc sling` has no duplicate guard. It offers `--force`, `--no-convoy`, `--owned` and
`--reassign`, and none of them asks whether the bead is already in flight. Verified
2026-09-11: slinging `gl-n4wrh7` while **two** open convoys already named it produced a third
with no warning and no refusal.

The cost is paid twice — provider quota for two lanes, and two writers in one branch.

Run this **before** every sling, and whenever quota is draining faster than the live lane
count explains.

### Quick pre-sling gate

Before slinging `<bead>`, run this one-liner gate to verify it is not already in flight:

```bash
gc bd --rig <rig> list --status open --json | jq -r --arg b "<bead>" '.[] | select(.issue_type=="convoy" and .title == ("input convoy for " + $b)) | "\(.id)\t\(.created_at)\t\(.title)"'
```

- **Fail shape (gate tripped):** Output returned (e.g. `gl-44uelf	2026-09-11T07:15:37Z	input convoy for gl-x1qrr4`). A convoy already names `<bead>` — **do not sling**. Proceed to step 2 to classify the in-flight shape.
- **Pass shape (gate clear):** Empty output (exit 0, no stdout). Safe to sling.

To use as an automated pre-sling assertion in shell scripts:

```bash
convoys=$(gc bd --rig <rig> list --status open --json | jq -r --arg b "<bead>" '.[] | select(.issue_type=="convoy" and .title == ("input convoy for " + $b)) | .id') && [ -z "$convoys" ] || { echo "GATE REFUSED: <bead> already in flight under convoy(s): $convoys" >&2; false; }
```

Complete when the check returns clean with no output, or in-flight convoys are identified and diverted to triage.

## 1. Group the open convoys by the bead they name

```bash
gc bd --rig <rig> list --status open --json | jq -r '
  .[] | select(.issue_type=="convoy") | select(.title|startswith("input convoy for "))
  | "\(.title|sub("^input convoy for "; ""))\t\(.id)\t\(.created_at)"' | sort
```

Expected output shape:

```tsv
gl-3n2bi	gl-nbk9wx	2026-09-10T20:35:14Z
gl-x1qrr4	gl-44uelf	2026-09-11T07:15:37Z
gl-x1qrr4	gl-bzyiqt	2026-09-11T10:45:49Z
gl-x1qrr4	gl-qm1uf5	2026-09-11T12:38:28Z
```

Any bead appearing twice is a duplicate. This is the sensitive predicate; use it as the
primary test.

Grouping by `gc.root_bead_id` — the test in
[`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 4 — answers a narrower question, and
on 2026-09-11 it found **none** of the four duplicate pairs then live, because a convoy that
never attached a root has no root key to group by. Run the root-key grouping as well when you
are classifying husks, and treat convoy titles as the test for duplicate *dispatch*.

Complete when every open convoy is grouped and each bead named by two or more is listed.

## 2. Name the shape before touching it

Read each duplicate's `gc.root_bead_id` and `gc.session_name`, and the **work bead's** own
metadata:

```bash
# Read duplicate convoy metadata:
gc bd --rig <rig> show <convoy-ids...> --json | jq -r '.[] | "\(.id)\troot=\((.metadata//{})["gc.root_bead_id"]//"-")\tsess=\((.metadata//{})["gc.session_name"]//"-")"'

# Read work bead metadata:
gc bd --rig <rig> show <work-bead> --json | jq -r '.[] | "\(.id)\tstatus=\(.status)\tassignee=\(.assignee//"-")\tsess=\((.metadata//{})["gc.session_id"]//"-")\tworkdir=\((.metadata//{})["gc.work_dir"]//"-")"'
```

Three shapes, and they resolve differently:

| Shape | Convoys | Work bead | Resolution |
|---|---|---|---|
| **Dud** | root and session both absent | clean — no assignee, no `gc.session_id` | nothing ran; re-dispatch, then clear the duds |
| **Pinned** | root present, session dead | carries `gc.session_id` / `gc.work_dir` | re-sling is skipped as idempotent until the pinning keys are unset |
| **Genuine race** | two roots, one on a live lane | in_progress | keep the root on the awake lane |

The **dud** is the common one and the easiest to misread. The sling was accepted, exited 0,
created a convoy, and attached no workflow — so the work bead sat untouched. Measured
2026-09-11: the dud set was four beads with two duds each (8 total dud convoys across 4 duplicate
pairs), created 13-38 minutes apart: someone saw nothing happen and slung again, and got a
second dud rather than a refusal.

Tell a dud from a pin by the **work bead**, never by the convoy. A dud leaves the work bead
clean, which is exactly why re-slinging it works.

Complete when every duplicate carries one of the three labels and the evidence for it.

## 3. Treat `gc.session_name` as a stale pointer

Check the recorded session against `gc session list --state all` before believing it:

```bash
gc session list --state all
```

A pool cycles sessions fast: on 2026-09-11 the root `gl-oih7f7` named `codex-ci-4ad1e`, which was
gone within two minutes, replaced by `ci-eqna9` and then `ci-xh7xa`. A lookup that treats the
recorded name as current will call live roots dead.

A lane parked on a quota limit is still live — read its tail for a usage-limit message before
classifying it dead:

```bash
gc session logs <session> --tail 20
```

| Failure shape / signal | Diagnosis | Action |
|---|---|---|
| Session absent or `closed` with no recent activity | Session dead | Lane is gone; classify root as dead unless pool cycled |
| Session active, or log tail shows rate/usage limit (`rate_limit`, `usage-limit`) | Lane quota-parked | Root is still live; do not classify dead or re-dispatch |
| Template / target active under new ID | Session cycled | Map to new session ID before acting |

Complete when each candidate root's recorded session has been verified against
`gc session list --state all` (and lane tails checked via `gc session logs <session> --tail 20`
for quota-park limits) with live and dead sessions conclusively distinguished.

## 4. Re-dispatch the duds, and confirm attachment

For a dud, route the raw bead:

```bash
gc sling <rig>/<pool> <bead> --no-formula
```

The default formula is the source of the duds. `city.toml`'s `default_sling_formula =
"mol-scoped-work"` produced all eight duds in the 2026-09-11 set; `--no-formula` attached
4-for-4 the same hour, matching the 8-for-8 result already recorded on `ci-cn7mx`. Read-only
gate and review beads never needed the worktree molecule anyway.

A sling exits 0 whether or not it attached, so confirm on the board rather than on the exit
code. Either signal counts:

- a formula sling printing `Attached workflow <id>`, or
- the bead reaching `in_progress` with a live assignee, typically within ~50s:

```bash
until gc bd --rig <rig> show <bead> | grep -qE 'Assignee|IN_PROGRESS'; do sleep 5; done
```

Complete when each re-dispatched bead shows an assignee that appears in
`gc session list --state all`.

## 5. Clearing the residue is destructive — get direction first

Duplicate convoys and husk roots are cleared with `gc convoy delete <root>`, which previews
without `--force`. Delete the **root**; closing steps individually regenerates them (see
[`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 6). When recording store impact across
a cleanup, track the reduction in [`gc-reclaim-register`](../gc-reclaim-register/SKILL.md).

Confirm with the owner before deleting anything on their board, and say what you are leaving
behind when you do not. Re-dispatching a dud is safe and needs no such confirmation — it adds
a convoy rather than removing evidence.

```bash
# Preview deletion (safe, dry-run):
gc convoy delete <root>

# Execute deletion after owner confirmation:
gc convoy delete <root> --force
```

Complete when owner confirmation is received before deleting roots, or residue is explicitly
left intact and documented in the handoff.
