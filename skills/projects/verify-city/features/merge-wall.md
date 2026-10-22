# merge-wall

How fleet PRs reach the trunk, and how the per-PR develop gate is kept for the few PRs that still use
it. The trunk is permanent (R-20261021-08, R-20261021-04, ADR 0002): `dispatch/integration-branch`
names it (`wall/develop`, to be renamed `trunk` under R-20261021-17), every fleet PR lands there
whatever base it names, and `develop` takes only promotions and hotfix back-merges. The trunk orders
land validated PRs (`wall-land`), run the post-merge check (`wall-verify`), hold a PR that adds a red
and file its fix round (`red-fix-rounds`), file a fix lane per tip red (`tip-red-rounds`), sync develop
back onto the trunk (`develop-watch`) and file rebase lanes for conflicting PRs (`pr-conflict-sweep`).
`kept-beads` closes a gate bead as LANDED once its PR is on the trunk at its current head. What reaches
develop, and from there development, is [trunk-promotion](./trunk-promotion.md). Method docs:
`docs/trunk-and-promotion.md` (first), `docs/merge-queue.md` and `docs/merge-train.md` for the per-PR
gate.

## Sub-features

- `mw-switch` `dispatch/integration-branch`, `.gc/runtime/wall-ci/wall.off` (an emergency stop),
  `.gc/runtime/fleet/merge-queue/queue-ready.off`, `city.toml` `rigs.formula_vars.base_branch` and
  `github.pr_monitor.base_branches`, and `WALL=` in `wall-land.sh` all describe the same mode.
- `mw-land` `wall-land` order (`wall-ready.sh land`, every 15 min): `wall-candidates.py` picks open
  non-draft hoomji PRs on the trunk, develop or a landed parent's `fleet/*` branch (never `release/*`)
  that have not landed at their current head, and `wall-land.sh` merges them `--no-ff`. It appends
  to `dispatch/ledgers/wall-land.tsv` (time, pr, head, tip, host), comments on each PR and labels it
  `wall-landed`.
- `mw-validated` validated gate (R-20261021-03, while `land-validated.on` exists): a candidate lands
  only with a staged validation PASS, or a FAIL whose every red is also red on the tip, at its exact
  head. PR CI gate (R-20261022-01, off with `ci-gate.off`): CI at the head may add no failing job the
  trunk lacks; trunk PRs get CI on demand (`gh workflow run`, `ci-requested.tsv`). Others print
  `SKIP <pr> ...`; a new CI red writes a `ci:<job>` hold to `red-heads.tsv`.
- `mw-hold` no-new-red gate (R-20261018-01): the first member that reddens a fast check is written to
  `.gc/runtime/wall-ci/red-heads.tsv` (pr, head, time[, steps]) and is skipped until its head moves.
  `red-fix-rounds` files one P0 round per held head (`.gc/runtime/fleet/red-fix-rounds.json`).
- `mw-verify` `wall-verify` order: `test:all` once per new tip. `verified` holds the last judged tip.
  A green tip writes `green`; a red one appends to `wall-tip-red.tsv` (time, tip, fails, files, log).
  `verify.off` holds the order.
- `mw-deploy` `wall-deploy` order: deploys the newer of `deployable` and `green` to development
  (`deployed/<worker>`, `deploy-failed/<worker>`, `dispatch/ledgers/wall-deploy.tsv`). It is off
  (`wall-deploy.off`, R-20261021-14) while develop's push CD owns development; it fires and prints
  off. Turn it on only during a billing wall.
- `mw-tipred` `tip-red-rounds` order (R-20261021-01): bisects each new tip red to its culprit and files
  one single-flight fix lane per red test file or `task:<name>` (`tip-red-lanes.tsv`). Lint-step reds
  (such as `plan-ids`) get lanes only once the lint-step change being added on 10-22 is live; read the
  script header. `tip-red-revert` is its shadow revert (pushes nothing without `tip-red-revert.on`).
- `mw-sync` develop-watch sync: a develop conflict during landing writes `sync-pending`, and landing
  goes on; the `develop-watch` order files one sync lane per develop sha (a PR into the trunk).
- `mw-conflict` `pr-conflict-sweep` order (`orders/scripts/conflict-sweep.sh` -> `.py`) files rebase
  lanes for fleet PRs that conflict with the trunk; a develop-based PR is judged against the trunk
  with a merge-tree probe.
- `mw-kept` `kept-beads` order: `pr_state` reads a wall-landed PR as LANDED only while its head is in
  `wall-land.tsv`, and `close` writes "LANDED" close reasons.
- `mw-queue` per-PR develop gate: `land.sh` gates 0-7 -> `merge-train.sh ready` (plus `prune`,
  `pin-aliases`, `repin-waiver`, `lane-blockers`). It now serves only promotions (driven by
  [trunk-promotion](./trunk-promotion.md)) and PRs people open against develop. `queue-ready` stays
  idle (`queue-ready.off`, R-20261021-04).
