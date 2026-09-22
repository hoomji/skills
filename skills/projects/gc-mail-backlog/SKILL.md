---
name: gc-mail-backlog
description: Clear a Gas City unread-mail backlog by harvesting its signal before archiving the residue. Use when gc mail count shows an unread backlog, when mail-check floods every prompt, when advisory mail has sat unread for days, or when message beads are inflating the open-bead count.
---

# Clearing a mail backlog without destroying what it was telling you

`gc mail` is beads with `type="message"`, so an unread backlog is two problems at once: a
deaf mayor, and message beads padding the store. Reclaiming the store is
[`gc-store-reclaim`](../gc-store-reclaim/SKILL.md); host-level diagnosis is
[`gc-host-health`](../gc-host-health/SKILL.md) — an unread backlog (measured on 2026-09-11:
872 notification beads) inflates the open-bead count, which is a host-level symptom visible
in `gc status` that slows prompt hooks across every active lane. This skill is the mail half.

A backlog is mostly repetition — the same hourly advisory hundreds of times — which is why
bulk archive exists and why reaching for it first is the mistake. **Harvest** the backlog
before you archive it: measured on **2026-09-11**, exactly 58 of 338 messages (17%) in the
backlog were each reporting a different piece of unpushed or stranded work, and that 17% is
what produced the unshipped-branch register. Archived blind, all of it is gone with no trace
that it existed.

## 1. Shape the backlog before touching it

Run count to measure the backlog, then build a histogram by sender and subject:

```bash
gc mail count
gc mail inbox --json | jq -r '(.messages // .)?[] | "\(.from)\t\(.subject)"' | sort | uniq -c | sort -rn
```

Expected output shape for `gc mail count`:
```
97 total, 97 unread for human
```

Expected output shape for the histogram:
```
     42 human	Dolt health advisory [MEDIUM]
     18 human	Dolt backup: 2/2 databases failed to sync [MEDIUM]
     13 human	ESCALATION: JSONL spike detected [HIGH]
      1 mayor	TWENTY-FIRST FLIP APPLIED: caps removed, implementers now shared
```

The `uniq -c` histogram is the whole plan: high-count identical subjects are the repetition
you will archive by filter, and the long tail of one-off subjects is the signal you harvest
by hand.

Complete when you have recorded the total and unread count from `gc mail count`, generated
the subject histogram, and verified that the sum of the histogram row counts accounts for
every unread message.

## 2. Harvest the tail

Read the one-off messages with `gc mail peek <id>`, which shows a message and leaves it
unread:

```bash
gc mail peek <id>
```

Reach for `gc mail read` only when you intend to mark it read — `archive` selects
*unread* messages by default, so reading a message during triage quietly removes it from the
slice your later filter will match.

What earns a bead of its own: a named branch, sha, PR, or bead id that appears nowhere else.
File those before archiving anything:

```bash
gc bd create --title "<harvested work summary>" --type task
```

Write down the count you harvested and the count you judged pure repetition; the two must sum
to the unread total.

Complete when every histogram row with a low count has been peeked, either filed as a new bead
or explicitly classified as repetition, and the harvested count plus repetition count exactly
equals the initial unread total.

## 3. Archive the repetition by filter

Every filter run is `--dry-run` first, then the same command without it:

```bash
gc mail archive --to <recipient> --subject-prefix '<prefix>' --dry-run
gc mail archive --to <recipient> --subject-prefix '<prefix>'
```

Select with `--subject-prefix`, `--subject-contains`, `--from`, or `--empty-body`; widen to
every mailbox with `--all-recipients`.

### Failure shapes and common traps

| Shape | Trap | Prevention / Fix |
|---|---|---|
| Partial archive | `--limit` defaults to **100**; reports success (exit 0) while 238 messages remain | Loop on `gc mail count` until unread stops falling |
| Store padding survives | Archive selects unread only; read-but-open messages stay open beads (`0 unread`, store still padded) | Pass `--include-read` to archive read-but-open message beads |
| Lost signal | Blind bulk archiving wipes unpushed work / branches | Step 2 harvest: peek tail rows before archiving |
| Missing recipient scope | Running archive without `--to` or `--all-recipients` exits 1 | Always pass `--to <recipient>` or `--all-recipients` |

Two flags decide whether the run does what you think:

- **The `--limit` default of 100 is a common trap**: A 338-message backlog needs four runs,
  and the first one reports success while 238 messages remain. An agent observing exit code 0
  will falsely believe the backlog is clear unless it loops on `gc mail count` until the count
  stops falling.
- Archive selects unread only. Read-but-open messages keep their beads open and stay out of
  every filter until you pass `--include-read` — these are why a mailbox can read `0 unread`
  while the store still carries the beads.

### Loop command pattern

Use this loop to drain batches through the `--limit 100` boundary until the unread count
reaches zero or stops falling:

```bash
# Archive loop pattern: repeat batch archive until unread count stops falling
while true; do
  unread_before=$(gc mail count --json | jq -r '.unread // 0')
  echo "Current unread: $unread_before"
  [ "$unread_before" -le 0 ] && break
  gc mail archive --to <recipient> --subject-prefix '<prefix>'
  unread_after=$(gc mail count --json | jq -r '.unread // 0')
  [ "$unread_after" -ge "$unread_before" ] && { echo "Unread stopped falling at $unread_after; filter matched all available items."; break; }
done
```

Or as a compact one-liner:

```bash
while [ "$(gc mail count --json | jq -r '.unread // 0')" -gt 0 ]; do before=$(gc mail count --json | jq -r '.unread // 0'); gc mail archive --to <recipient> --subject-prefix '<prefix>'; after=$(gc mail count --json | jq -r '.unread // 0'); [ "$after" -ge "$before" ] && break; done
```

Verify final count:

```bash
gc mail count
```

Complete when `gc mail count` reports zero unread and the total has fallen by the number you
classified as repetition.

## 4. Report both numbers and both classes

State the before/after unread count and, separately, how many messages became filed work.
That second number is the one that justifies the time; record it in the reclaim register
(see [`gc-reclaim-register`](../gc-reclaim-register/SKILL.md)) as the `Unread mail` row.

| Metric | Before | After | Destination / Notes |
|---|---|---|---|
| Unread mail | 338 | 0 | Reclaim register `Unread mail` row |
| Harvested signal | 0 | 58 | Filed as tracked task beads (17% on 2026-09-11) |
| Repetition archived | 0 | 280 | Dismissed with filter archive |

Complete when both before/after unread counts and harvested work counts are recorded in the
reclaim register ([`gc-reclaim-register`](../gc-reclaim-register/SKILL.md)).

## Mail does not cross stores

`gc mail` is bead-backed, so a rig with its own Dolt store cannot mail this city — the Dell
rig cannot reach the mayor at all. Its reports arrive only by polling
(`dispatch/dell.sh snap`). A quiet mailbox is evidence about this store only.

Complete when mailbox triage confirms evidence applies solely to the local city store.
