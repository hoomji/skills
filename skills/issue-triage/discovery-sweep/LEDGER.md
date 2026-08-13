# The ledger — reference

The **ledger** is a discovery sweep's only memory. Every firing wakes amnesiac;
everything a firing must know about the last one lives here. Reference for
[`SKILL.md`](SKILL.md).

## Where it lives

Prefer **a tracker item carrying a marker comment**. It survives a lost machine,
and it doubles as the decision channel — the human replies in a comment, which is
the one place an approval can be recorded that the next firing will actually read.

A **state file on disk** is the fallback when the tracker has no home for it. It
costs the reply channel: the host must then name where decisions arrive, and a
firing that cannot find that channel proposes nothing and says so.

Find a tracker-item ledger by its marker, never by title:

```bash
gh issue list --state open --limit 100 --json number,body \
  --jq '.[] | select(.body | contains("<!-- DISCOVERY-LEDGER:v1 -->")) | .number'
```

## Sections

| Section | Holds | Drained by |
|---|---|---|
| **Awaiting review** | Human candidates proposed, not filed. One row per id, with the blocking capability and a sweep count. | A decision comment, or ageing out at ten sweeps. |
| **Deferred** | Agent-finishable candidates held only by the file cap. Not filed, no approval pending. | The next firing's step 6, before it spends anything on fresh candidates. |
| **Blocked** | Items already **filed and unarmed**, held by a blocking edge. One row per item with the blockers it waits on. | The next firing's step 2, which arms whatever reached the frontier and drops the row. |
| **Filed** | Every item this routine opened, with its number, its route, and whether it is armed. | Nothing — this is the dedupe record. |
| **Rejected** | Everything that will never be re-surfaced: human-cut, superseded, or aged out. Carries the reason verbatim. | Nothing — this is the other half of the dedupe record. |
| **Swept** | One row per firing: date, lanes touched, what it found. `queue-at-target` for a gated firing. | Nothing; trim to the last ~20 rows. |

Filed and Rejected are permanent for a reason: together they are what step 4
dedupes against and what stops a rejected idea returning every firing until it
gets filed by attrition.

A blocked item lives in **both** Filed and Blocked: Filed is the permanent dedupe
record and carries the armed flag, Blocked is the working list step 2 walks. Arming
one flips its Filed row and removes its Blocked row, so an item is never in Blocked
and armed at once.

**Deferred and Blocked are not interchangeable.** A Deferred candidate has no
tracker item and is released by budget; a Blocked one already exists on the
tracker, unarmed, and is released by its blockers closing. Recording a Blocked
item as Deferred files it a second time; recording a Deferred one as Blocked leaves
it waiting on an edge that no firing will ever advance.

## Ids

Proposals are numbered `D-1`, `D-2`, … in one sequence that never restarts. A
firing reads the highest id ever used — across **all** sections, not just Awaiting
review — and continues from there. Restarting the sequence collides a new proposal
with a decided one, and step 2 then reads a stale decision as a live instruction.

An id is permanent once assigned: an entry moving between sections keeps it, so a
filed item traces back to the proposal it came from.

## Decision syntax

The human replies in a comment on the ledger:

- `APPROVE: D-12, D-14` — file these; human-routed, so **without** the arm marker.
- `AGENT: D-12` — agent-finishable after all; file it armed.
- `REJECT: D-13 — <reason>` — move to Rejected carrying that reason verbatim.

Anything unanswered stays in Awaiting review with its sweep count bumped.

## Template (first run only)

Title: `Discovery ledger — <routine name> (routine state)`

```markdown
<!-- DISCOVERY-LEDGER:v1 -->

State for the `<routine-name>` routine (`<path to its SKILL.md>`). Each firing
wakes with no memory; this issue is the memory.

**Decisions:** reply in a **comment** — `APPROVE: D-n` to file it,
`AGENT: D-n` if it's agent-finishable after all, `REJECT: D-n — reason`. The
routine owns this body and rewrites it each sweep; your comments are never edited.

Last swept: <date>

## Awaiting review

_Proposed, not filed. Sweeps counted so a stale proposal ages out after ten._

| id | Candidate | Blocked for the agent by | Sweeps |
| -- | --------- | ------------------------ | ------ |

## Deferred

_Agent-finishable, not yet filed, held only by the file cap. No approval needed —
the next sweep files these before it sweeps for anything new._

| id | Candidate | Acceptance criteria, in short |
| -- | --------- | ----------------------------- |

## Blocked

_Filed and unarmed, held by a blocking edge. The next sweep arms whichever of these
has had all its blockers close._

| id | Item | Blocked by | What closing it makes knowable |
| -- | ---- | ---------- | ------------------------------ |

## Filed

| id | Item | Route | Armed |
| -- | ---- | ----- | ----- |

## Rejected

| id | Candidate | Why |
| -- | --------- | --- |

## Swept

| Date | Lanes | Found |
| ---- | ----- | ----- |
```
