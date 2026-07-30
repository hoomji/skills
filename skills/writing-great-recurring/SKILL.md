---
name: writing-great-recurring
description: Stand up a recurring routine end to end — pick the surface, write the recurring prompt, wire it, and verify the first firing.
disable-model-invocation: true
argument-hint: "The recurring-work request to stand up"
---

# Writing Great Recurring

Take a recurring-work request and stand the routine up end to end. A routine is
judged by its hundredth firing, not its first — every step below exists so firing
#100 is still cheap, still idempotent, and still tells the user something.

## The surface table

Pick by what the routine **waits on** — the awaited signal, never the surface you
reached for last time.

| Waiting on | Surface | One line |
|---|---|---|
| A fixed cadence, needing this session's context | `/loop <interval>` | Re-invokes the prompt here on the interval. |
| A signal with variable pacing, in this session | `/loop` (no interval) → `ScheduleWakeup` | The model picks each delay, clamped to [60, 3600]s. |
| A wall-clock schedule, no session state needed | `/schedule` → `CronCreate` | A cron-scheduled agent; fresh context every firing. |
| A condition, not a clock | `Monitor` | Streams an event the moment the condition fires — no polling prompt at all. |
| Completion of work already started | Background `Bash` / `Agent` | The harness re-invokes you when it finishes — nothing to stand up. |

When two rows fit, or you need a surface's cost, visibility, wrong-pick failure
mode, or its inspect/cancel commands, read [`SURFACES.md`](SURFACES.md).

## Steps

### 1. Name what it waits on

Write down three things: the **awaited signal** (a clock tick, a schedule, a
condition becoming true, or completion of work already started), the
**termination condition** (when the routine ends, including a concrete test for
"nothing new"), and the **actions** each firing may take, split into reversible
and not.

Two asks end here with nothing stood up:

- It fires **once** — do the one-shot (or offer to) and say why no routine exists.
  A one-shot at a *future* time still gets registered: the scheduling surface's
  one-time mode (`fireAt` / `recurring: false`), never a recurring cron expression.
- It waits on **harness-tracked work** (a background `Bash` or `Agent` task) —
  the completion notification is already coming, and a poll duplicates it. Say
  so; add at most a long fallback wakeup (1200s+) if the work could hang silently.

*Done when:* signal, termination, and actions are each written down — or the ask
is correctly declined with the reason stated.

### 2. Pick the surface

Match the awaited signal to one row of the table. A condition beats a clock: when
the ask is "when X happens," reach for `Monitor` before any interval, however
natural an interval sounds. For a condition, also declare which reading you took:
**every occurrence** is `Monitor`; the **first occurrence only** is one
notification, which belongs on background `Bash` with an `until` loop (the
`Monitor` contract's own rule). When the phrasing is ambiguous, name your reading
and offer the flip.

*Done when:* one surface is named with the row that selected it — and if two rows
fit, the tie was broken on wrong-pick failure modes from
[`SURFACES.md`](SURFACES.md), not on familiarity.

### 3. Write the recurring prompt

Draft the prompt a single firing will receive. It must answer all six gates:

1. **Cadence** — derived from how fast the watched state actually changes. A CI
   run that takes ~8 minutes earns one ~480s check, not eight 60s ones; issues
   that arrive daily earn a daily firing. A cadence the user named for batch
   work survives as the report or heartbeat rhythm even when detection goes
   event-driven — honor the number, convert the mechanism, and say so.
2. **Termination** — when the routine stops, and the concrete test for "nothing
   new."
3. **Memory** — what the next firing must know about the last one, and where that
   lives. A `/loop` firing has the session; a cron firing wakes amnesiac, so its
   memory must live somewhere durable it re-reads — a state file, labels, a
   comment marker.
4. **Idempotence & blast radius** — a firing that finds its work already done
   does nothing; a routine that fires 100 times must not act 100 times. Name
   which actions a firing takes autonomously and which it only surfaces for
   confirmation (anything irreversible or outward-facing: closing, sending,
   deleting, publishing).
5. **Failure** — what a failed firing does (skip, retry, alert), and how the user
   notices the routine has died or gone stale rather than merely gone quiet.
6. **Quiet report** — the one line a firing emits when nothing happened. Silence
   is indistinguishable from dead.

*Done when:* reading the prompt back, each of the six gates has an explicit
answer in its text.

### 4. Wire it

Register the prompt on the chosen surface, following that surface's own contract
for mechanics — the `/loop` and `/schedule` skills, and the `ScheduleWakeup`,
`CronCreate`, and `Monitor` tool contracts — rather than reinventing them.

*Done when:* the routine is registered and appears in its surface's listing (for
`ScheduleWakeup`, the first wakeup is scheduled with a specific reason).

### 5. Verify the first firing, then hand over the controls

Watch the first firing run — or force one when the first natural firing is far
off: run a cron prompt once by hand, append a synthetic matching line for a
`Monitor`. Check its output against the shape from step 3: it acted (or correctly
surfaced for confirmation), and the quiet path emits its report. Then give the
user the inspect and cancel commands for this surface (per-surface list in
[`SURFACES.md`](SURFACES.md)) — quoting only commands that resolve in this
harness; tool names vary by environment, so check before handing them over.

*Done when:* one firing has actually run and produced the intended shape, and the
user has been told how to inspect the routine and how to cancel it.
