---
name: gc-board-and-memory-prune
description: Prune a Gas City city's work beads and the mayor's memory of sediment, then mail the owner a review digest. Use when the scheduled prune mail arrives, when the owner asks to clean up memory or beads, or when MEMORY.md or the open-bead list has gone stale.
---

# Board and memory prune

Pruning removes **sediment**: work beads and memories whose trigger has retired. It also
surfaces what waits on the owner. The owner's review is the product; the closes and deletes
exist to keep that review short. Scope is the city store's **work** beads (`gc bd`, no `--rig`)
and a report on `.claude-memory/` (the mayor's memory dir), which the memory dream now prunes.

Neighbours own the rest, so hand off rather than repeat them:
- molecule step beads, husk roots, a slow store: [`gc-store-reclaim`](../gc-store-reclaim/SKILL.md)
- an unread-mail backlog: [`gc-mail-backlog`](../gc-mail-backlog/SKILL.md)
- config, pin or order drift found on the way: [`gc-city-audit`](../gc-city-audit/SKILL.md)
- processes, disk, worktrees: [`gc-city-cleanup`](../gc-city-cleanup/SKILL.md)
- rig-store (`gl-`) beads: out of scope

Evidence rules: `.claude-memory/bare-closed-is-not-delivery.md` (delivery is a merged PR, a
pushed head or an accepted receipt, never a status) and
`.claude-memory/read-spec-and-code-from-origin-develop.md`. The memory contract is
`.claude-memory/memory-earns-its-line.md`; the dream applies it.

## 1. Board

Note the starting counts (`gc bd count --by-status`, memory file count) for the digest. List
every open, in-progress and blocked city work bead with its created and updated dates. For each
one, read `gc bd show <id>` (description, notes, comments, deps) and give it a grade:

- **Delivered**: a merged PR, a commit on the target branch or an accepted receipt proves the
  work landed. Close it, quoting that proof in `--reason`.
- **Superseded**: a later bead, owner ruling or config change made it moot (its dependency closed,
  its pool was retired, a newer epic owns the scope). Close it, naming what superseded it.
- **Live**: a job in `.gc/runtime/fleet/jobs/` or a session is on it, or its next step is
  clear. Leave it alone.
- **Owner-waiting**: an `OWNER-DECISION` or `OWNER-ACTION` title, an `owner` assignee, or a reserved
  subject (money, customer data, credentials, product scope). Never close these; they go in the
  digest. If one is plainly answered already, put it in the digest's close list with the evidence.

Standing beads stay: the discovery-sweep ledger (`ci-crt2uf`) and session beads (title `mayor`).
Hand a bead to the mayor with the `mayor` label, never the `mayor` assignee: an open bead
assigned to `mayor` triggers the seat-claim nudge loop.
After every close, re-read the bead, because store writes can report success and still not land.
**Done when** every listed bead has a grade written beside it, and every delivered or superseded
bead is closed with its evidence.

## 2. Memory

The memory dream consolidates memory now (owner 2026-11-07): the city's `memory-dream` order
(pack hoomji/memory-dream) dreams weekly, the mayor reviews, and a swap merges it in. Do not edit
memory in this step. Instead:

- Find the latest dream: the newest folder in `.gc/runtime/packs/memory-dream/runs/`, its
  `report.md` (two `counts:` lines and the cited changes) and `swap.json` when it was swapped.
- If a dream's review is open (`gc bd list --metadata-field dream.step=review`), say so in the
  digest with its bead id; the mayor reviews it per the review step.
- Count live memory the way the dream's check does (files, MEMORY.md bytes, index lines over
  120 characters) so the digest shows drift since the last swap.

**Done when** the digest's memory line names the latest dream report, its state (waiting for
review, swapped with its rollback point, rejected, failed) and the live counts.

## 3. Owner digest

Mail the owner (`gc mail send human`) one message titled `Prune <date>: N items for you`:

1. **Needs you**, newest first, one line each: the bead or mail id, what it is, and your
   recommended answer. Credential and money items go first.
2. **Close list**: owner-waiting beads that look answered, each with its evidence, for a yes or no.
3. **Old mail**: unread owner mail more than three days old that is purely informational, listed
   by id and offered for archive. Leave all owner mail unread yourself.
4. **Pruned**: beads closed, with counts before and after; memory: the latest dream report and its state.

**Done when** the mail is sent and `gc mail inbox human` lists it.
