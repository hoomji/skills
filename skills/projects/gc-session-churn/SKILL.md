---
name: gc-session-churn
description: Identify and recover from short-lived codex sessions that discard uncommitted work. The reconciler aggressively retires pool slots, causing session churn where 46% of sessions die under 5 minutes. Stranded sessions trigger bead.dead_assignee_reopened, abandoning work in progress. Watch for session.stranded and session.drain_acked_with_assigned_work.
---

# Recovering stranded codex sessions and measuring churn

The reconciler retires pool slots aggressively, leading to session churn. If a lane is holding assigned work when it drains or strands, the in-progress uncommitted work on its branch is abandoned.

A 2026-09-13 measurement forms our baseline:
- **Churn:** 46% of 35 codex sessions lasted under 5 minutes. (Median lifetime: 7.8 min, Mean: 11.8 min).
- **Stranded beads:** 4 sessions threw away work on 15 beads that had to restart from scratch.
- **Drain with work:** `session.drain_acked_with_assigned_work` hit 14 times in 8 hours.

When a codex lane strands, its beads reopen via `bead.dead_assignee_reopened` but lose all uncommitted work. Rescue the branch with `git ls-remote` first, then re-sling.

## 1. Detect session churn and stranded work

Read the city event log for the specific events:

```bash
grep -E 'session\.stranded|session\.drain_acked_with_assigned_work|bead\.dead_assignee_reopened' <city>/.gc/events.jsonl
```

To calculate the session lifetime and count short-lived sessions, extract session start and end times from the event log or use jq over `events.jsonl` matching `session.started` and `session.ended` / `session.stranded`. 

Complete when you have a count of recent `session.stranded` and `session.drain_acked_with_assigned_work` events.

## 2. Rescue stranded branches (strand recovery)

When you see a `bead.dead_assignee_reopened` event, the bead has been put back into the queue, but its prior assignee's branch might hold uncommitted work. The dead lane can leave a pushed branch behind that is invisible to the bead and to `gh pr view`.

```bash
# For a reopened bead <id>
git ls-remote origin | grep <id>
```

If a branch exists, rescue its work: check it out, inspect it, commit anything useful, and make sure the new assignee gets this branch instead of starting from scratch. Re-sling the bead onto the rescued base.

Complete when you have checked `git ls-remote` for reopened beads and rescued any abandoned branch work before re-slinging.
