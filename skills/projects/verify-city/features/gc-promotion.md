# gc-promotion

The city runs a hand-built gc from the fork `hoomji/gascity`, branch `city-next` (upstream main
plus the city patch queue). `dispatch/gc-shadow-build` replays that queue nightly on the latest
release tag and on upstream/main without installing anything. `dispatch/gc-promote <ref>` gates a
candidate on `dispatch/city-patches.toml` and on the bd version, stages it in `~/src/gc-staged/`,
swaps `~/go/bin/gc`, restarts the supervisor, probes, and rolls back on its own. Both scripts share
`dispatch/gc_upgrade.py`; the method is `docs/gc-upgrade.md`. gc and bd move together: `bd version`
must equal the `github.com/steveyegge/beads` version in the installed commit's `go.mod`.

## Sub-features

- `gcp-installed` `gc version --json` reports a version and commit, and the commit resolves in the fork.
- `gcp-layout` `~/.local/bin/gc` -> `~/go/bin/gc` -> `~/src/gc-staged/gc-<sha>.d/gc`, a hard link to
  `gc-<sha>`, and `<sha>` is the reported commit.
- `gcp-procname` the supervisor and every process running a staged gc have comm `gc` and run the live
  binary. The control-dispatcher's `GT_PROCESS_NAMES` is `gc`.
- `gcp-patches` every non-retired `city-patches.toml` entry is present in the installed commit, by the
  promoter's own rule: ancestor (sha or alias), patch-id, subject, or upstream PR for `pr-open`/`upstreamed`.
- `gcp-bd-pair` `bd version` equals the beads version in `go.mod` at the installed commit.
- `gcp-rollback` the newest installed promote record whose `previous` differs from the live binary
  names a binary that still exists.
- `gcp-shadow` `gc-shadow-build.timer` is active and enabled, the last run's result is `success`, and
  `latest-shadow.json` is under 36 h old.
- `gcp-docs` `docs/gc-upgrade.md` describes the live layout and branch.

## How to get to it (user POV)

- The mayor reads the morning `gc-shadow:` mail (also the last `gc-shadow:` journal line of
  `gc-shadow-build.service` and `.gc/runtime/gc-upgrade/latest-shadow.md`).
- The owner or the mayor runs `dispatch/gc-promote <ref> [--version V]` at a quiet hour. Every run
  writes `.gc/runtime/gc-upgrade/promote-<stamp>-<sha>.json`.
- Each later session runs whatever `~/go/bin/gc` points at; `gc version --long` shows the commit.

## Driving it with gc_promotion.py

Harness: `.claude/skills/verify-city/scripts/gc_promotion.py` (python3, stdlib only), run from `~/city`. `--city` defaults
to `$GC_CITY` or `~/city`. `--fork` defaults to `$GC_UPGRADE_FORK` or `~/src/gascity-city15x`, the
checkout `gc_upgrade.py` reads. It is a worktree of `~/src/gascity` and shares its refs.

Preconditions:

- Doctor ran this pass. `systemctl --user is-active gascity-supervisor.service` prints `active`.
- `mkdir -p $EV/gc-promotion`.

- **Doctor.** `gc_promotion.py doctor > $EV/gc-promotion/doctor.txt`. Exit 0 and the single line
  `gc-promotion: clean`; otherwise each line is one finding and the exit is 1. It covers every
  sub-feature except `gcp-docs`.
- **Installed.** `gc_promotion.py installed > $EV/gc-promotion/installed.json`. Read `live_real`
  (ends `gc-<gc_commit_short>.d/gc`), `hard_link_ok: true`, `path_gc_real == live_real`,
  `supervisor_exe == live_real` with `supervisor_comm: gc`, each `gc_processes[].comm == "gc"`,
  `bd_version == gomod_beads`, `rollback.exists: true`, and `city_next_ahead_of_installed`. A
  non-zero value means `origin/city-next` has commits that are not promoted yet. That is a decision
  for the mayor, not drift.
- **Patches.** `gc_promotion.py patches > $EV/gc-promotion/patches.txt`. One row per entry: `ancestor`
  names the sha or alias found by `git merge-base --is-ancestor`, and `present` is
  `gc_upgrade.patch_presence` (the gate `gc-promote` runs). No row reads `MISSING`. `patch-id` rows
  (8203bbd07, 8aee935c6) are contained by content, not ancestry.
- **Shadow.** `gc_promotion.py shadow > $EV/gc-promotion/shadow.json`. `timer_calendar` is
  `*-*-* 03:30:00 America/Toronto`, `service_result: success`, `base` is `origin/city-next`, and
  `base_sha` equals the installed commit. `summary` matches `journal_last_summary`.
- **Docs.** Read `docs/gc-upgrade.md` beside the installed facts. The intro, the step-5 row and the
  hand-rollback line name the branch and the `<staged>.d/gc` layout that `installed` shows.
- **Red proof (optional).** Copy `dispatch/gc_upgrade.py` and `dispatch/city-patches.toml` into a
  scratch `<dir>/dispatch/` and append a `carry` entry for `e65ed7341` (the city-1.5.x tip, not on
  city-next). `gc_promotion.py --city <dir> doctor` exits 1 and names `patch: e65ed7341 ... missing`.
  Delete the scratch dir afterwards.

## Gotchas

- Never run `dispatch/gc-promote`, not even `--check-only`: every run writes a promote record under
  `.gc/runtime/gc-upgrade/` and mails the mayor on refusal. A full run swaps the binary and restarts
  the supervisor, which drops every lane. Use `patches` to get the same gate answer read-only.
- Never run `dispatch/gc-shadow-build` by hand: it fetches, builds and tests under resource_guard,
  and mails the mayor.
- `gc` on PATH is `~/.local/bin/gc` (the unit's ExecStart), a symlink to `~/go/bin/gc`. `bd` is
  `~/.local/bin/bd` (via the `~/coolhenry` symlink); there is no `~/go/bin/bd`.
- The 10-17 promote record (`promote-20261017T0202Z-1bd67220c.json`) re-promoted the same sha to
  move to the `.d/gc` layout, so its `previous` is the live binary itself. The real rollback copy is
  `gc-prev-202610151943` (1.5.1-city, e65ed7341), from the 10-15 record. The harness skips self-previous records.
- `GT_PROCESS_NAMES` belongs to the session's agent. gc hook children inside a claude session carry
  `node,claude`, so the name check applies only where the list names gc.
- `~/src/gascity` is usually on a fix branch, not `city-next`. Read the branch as `origin/city-next`.
- The supervisor's unit environment holds provider keys. Never dump `/proc/<pid>/environ` or
  `systemctl show -p Environment` into evidence; the harness reads single keys only.
- The shadow report's `release` target conflicts are the city-next queue replayed on v1.5.0. Read the
  `main` target for forward-port debt.
