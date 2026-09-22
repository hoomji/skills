---
name: gc-reclaim-register
description: Record a Gas City reclaim as a six-row before/after register — open beads, hot-list payload, molecule step beads, molecule roots, unread mail, host health — and keep a size drop from being reported as health. Use when starting or finishing a store reclaim, when reporting what a cleanup achieved, or when a store-health claim needs a measured number behind it.
---

# The reclaim register

A reclaim is believed only where it is measured twice. The register is six rows taken before
the repair and again after, so the claim "the store is better" carries numbers instead of an
impression.

The repair itself is [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md), and host diagnostics are
[`gc-host-health`](../gc-host-health/SKILL.md). Every measurement command below comes directly from
those procedures. This skill adds no arbitrary metrics — it fixes **which** numbers get recorded,
and how a reclaim report avoids misdiagnosing success when symptoms survive.

## The six rows

| Row | Source |
|---|---|
| Open beads, per rig | `gc bd --rig <rig> list --status open --json \| jq length` |
| Hot-list payload | bytes and seconds for that same call — [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 2 |
| Molecule step beads | beads carrying `gc.root_bead_id` — [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 3 |
| Molecule roots, **live** | roots classified live vs husk — [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) step 4 |
| Unread mail | `gc mail count` — [`gc-mail-backlog`](../gc-mail-backlog/SKILL.md) |
| Host health | load average (`uptime`), swap used (`free -h`), orphan/workerd processes (`ps`) — [`gc-host-health`](../gc-host-health/SKILL.md) steps 1–3 |

Record step beads as a share of open beads, not as a bare count: the share is what says
whether husks are the problem. A worked register, measured on 2026-09-11 (rows 1–5) and 2026-09-13 (row 6), for shape:

```
Open beads, rig gateway-llm | 442                                            | 226
Hot-list payload            | 1.19 MB                                        | 680 KB
Molecule step beads         | 271 (61%)                                      | 55
Molecule roots              | 13                                             | 2 live
Unread mail                 | 338                                            | 0
Host health                 | load 8.4 (8c), 4.1 GB swap, 1 workerd (100% CPU) | load 1.2, 0 B swap, 0 orphans
```

The roots row is `2 live`, not `2`. A count alone cannot distinguish two working lanes from
two husks you failed to clear.

The host health row records three numbers: load average vs core count, swap used, and runaway
child count (such as orphaned `workerd` processes). Host health must be measured alongside store
health because host resource exhaustion (CPU starvation, swap latency) directly masquerades as
database degradation.

Complete when all six rows carry a before and an after value, and the step-bead row carries
its percentage.

### Disk rows

A whole-city cleanup ([`gc-city-cleanup`](../gc-city-cleanup/SKILL.md)) adds disk rows beneath
the six, kept separate because a size drop is not health (next section):

| Row | Source |
|---|---|
| `.gc/runtime` by child | `du -sh .gc/runtime/* \| sort -rh \| head` |
| `.beads/dolt` | `du -sh .beads/dolt` |
| Rig worktrees, per host | registered count from `git worktree list`, folder entries, `du -sh <worktrees>` |
| Root filesystem | `df -h /` used and free, per host |

Take all rows before the first `gc` command of the session: after `gc stop` the first
`gc status` or `gc bd` boots the managed dolt, so the store rows would otherwise measure a
server you just started.

## A size drop is not health

Report the failure shape you actually found. A reclaim that moves the six rows has fixed
**churn**; it has not necessarily fixed anything `gc status` reports about the store.

Measured on 2026-09-11: the reclaim took the store from 6.2 GB to 2.3 GB and a GC ran
successfully — and `Live rows: 0` with a `0.0 MB/row` ratio survived both, unchanged. That
zero means the health probe is timing out, so the GC advisory can never fire. A report that
leads with the gigabytes reads as "store healthy" and buries a blind guard.

The `Live rows: 0` blind guard is a **host-visible** symptom, not a store-visible one:
`gc status` runs a probe query (`dolt sql -q "SELECT COUNT(*) FROM beads"`) that gets reaped
when the host is under severe resource contention (such as high CPU load from runaway formula
children or memory thrashing from stale swap). When `Live rows: 0` persists after a store reclaim,
do not diagnose the store — switch to [`gc-host-health`](../gc-host-health/SKILL.md) to audit
CPU, swap, and orphan processes.

| Symptom | Domain | Where to diagnose | Reclaim fixes it? |
|---|---|---|---|
| Inflated open bead count / slow `bd list` | Bead churn | [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md) | Yes (drops hot-list size) |
| Bloated `.beads/dolt` directory | Disk storage | [`gc-dolt-disk-reclaim`](../gc-dolt-disk-reclaim/SKILL.md) | Yes (compacts oldgen chunks) |
| `Live rows: 0`, `0.0 MB/row` (probe timeout) | Host resources | [`gc-host-health`](../gc-host-health/SKILL.md) | No (requires host CPU/swap remediation) |
| High load avg / runaway `workerd` | Host CPU/RAM | [`gc-host-health`](../gc-host-health/SKILL.md) | No (requires killing orphaned processes) |

So state the rows that moved and the symptoms that did not, as two separate lists. Where a
symptom is unexplained, say it is unexplained rather than attributing it to the churn you
just cleared.

Complete when the report explicitly separates churn rows that moved from surviving host-visible
symptoms (`Live rows: 0`), and any surviving symptom has either a host health audit
([`gc-host-health`](../gc-host-health/SKILL.md)) or an explicit note marking it unexplained.

## Retitle the beads whose premise you just killed

A bead's **title** is what the next session triages on, and it is the part that goes stale
first. After the 2026-09-11 reclaim, `ci-7otz0` still read "Primary dolt store is 6.2 GB ...
and 7 days without GC" and `ci-sm3bk` still read "bead store is 6.0GB" — two open P0/P1 beads
advertising a state that no longer existed, which is how a reclaim gets run twice.

For every bead whose title states a number you just moved: comment the new measurement, and
retitle or close according to what survives.

Audit open beads for stale store or size premises:
```bash
gc bd list --status open --json | jq -r '.[] | select(.title | test("([0-9]+\\s*(GB|MB))|dolt|reclaim|GC|store"; "i")) | "\(.id): \(.title)"'
```

For each identified bead:

1. Post the register measurement to the bead audit trail:
```bash
gc bd comment <id> "Reclaim register $(date +%Y-%m-%d): store size <after_size> (was <before_size>), hot list <after_len> (was <before_len>). Host health: <host_status>. Surviving symptom: <surviving_symptom>."
```

2. Act based on surviving premises:
- **Every claim in the title is now false** → close it, quoting the measurement:
```bash
gc bd close <id> --reason "Resolved by store reclaim $(date +%Y-%m-%d). Hot list <before> -> <after>, store <before> -> <after>. Register verified."
```
- **Some claims survive** → keep it open and retitle to the surviving claim alone (`ci-7otz0`'s
  size and GC-age premises died; its `Live rows: 0` premise did not):
```bash
gc bd update <id> --title "Dolt health probe timeout (Live rows: 0)"
```

Complete when:
1. `gc bd list --status open --json | jq -r '.[] | select(.title | test("([0-9]+\\s*(GB|MB))|dolt|reclaim|GC|store"; "i")) | "\(.id): \(.title)"'` has been run and evaluated against the post-reclaim register.
2. Every bead referencing a moved metric carries a comment recording the measured date and register values.
3. Every bead whose premises were fully resolved is closed with `--reason` citing the measurements.
4. Every bead with surviving premises is retitled to state only the surviving symptom (routing `Live rows: 0` to [`gc-host-health`](../gc-host-health/SKILL.md)).
5. No open bead's title states a number or premise that the post-reclaim register contradicts.
