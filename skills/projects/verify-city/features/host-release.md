# host-release

How city code reaches the remote hosts (Dell, GTX, Hailey) and whether they run the release Ryzen
expects. Ryzen runs the live `~/city` checkout: a `dispatch/` edit is live there at once, before
any commit. The remotes' `~/city` is not a git checkout. Each runs a checksummed release of the
`FILES` list in `dispatch/deploy-resource-routing.py`, installed by `dispatch/stage-release.sh`
(run by the `host-release` order through `dispatch/auto-release.py`), plus its own host-specific `city.toml`. The release marker is
`~/city/.gc/runtime/fleet/release.json` on each host: `release` (the city commit), `installed`
(epoch) and a sha256 for each released file. The harness is `.claude/skills/verify-city/scripts/host_release.py`.

## Sub-features

- `hr-marker` each remote has `.gc/runtime/fleet/release.json`, the release is in Ryzen HEAD's
  history, and all remotes run the same release.
- `hr-skew` every released file on a remote matches Ryzen HEAD. Released files that changed since
  the host's release are named. This is the "has today's commit reached the hosts" answer.
- `hr-handedit` the on-disk released files on a remote match that host's own installed manifest.
  A mismatch is a hand copy, the drift `docs/city-as-git.md` "Remote hosts" forbids.
- `hr-live-edit` Ryzen has no uncommitted edit to a released file. Such an edit is live on Ryzen
  only, and no release can carry it (memory `live-checkout-edit-is-a-ryzen-only-deploy`).
- `hr-files` every `FILES` entry exists at HEAD. A released prompt never calls a
  `{{ template }}` defined only in an unreleased city file.
- `hr-overlay` each remote `city.toml` keeps the installer's overlay: every `dsh-*` pool command is
  `<host city>/dispatch/dsh-scoped.sh`, and every base pool has the `resource` options schema. Its
  rig is the one `fleet.py` HOSTS names. These files differ per host by design.
- `hr-helpers` `stage-release.sh` default hosts equal the remotes in `fleet.py` HOSTS. Each remote has
  `dispatch/<host>.sh`, `dispatch/<host>-sync.sh` and `orders/<host>-sync.toml`.
- `hr-baseline` each host's hardware inventory, supervisor shim PATH and lane tools match
  `docs/host-baseline.json`. These are `host-baseline.sh --check`'s checks without its bench.
- `hr-docs` no doc runs `stage-release.sh` with a host as its first argument.

## How to get to it (user POV)

- The `host-release` order runs `dispatch/auto-release.py` every 10 min: it compares each host's
  `release.json` hashes with HEAD, waits for 10 min without a commit to `FILES`, pre-checks the
  staged tree (compile, `bash -n`, `import fleet, resource_guard`), then runs
  `dispatch/stage-release.sh HEAD <stale hosts>` and re-reads each `release.json`. State:
  `.gc/runtime/auto-release/state.json`; `auto-release.py --dry-run` is read-only (it writes nothing).
  `stage-release.sh [<commit>] [<host>...]` (defaults HEAD and `dell gtx hailey`) reads `FILES` and
  each file's content with `git show <commit>:<path>`, then scp's a tarball to each host. On
  the host it runs `deploy-resource-routing.py <stage> ~/city --release <sha>`, which writes
  `release.json` and an `archive/resource-routing-<sha>/` backup, and prints the new head. Never
  run it from a verification pass: it writes to every host.
- `.git/hooks/post-commit` warns "released files changed (...)" when a commit touches `FILES`.
- The mayor reads hosts through `dispatch/{dell,gtx,hailey}.sh`. Of its subcommands, `snap`,
  `report`, `logs`, `top` and `capcheck` only read. `status` runs `<host>-sync.sh`, which rsyncs
  into Ryzen's `.gc/runtime/` and rewrites `<host>-status.json`. It is a write; leave it to the
  `<host>-sync` orders. `file`, `sweep`, `prune` and `bd`/`sh` can mutate.

