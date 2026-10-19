# resource-guard

Host memory admission for fleet lanes and ad-hoc heavy commands. `dispatch/resource_guard.py`
admits a lane with `--resource <read|write|build|typecheck|test|check>` (one
`fleet-resource-<hex>.scope` in its own slice, record under `.gc/runtime/fleet/resources/`) and
runs one classified command with `--permit <class>` (a `fleet-permit-<hex>.scope` in
`fleet-permits.slice`, drawn from the host permit pool, record under `.gc/runtime/fleet/permits/`).
Classes and sizes come from `.gc/runtime/fleet/resource-policy.json` through
`dispatch/resource_policy.py`; the runtime file overrides the code `DEFAULT` per host, and a file
that fails validation drops the host to the default in shadow. `dispatch/resource-bin/` shims
(`pnpm npm npx tsc vitest node bazel` -> `heavy-shim`, plus `systemd-run`) route heavy commands to
`--permit`; `dispatch/command_accounting.py` fingerprints and records every command.

## Sub-features

- `rg-policy` the runtime policy parses, passes `resource_policy._validate`, is the loaded source (not `default (file rejected ...)`) and is `mode: active`.
- `rg-classes` every class the city names in `--permit <class>` (scripts, docs, prompts, mayor memory) exists in the policy with `permit` true; each class's reserve fits `permit_gib`.
- `rg-lane` `--resource` lane reservations: in mode active every lane reserves `baseline_gib`; live records match live `fleet-resource-*.scope` units.
- `rg-nested` a `--resource` inside a `fleet-resource-*` cgroup is refused (`RESOURCE-BLOCKED: nested reservation`); a `--permit` inside a permit scope or with `GC_PERMIT_ACTIVE=1` execs the command unwrapped.
- `rg-permit` a `--permit` takes a ticket, is granted oldest first under the pool and MemAvailable, runs in `fleet-permits.slice`, and removes its ticket and record on exit.
- `rg-queue` pool growth (`permit_gib + permit_step_gib` per live ticket, capped at `permit_gib_max`), head-of-queue grant with nothing held, and the 600 s `.starve` marker that holds the reserve against new lanes.
- `rg-shims` the seven shim symlinks point at `heavy-shim`, and `gascity-supervisor`'s PATH starts with `dispatch/resource-bin` (drop-in `~/.config/systemd/user/gascity-supervisor.service.d/native.conf`).
- `rg-accounting` `command_accounting.py fingerprint` classifies a command line the way the shim will.
- `rg-hygiene` no unparsable or dead-pid files in `permits/`, no active permit scope without a record, no failed `fleet-*` units lingering, no dead lane records piling up in `resources/`.

## How to get to it (user POV)

- A lane gets its reservation from fleet dispatch (`fleet.py` launches `resource_guard.py --resource <class>`).
  The mayor or a subagent running a suite by hand uses
  `python3 ~/city/dispatch/resource_guard.py --permit <class> --timeout 3600 -- <cmd>`, with a
  class from `.gc/runtime/fleet/resource-policy.json`, never `--resource` outside a lane (mayor memory
  "Heavy runs go through resource_guard").
- An agent typing `pnpm test` in a gc session reaches `dispatch/resource-bin/heavy-shim` through the
  supervisor PATH, which re-runs it under `--permit <class>`.
- Docs: `docs/fleet-lifecycle.md` "Ad-hoc heavy runs", "Command-level accounting", "Head permit and
  light classes", "Permit pool sizing"; `docs/host-baseline.md` (`host-baseline.sh --check` emits `SHIM`).

## Driving it with resource_guard_check.py

Harness: `~/projects/skills-verify-agent-context/skills/projects/verify-city/scripts/resource_guard_check.py`
(`--city` defaults to `$GC_CITY` or `~/city`). Preconditions: doctor ran this pass;
`EV=~/.local/state/verify-city/$RUN/resource-guard; mkdir -p $EV`.

