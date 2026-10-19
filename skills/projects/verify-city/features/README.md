# Gas City operations verification map

This directory is the maintained source for verifying the city's operational subsystems on the
live Ryzen city: merge queue and standing wall, fleet dispatch, quota routing, resource guard,
orders, multi-host releases, gc promotion and observability. Read the index, then use the
matching feature file as the recipe. Agent prompts and memory are verify-agent-context's.

## Baseline preconditions

- Run from the city root, `~/city` on Ryzen, with `gc` on PATH; `gc status` exits 0.
- `.claude/skills/verify-city/scripts/doctor.sh` has run this pass; its output is in `$EV/doctor.txt`.
- Evidence dir: `RUN=$(date -u +%Y%m%dT%H%M%SZ); EV=~/.local/state/verify-city/$RUN; mkdir -p $EV`.

## Driving conventions

- Every drive is read-only: no order fired, no mail, no bead or store write, no lane filed,
  retried or withdrawn, no push, no service restart, no file under `.gc/runtime/` changed.
- Many city scripts act on any argument (`land.sh --help` runs gates, a bare `route.sh` runs
  `backlog`, every `codex-fallback.py` flag runs a full pass with remote writes). Read a script's
  source or usage header before running it; run only subcommands the source shows are read-only.
- Heavy commands go through `python3 dispatch/resource_guard.py --permit <class>`; never
  bwrap or unshare (they panic the Ryzen kernel).
- Treat every command as literal. A fact with a live source (`city.toml`, a script header,
  `--help` of a safe script) is read, never recalled.

## Proof and skip reporting

- Record the feature ID, the command, its exit code and output in `$EV/<feature>/`.
- A feature whose prerequisite is absent (the wall ended, a host is offline) is
  `verified-unreachable` with the prerequisite and the command that showed it.
- Drift is a feature file or doc that disagrees with the code or live state; a broken live
  behaviour is a product gap reported to the mayor, never papered over in the map.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph, then exactly four H2 sections in
this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with <harness>`,
`Gotchas`. The user is the mayor, a seat or the owner operating the city.

## Features

- [merge-wall](./merge-wall.md) covers the merge queue, the standing wall, holds, conflict sweep and the big-bang exit.
- [quota-routing](./quota-routing.md) covers quota readings, backend fallback, Pareto write and review placement.
- [resource-guard](./resource-guard.md) covers lane reservations, command permits, the PATH shims and record hygiene.
- [orders](./orders.md) covers every order file, its script and formula target, cadence and the seat wake checks.
- [host-release](./host-release.md) covers stage-release, each remote host's release marker and skew from Ryzen.
- [gc-promotion](./gc-promotion.md) covers the installed gc, the city patch list, the shadow build and rollback.
- [observability](./observability.md) covers gc-top, gc-mobile, fleet facts and the views' agreement with placement.