## Driving it with host_release.py

Preconditions:

- Doctor ran this pass. `ssh -o BatchMode=yes dell true` works (tailnet with a warm
  ControlMaster). An offline host prints `verified-unreachable`, which is not a finding.

Run from the city root. `H=~/projects/skills-verify-agent-context/skills/projects/verify-city/scripts/host_release.py`; `mkdir -p $EV/host-release`.

- **Doctor.** Run `$H doctor | tee $EV/host-release/doctor.txt`. Each line is a finding and the
  exit code is 1 on any. A clean run prints `host-release: clean`, plus any unreachable hosts in
  parentheses. Covers `hr-marker`, `hr-skew`, `hr-handedit`, `hr-live-edit`, `hr-files`,
  `hr-overlay`, `hr-helpers` and `hr-docs`.
- **Skew.** Run `$H skew | tee $EV/host-release/skew.txt` and
  `$H skew --json > $EV/host-release/skew.json`, with `--host dell` for one host.
  - Ryzen side: HEAD, the city mirror's `main` (`~/src/city.git`, what remote lanes fetch),
    uncommitted released files, and Ryzen's own stale `release.json`.
  - Per host: release sha, install time, commits behind HEAD, released files behind HEAD, hand
    edits, missing files, and off-release copies (tracked `dispatch/`, `formulas/` and `orders/`
    files on the host that are not in `FILES`).
  - Proof that a commit reached a host: the host's `release` is that commit or a descendant, and
    `released files behind HEAD` is empty. Check a named commit with
    `git show --name-only <sha>` against the list.
- **Config.** Run `$H config | tee $EV/host-release/config.txt`. Each host prints `overlay holds`
  and its rig name.
- **Baseline.** Run `$H baseline | tee $EV/host-release/baseline.txt`. Each host prints `matches`,
  or lists `CHANGED`/`UNREAD`/`SHIM`/`TOOLS` lines in `host-baseline.sh --check` wording. Run the
  real `--check` only when a bench is wanted: on a quiet host it writes a 512 MiB file and loads
  every thread.

## Gotchas

- Release lag alone is normal: 85 commits behind HEAD is fine when none touched `FILES`. Only
  `released files behind HEAD` is skew.
- `stage-release.sh` reads `FILES` from the commit since 2026-10-22; before that it read the
  working tree and an uncommitted `FILES` entry failed mid-stage. Doctor's "not in HEAD" line
  still names such an entry.
- Skew that lasts past about 20 min means the order is failing: read its `order.failed` message or
  the mayor's `AUTO-RELEASE failed` mail, not the doctor.
- `dispatch/ledgers/review-feedback.jsonl` is merged with the host's own rows on install, so it
  differs from HEAD by design and is skipped. The resource-bin shims (`pnpm`, `npm`, `npx`, `tsc`,
  `vitest`, `node`, `bazel`) are symlinks to `heavy-shim` and are compared as links.
- Ryzen also has a `.gc/runtime/fleet/release.json` (7feebf83, installed 2026-10-04), but it runs
  its checkout. `fleet-session.py` and `work_retrospective.py` still read that file, so Ryzen lane
  records name a release Ryzen does not run.
- `<host>-sync.sh` reports `city_source_head` from `~/src/city-dev` on the host, a side checkout
  frozen since 2026-10-03 (Dell/GTX) or 2026-10-15 (Hailey). It is not the release marker, and its
  `city_source_lag: true` is permanent.
- Remote off-release copies (for example `orders/fleet-maintenance.toml` and
  `formulas/mol-scoped-work.toml`) are host-local by design. The count is context, not a finding.
- `archive/resource-routing-<sha>/` grows on every stage and is never pruned (262 on Dell, about
  391 MB on 2026-10-19).
- `docs/host-baseline.md` tables still show three hosts. Hailey exists only in
  `docs/host-baseline.json` and the script.
