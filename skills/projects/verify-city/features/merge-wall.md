# merge-wall

How fleet PRs reach an integration branch. Normally `develop` through Mergify: `queue-ready.sh`
runs `merge-queue.sh run`, which gates each PR with `land.sh`, built on `merge-train.sh ready`.
While the Actions billing wall stands, `dispatch/integration-branch` names `wall/develop` instead.
On that branch the wall orders land every open fleet PR (`wall-land`), test the tip (`wall-verify`),
deploy a green tip to development (`wall-deploy`), hold a PR that adds a red and file its fix round
(`red-fix-rounds`), and rebase or retarget conflicting PRs (`pr-conflict-sweep`). `kept-beads` closes
a gate bead as LANDED once its PR is on the wall at its current head. Method docs:
`docs/merge-queue.md` ("Standing wall") and `docs/merge-train.md`.

## Sub-features

- `mw-switch` `dispatch/integration-branch`, `.gc/runtime/wall-ci/wall.off`,
  `.gc/runtime/fleet/merge-queue/queue-ready.off`, `city.toml` `rigs.formula_vars.base_branch` and
  `github.pr_monitor.base_branches`, and `WALL=` in `wall-land.sh` all describe the same mode.
- `mw-land` `wall-land` order (`wall-ready.sh land`): `wall-candidates.py` picks open non-draft
  hoomji PRs on both bases that have not landed at their current head, and `wall-land.sh --all`
  merges them `--no-ff`. It appends to `dispatch/ledgers/wall-land.tsv`
  (time, pr, head, tip, host), comments on each PR and labels it `wall-landed`.
- `mw-hold` no-new-red gate: the first member that reddens a fast check is written to
  `.gc/runtime/wall-ci/red-heads.tsv` (pr, head, time[, steps]) and is skipped until its head moves.
  `red-fix-rounds` files one P0 round per held head (`.gc/runtime/fleet/red-fix-rounds.json`).
- `mw-verify` `wall-verify` order: `test:all` once per new tip. `verified` holds the last judged tip.
  A green tip writes `green`; a red one appends to `wall-tip-red.tsv` (time, tip, fails, files, log).
  `verify.off` holds the order.
- `mw-deploy` `wall-deploy` order: deploys the `green` tip to development and updates `deployed/<worker>`,
  `deploy-failed/<worker>` and `dispatch/ledgers/wall-deploy.tsv`.
- `mw-conflict` `pr-conflict-sweep` order (`orders/scripts/conflict-sweep.sh` -> `.py`) files rebase
  lanes for CONFLICTING PRs on the wall. It also retargets a `develop` PR that conflicts with the wall
  (`PR-RETARGET` lines in `.gc/runtime/route.log`).
- `mw-kept` `kept-beads` order: `pr_state` reads a wall-landed PR as LANDED only while its head is in
  `wall-land.tsv`, and `close` writes "LANDED" close reasons.
- `mw-queue` develop path: `queue-ready.sh` -> `merge-queue.sh run --no-stack` -> `land.sh` gates
  0-7 -> `merge-train.sh ready` (plus `prune`, `pin-aliases`, `repin-waiver`, `lane-blockers`).
  It is off during the wall (`queue-ready.off`).
- `mw-radar` `gitbutler-radar.sh` writes `latest.tsv` (develop, land.sh gate 3) and, with `--base`,
  `base-wall-develop.tsv` (advisory; `--all` landing ignores it).
- `mw-bigbang` the end-of-wall procedure in `docs/merge-queue.md` "Big bang, when billing returns".

## How to get to it (user POV)

- The owner or the mayor sets the mode: one line in `dispatch/integration-branch`, plus the two
  `city.toml` keys kept in step by hand. `touch .gc/runtime/wall-ci/wall.off` stops the wall orders.
- After that, the wall runs itself. `gc order list` shows `wall-land`, `wall-verify`, `wall-deploy`,
  `wall-e2e`, `red-fix-rounds`, `pr-conflict-sweep`, `kept-beads` and `queue-ready`, and the
  ci-controller seat watches the result.
- The mayor reads the outcome from PR comments ("Landed on `wall/develop`", "Held off"), the ledgers
  above and `gc order history <name>`.

## Driving it with merge_wall.py

`.claude/skills/verify-city/scripts/merge_wall.py [--city DIR] doctor|state|holds|candidates`. Every subcommand is read-only:
file reads, `gc order list/history`, `git rev-parse/merge-base/ls-remote` in
`~/projects/Gateway-LLM`, and `gh pr list/view`.

Preconditions:

- Baseline preconditions hold, and `mkdir -p $EV/merge-wall`.
- `gh auth status` succeeds (needed by `holds` and `candidates`).

