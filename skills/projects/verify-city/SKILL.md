---
name: verify-city
description: Verify a Gas City's operations on the live Ryzen city — trunk landing and the develop gate, trunk-to-develop promotion, quota routing, resource guard, orders, multi-host releases, gc promotion and the gc-top/gc-mobile views — by reading live state read-only and checking it against the code and docs. Use when proving a change to dispatch/, orders/ or a city doc, when a subsystem acts on a stale rule, before staging a release, or when /maintain-verification-skill audits this map.
---

# Verify city operations

The "app" is the running city on Ryzen (`~/city`): its dispatch scripts, orders, quota
controller, resource guard, remote hosts and operator views. A user is the mayor, a seat or
the owner operating it. Drift is a doc, comment or display that disagrees with the code or the
live state; a broken behaviour is a product gap. Agent prompts and memory belong to
`verify-agent-context`; the gc binary itself to `verify-gascity`.

Feature map: [`features/README.md`](features/README.md). Every drive is read-only (the README's
driving conventions are binding).

## Launch

Nothing starts: the instance is the live city. Ready when `cd ~/city && gc status` exits 0.
Pick a run id and evidence dir:
`RUN=$(date -u +%Y%m%dT%H%M%SZ); EV=~/.local/state/verify-city/$RUN; mkdir -p $EV`.
There is no second instance; never drive a copy of the city as if it were live.

## Doctor

`.claude/skills/verify-city/scripts/doctor.sh [--city DIR] [feature...]` runs each feature harness's `doctor` and prefixes
every finding with its feature; it prints `verify-city: clean` and exits 0 only when all are
clean (about 45 s; `orders` reads 24 h of order history). Run it first, save it to
`$EV/doctor.txt`, and again after any edit you prove. A finding about live state (a failing
quota reading, a host behind the release) is reported as state, not fixed in the map.

## Drive

One harness per feature, all python3 stdlib, each with `--city` and a safe `--help`:

| Feature | Harness | Drives |
|---|---|---|
| [merge-wall](features/merge-wall.md) | `.claude/skills/verify-city/scripts/merge_wall.py` | `state`, `holds`, `candidates` |
| [trunk-promotion](features/trunk-promotion.md) | `.claude/skills/verify-city/scripts/trunk_promotion.py` | `state`, `promotable`, `gate` |
| [quota-routing](features/quota-routing.md) | `.claude/skills/verify-city/scripts/quota_routing.py` | `readings`, `placement`, `orders`, `supply` |
| [resource-guard](features/resource-guard.md) | `.claude/skills/verify-city/scripts/resource_guard_check.py` | `state`, `classes`, `prove-permit` (the one drive that takes a permit) |
| [orders](features/orders.md) | `.claude/skills/verify-city/scripts/orders_check.py` | `inventory`, `order <name>`, `seats` |
| [host-release](features/host-release.md) | `.claude/skills/verify-city/scripts/host_release.py` | `skew`, `config`, `baseline` (ssh reads only) |
| [gc-promotion](features/gc-promotion.md) | `.claude/skills/verify-city/scripts/gc_promotion.py` | `installed`, `patches`, `shadow` |
| [observability](features/observability.md) | `.claude/skills/verify-city/scripts/observability.py` | `mobile`, `top`, `facts`, `views` |

Run a drive as `python3 .claude/skills/verify-city/scripts/<harness> <drive> > $EV/<feature>/<drive>.txt`. The feature
file names what each output proves and which sub-feature it covers.

## Evidence

Each proof is the command, its exit code and output under `$EV/<feature>/`. Prove behaviour
from live state and the code that produced it, never from a doc's claim: a dry-run flag is
trusted only after reading what it still writes (several city scripts write under `--dry-run`;
the feature Gotchas name them).

## Cleanup

Drives start nothing long-lived. `observability top` creates and kills its own tmux socket
(`tmux -L verify-city-obs`); confirm `tmux -L verify-city-obs ls` reports no server. Evidence in
`~/.local/state/verify-city/` stays.

## Helpers

`.claude/skills/verify-city/scripts/doctor.sh` and the eight harnesses above are executable. The weekly order
`verify-skill-doctors` (city `orders/scripts/verify-skill-doctors.sh`) runs `.claude/skills/verify-city/scripts/doctor.sh`
and mails the mayor `VERIFY-SKILLS:` when its findings change.
