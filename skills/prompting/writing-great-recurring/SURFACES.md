# Surfaces — reference

The full decision reference behind the table in [`SKILL.md`](SKILL.md). Per
surface: what it costs, what it can and can't see, the failure mode of picking it
wrong, and how to inspect and cancel it. Mechanics live in each surface's own
contract — the `/loop` and `/schedule` skills, and the `ScheduleWakeup`,
`CronCreate`, and `Monitor` tool docs; this file only covers choosing between them.

Tool names vary by harness: `CronCreate` or `ScheduleWakeup` may be absent, and
`/schedule` may resolve to a scheduled-tasks MCP or a cloud-routines API. The
rows and failure modes hold either way — but before wiring or handing over
controls, check which names actually resolve here and use those.

## `/loop` with an interval

Re-invokes the prompt in this session on a fixed cadence.

- **Lives:** this session — a closed session takes the loop with it.
- **Cost:** every firing is a full turn in this session — tokens, context growth,
  and the session must stay open for the routine to live.
- **Sees:** the whole conversation — files read, decisions made, what earlier
  firings found. **Can't:** outlive the session.
- **Wrong pick:** a 60s interval on state that changes hourly burns ~59 wasted
  firings per real change — the interval must come from the watched state, not
  from wanting to feel responsive. And any state the routine must survive belongs
  on `/schedule`, since a closed session takes the loop with it.
- **Inspect / cancel:** the loop is visible in-session; the user interrupts or
  asks to stop it at any time.

## `/loop` with no interval → `ScheduleWakeup`

The model schedules its own next wakeup each turn, delay clamped to [60, 3600]s,
with a stated reason the user sees.

- **Lives:** this session.
- **Cost:** same session-turn cost as `/loop`, plus the routine spends judgment
  each firing choosing the next delay.
- **Sees:** session context, like `/loop`. The per-wakeup `reason` doubles as the
  routine's visible heartbeat.
- **Wrong pick:** self-pacing a fixed external schedule wastes the flexibility —
  use cron. Worse: short wakeups polling harness-tracked work duplicate a
  notification that is already coming; the contract's own guidance is a long
  fallback (1200s+) at most.
- **Inspect / cancel:** each wakeup announces its reason; cancel with
  `ScheduleWakeup {stop: true}` or by telling the session to stop.

## `/schedule` → `CronCreate`

A prompt on a 5-field cron, each firing a fresh agent. Two homes share the
contract: `/schedule` creates persistent cloud agents that outlive this session —
the default for standing routines — while `CronCreate` jobs are session-local
(gone when the session ends, auto-expire after 7 days), fit for a routine scoped
to today's work.

- **Lives:** `/schedule` outlives every session — the only row that does;
  `CronCreate` jobs die with the session. A weeks-scale signal or a standing
  policy belongs here for lifetime alone, even when a condition row also fits.
- **Cost:** cheap to register; each firing runs without touching this session's
  context or tokens.
- **Sees:** only what the prompt says and what it can re-read from the world —
  the repo, APIs, files. **Can't:** see this conversation or any prior firing's
  reasoning. The prompt must be self-contained, and cross-firing memory must live
  somewhere durable the next firing re-reads.
- **Wrong pick:** a cron agent for work that needs session context wakes up
  amnesiac every firing — it re-derives what the session already settled, or
  re-does it.
- **Inspect / cancel:** `/schedule` list/update/delete for cloud agents;
  `CronList` / `CronDelete` for session jobs.

## `Monitor`

Waits on a condition rather than a clock — a script whose stdout lines become
events, or a WebSocket. Fires exactly when the condition becomes true.

- **Lives:** this session — a watcher that can't survive to its own event
  (a weeks-scale condition) belongs on `/schedule` instead.
- **Cost:** one background process; every event line lands as a conversation
  message, so the filter must be selective.
- **Sees:** only what its script observes — but events arrive in this session,
  which has full context to act on them.
- **Wrong pick:** a clock surface aimed at a condition re-asks "anything yet?" on
  every firing; a `Monitor` answers once, the moment it's yes. The inverse trap —
  an unbounded `Monitor` for a single notification — is covered by the tool's own
  contract (use background `Bash` with an `until` loop instead).
- **Inspect / cancel:** `TaskList` to see it, `TaskStop` to end it.

## Background `Bash` / `Agent`

Not a surface to stand up — harness-tracked work re-invokes you on completion, so
the notification is built in. Also the home for a **first-occurrence-only**
condition wait: an `until`-style loop that exits when the condition trips is one
notification, per the `Monitor` contract's own rule.

- **Lives:** until the process exits; in-session.
- **Cost:** zero beyond the work itself.
- **Wrong pick (the trap):** any timer polling harness-tracked work duplicates
  the notification that's already coming — pure waste. Correct: nothing, or a
  single long fallback wakeup (1200s+) in case the work hangs without exiting.
- **Inspect / cancel:** `TaskList` / `TaskOutput` to check on it, `TaskStop` to
  kill it.