- **Doctor.** `resource_guard_check.py doctor > $EV/doctor.txt`. Proves `rg-policy`, `rg-classes`,
  `rg-shims` and `rg-hygiene`. Output is `resource-guard: clean` and exit 0, else one line per
  finding with a prefix: `policy-*`, `permit-unknown-class`/`permit-false-class` (file:line),
  `doc-policy-path`, `shim-*`, `supervisor-path`, `permit-orphan`, `permit-unaccounted`,
  `unit-failed`, `resource-records-stale`.
- **State.** `resource_guard_check.py state > $EV/state.json`. Proves `rg-lane` and `rg-queue` from
  live data: policy sizes, MemAvailable, each live lane reservation (reserve, max, current GiB),
  granted permits, tickets oldest first, `.starve` markers, `pool_now_gib`, `held_gib`, `queued_gib`,
  `fleet-permits.slice` resident, supervisor PATH head. Check: every lane `reserve_gib` equals
  `baseline_gib`; `pool_now_gib = min(permit_gib_max, permit_gib + permit_step_gib x live tickets)`;
  `fleet_resource_scopes_active` and `lane_reservations` name the same units.
- **Classes.** `resource_guard_check.py classes > $EV/classes.json`. Proves `rg-classes`: per class
  in match order its reserve/limit/cpus/workers/permit, `fits_pool`, word-count mentions in `docs/`
  and mayor memory, and `runtime_vs_code` drift against `resource_policy.DEFAULT`;
  `order_matches_code`; the lane classes `--resource` accepts (read by AST from `POLICY`); every
  `--permit <name>` found in the city with `known`.
- **Fingerprint.** `cd ~/city/dispatch && python3 command_accounting.py fingerprint pnpm run typecheck`
  prints `{"fingerprint": ..., "class": ...}` (read-only; proves `rg-accounting`). Expect
  `typecheck-bun` for that line, `lint-targeted` for `biome check x.ts`.
- **Nested refusal.** Static only (a live nested run needs a lane): `grep -n 'nested' dispatch/resource_guard.py`
  shows the `--resource` refusal in `execute()` and the `--permit` passthrough in `permit()`.
- **Permit proof (acts).** `resource_guard_check.py prove-permit > $EV/prove-permit.txt`. Runs
  `python3 dispatch/resource_guard.py --permit <smallest permit:true class> --timeout 60 -- true`
  (`lint-targeted`, 0.75 GiB, on 2026-10-19). Exit 0 with `RESOURCE-PERMIT: class=...` is a grant;
  75 with `RESOURCE-WAIT ... RESOURCE-BLOCKED: permit <reason> exhausted` is a ticket that queued
  behind older ones for 60 s. Both exercise `rg-permit`; `left_behind_by_drive: []` proves cleanup.
  Its writes: a transient ticket/record in `permits/`, and on a grant one record under
  `resource-results/commands/` (a ~0 GiB `true` in that class's profile). Run it at most once a pass.

## Gotchas

- Never import or call `resource_guard.py` helpers to read state: `permit_tickets()`,
  `permit_starving()` and the `permit()` loop unlink dead files. Importing the module also runs
  host probes. The harness reimplements `alive()` (boot id + `/proc/<pid>/stat` start time).
- `systemctl --user show gascity-supervisor -p Environment` carries provider API keys. Print only
  `PATH`; never save that output to `$EV`.
- `--permit` with a name that is not a policy class, or a `permit: false` class, or in mode shadow,
  silently `execvp`s the command (`resource_guard.py` `permit()`), with no error. The PATH shim
  usually re-wraps a pnpm/vitest child, so the mistake hides; doctor's `permit-unknown-class` is
  the only signal. `test`, `check`, `build`, `write` are `--resource` lane classes; only `build` is
  also a permit class.
- With a deep queue the proof times out (75) rather than grants: grants are strict oldest first,
  so even a 0.75 GiB class waits behind 6 GiB suites. That is the design (owner 2026-10-08), not a fault.
- `docs_mentions`/`memory_mentions` are word counts: short names (`go`, `build`, `suite`) over-count.
- The runtime file lists `bazel` last; the code `DEFAULT` lists it before `local-stack`. First match
  wins, so order drift matters only when patterns overlap.
- Never bwrap or unshare to test isolation; both panic the Ryzen kernel.