- `mw-radar` `gitbutler-radar.sh` writes `latest.tsv` (develop, land.sh gate 3) and, with `--base`,
  `base-wall-develop.tsv` (advisory; landing ignores it).
- `mw-bigbang` history: the billing-wall plan of one wall/develop->develop PR was replaced by
  promotions (R-20261021-06); the hand promotion #6194 was its only instance. See trunk-promotion.

## How to get to it (user POV)

- The trunk is permanent: `dispatch/integration-branch` plus the two `city.toml` keys kept in step by
  hand name it. `touch .gc/runtime/wall-ci/wall.off` is the emergency stop for every trunk order.
- The trunk runs itself. `gc order list` shows `wall-land`, `wall-verify`, `wall-deploy`, `wall-e2e`,
  `red-fix-rounds`, `tip-red-rounds`, `tip-red-revert`, `develop-watch`, `pr-conflict-sweep`,
  `kept-beads` and `queue-ready`, and the ci-controller seat watches the result.
- The mayor reads the outcome from PR comments ("Landed on `wall/develop`", "Held off", `SKIP`
  reasons), the ledgers above, `.gc/runtime/wall-ci/runs/<ts>-<mode>.log` and
  `gc order history <name>`.

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
  - `doc-path-missing`: a `dispatch/` or `orders/scripts/` path named in `docs/trunk-and-promotion.md`,
    `docs/merge-queue.md` or `docs/merge-train.md` does not exist.
  - `subcommand-missing`: a documented `case` arm is gone from `merge-train.sh`, `merge-queue.sh` or
    `wall-ready.sh`.
  - `doc-order-missing` (an order `docs/trunk-and-promotion.md` names), `order-missing`,
    `order-disabled`, `order-exec-missing`: from `gc order list --json`.
  - `ledger-row-bad` / `ledger-missing`: a ledger does not have the column shape its writer prints.
  - `switch-split`: the mode files disagree (see `mw-switch`).
  - `order-stale` / `order-never-ran`: a trunk order's last `gc order history` run (wall-land,
    wall-verify, wall-deploy, pr-conflict-sweep, red-fix-rounds, tip-red-rounds, develop-watch) is
    older than 2-4x its interval.
  - `wall-tip-diverged`: the last `wall-land.tsv` tip is not an ancestor of the local
    `origin/wall/develop`.
  - `verify-unrecorded`: `verified` is neither in `green` nor in a `wall-tip-red.tsv` row.
- **State** (`mw-switch`, `mw-land`, `mw-verify`, `mw-deploy`). Run `merge_wall.py state >
  $EV/merge-wall/state.txt`. Read the integration branch and the three off switches, the city.toml
  keys, the `ls-remote` tips of `develop` and the wall, the last `wall-land.tsv` row and its age
  (rows today), `verified`/`green`, the last red rows, `deployed/`, and each order's enabled flag and
  last run. The trunk tip equals the last ledger tip or is ahead of it (sync and fix merges push
  straight to the branch). `green (absent)` is normal: the ratchet ships `deployable`, and
  `wall-deploy` is off anyway.
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
  `sed -n 12,40p dispatch/merge-train.sh`). Live behaviour is driven through a promotion:
  `trunk_promotion.py gate`. `queue-ready.off` is set, so `gc order history queue-ready` only proves
  the order fired and printed `off`.
- **Validated and CI gates** (`mw-validated`). Read the last run log's `SKIP` lines
  (`ls -t .gc/runtime/wall-ci/runs/ | head -1`) and `tail .gc/runtime/wall-ci/ci-requested.tsv`;
  `candidates` lists only the gate-free picks, not the validated filter.
- **Tip reds and sync** (`mw-tipred`, `mw-sync`). `tail .gc/runtime/wall-ci/tip-red-lanes.tsv`,
  `gc order history tip-red-rounds --limit 3`, `cat .gc/runtime/wall-ci/sync-pending` (absent is
  normal) and `gc order history develop-watch --limit 3`. Never run `tip-red-rounds.py` or
  `develop-watch.py` to check: both file lanes.
- **Big bang** (`mw-bigbang`). History; nothing to drive.

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
- `wall-landed` + head in `wall-land.tsv` is delivery for a `develop`-based PR (R-20261018-03).
  GitHub keeps such a PR OPEN until a promotion carrying it merges into develop. PRs based on
  `wall/develop` read MERGED instead.
- `verified` with no `green` and the same sha as the last `wall-tip-red.tsv` row means the tip is
  red and verify waits for a new tip. That is not a stuck order.
- `base-wall-develop.tsv` and `latest.tsv` go hours stale. That is expected: landing ignores the
  radar, and `queue-ready` is off.
- `conflict-sweep.py`'s lane brief for a develop-based PR that conflicts with the trunk still tells
  the lane to retarget the PR base to the trunk, while `docs/trunk-and-promotion.md` says a PR is
  never moved to another base. That is live code-vs-doc drift for the mayor, not map wording.
- Every `candidates` run counts all open PRs on `wall/develop`: a PR there is never open once landed,
  because GitHub marks it merged.