- **Doctor.** `merge_wall.py doctor > $EV/merge-wall/doctor.txt; echo $?`. A clean run prints
  `merge-wall: clean` and exits 0. Each finding is one line with a kind prefix:
  - `script-missing` / `script-not-executable`: a feature script is missing or not executable.
    `wall-checks.sh` is sourced, so it is exempt.
  - `doc-path-missing`: a `dispatch/` or `orders/scripts/` path named in either doc does not exist.
  - `subcommand-missing`: a documented `case` arm is gone from `merge-train.sh`, `merge-queue.sh` or
    `wall-ready.sh`.
  - `doc-order-missing`, `order-missing`, `order-disabled`, `order-exec-missing`: from
    `gc order list --json`.
  - `ledger-row-bad` / `ledger-missing`: a ledger does not have the column shape its writer prints.
  - `switch-split`: the mode files disagree (see `mw-switch`).
  - `order-stale` / `order-never-ran`: a wall order's last `gc order history` run is older than
    2-4x its interval.
  - `wall-tip-diverged`: the last `wall-land.tsv` tip is not an ancestor of the local
    `origin/wall/develop`.
  - `verify-unrecorded`: `verified` is neither in `green` nor in a `wall-tip-red.tsv` row.
- **State** (`mw-switch`, `mw-land`, `mw-verify`, `mw-deploy`). Run `merge_wall.py state >
  $EV/merge-wall/state.txt`. Read the integration branch and the three off switches, the city.toml
  keys, the `ls-remote` tips of `develop` and the wall, the last `wall-land.tsv` row and its age
  (rows today), `verified`/`green`, the last red rows, `deployed/`, and each order's enabled flag and
  last run. While the wall stands, the wall tip equals the last ledger tip or is ahead of it (fix
  lanes push straight to the branch). `green (absent)` means `wall-deploy` correctly does nothing.
- **Holds** (`mw-hold`). Run `merge_wall.py holds > $EV/merge-wall/holds.txt`. Each held PR shows a
  verdict:
  - `HELD`: the head is unchanged. The `fix_round_at_head` column must read `yes`. A `no` that lasts
    past one `red-fix-rounds` interval (15 min) is a product gap.
  - `MOVED`: a new commit; the PR is a candidate again.
  - `MERGED`/`CLOSED`: done.
- **Candidates** (`mw-land`). Run `merge_wall.py candidates > $EV/merge-wall/candidates.txt`. It imports
  `dispatch/wall-candidates.py` and prints the PR list the next `wall-land` run would pass to
  `wall-land.sh`, with each excluded PR's reason (`draft`, `held at head`, `landed at head`). A PR
  on `develop` with label `wall-landed` and a later head is a `CANDIDATE`; that is correct.
- **Conflicts** (`mw-conflict`). Run `grep -E 'PR-RETARGET|conflict' .gc/runtime/route.log | tail` and
  `gc order history pr-conflict-sweep --limit 5`. Retargets name the conflicting file.
- **Kept** (`mw-kept`). Run `python3 dispatch/kept-beads.py list`, which only prints the last summary
  JSON. Do not run `sweep` or `close`: both write beads. Reading a LANDED close: run `gc bd show <id>`
  on a closed gate, and its reason names `on wall/develop <time>`.
- **Develop queue** (`mw-queue`). Read-only checks are `cat .gc/runtime/fleet/merge-queue/queue-ready.off`
  and the usage headers (`sed -n 1,40p dispatch/land.sh`, `sed -n 1,40p dispatch/merge-queue.sh`,
  `sed -n 12,40p dispatch/merge-train.sh`). While the wall stands, `mw-queue` live behaviour is
  `verified-unreachable`: `queue-ready.off` is set, and `gc order history queue-ready` only proves
  the order fired and printed `off`.
- **Big bang** (`mw-bigbang`). `verified-unreachable` while `dispatch/integration-branch` names the wall.
  Check the doc steps against `wall-land.sh verify`, `land.sh --yes` and the switch files only.

## Gotchas

- Never run these to "check" something:
  - `land.sh <pr>`: even `--help` runs the gates.
  - `wall-land.sh`: any argument fetches, then builds a worktree and merges.
  - `queue-ready.sh --dry-run`: still refreshes the radar, which writes `latest.tsv`.
  - `merge-train.sh prune --dry-run`: still runs `git worktree prune`.
  - `red-fix-rounds.py` without `--dry-run`, and `kept-beads.py sweep|close`.
  - `gitbutler-radar.sh`: writes TSVs and moves GitButler refs.
  - `gc order run/check`.
- `wall-deploy.sh` with no flags is a plan (it exits before any fetch), but the harness reads the same
  files instead of running it.
- `red-heads.tsv` has two row shapes: 3 columns from the original bisect (line 231 of
  `wall-land.sh`) and 4 columns from the no-new-red gate (line 173). Both are valid.
- `wall-landed` + head in `wall-land.tsv` is delivery for a `develop`-based PR (owner 10-18).
  GitHub keeps such a PR OPEN until the big-bang. PRs based on `wall/develop` read MERGED instead.
- `verified` with no `green` and the same sha as the last `wall-tip-red.tsv` row means the tip is
  red and verify waits for a new tip. That is not a stuck order.
- `base-wall-develop.tsv` and `latest.tsv` go hours stale during the wall. That is expected: `--all`
  landing ignores the radar, and `queue-ready` is off.
- Every `candidates` run counts all open PRs on `wall/develop`: a PR there is never open once landed,
  because GitHub marks it merged.
