---
name: gc-fleet-metrics
description: Gather Gas City fleet metrics and write a scorecard — per agent type (runs, $, cost per task, pass and WORKED rates, waste), per node (lanes filed, completed, stuck), stalls and bottlenecks, quota burn, and before/after any config change. Use when asked for fleet or lane stats, agent cost, cost per task, how many lanes completed, where lanes stall or bottleneck, or whether a change helped.
---

# Fleet metrics

The city changes several times a day — provider pins, effort, pools, caps, routing rules. A
number that spans a change is the average of two fleets and describes neither. So every
figure in this report belongs to a **window**, and every window is cut into **epochs** at the
config changes inside it. Sources go stale and rotate; a figure whose source does not cover its
window is **UNREAD**, never zero. A percentile from fewer than 20 rows is **low_n**: a sample,
not a measure.

Paths below are relative to the city (`/home/coolhenrylinux/city`). The skill's own collector:

    M=~/.claude/skills/gc-fleet-metrics/scripts/fleet-metrics.py
    python3 $M [--days N | --since ISO --until ISO] [--json]      agents, nodes, stalls, bottlenecks, changes
    python3 $M --around <sha|ISO> [--hours H] [--json]             the same, H hours before vs after a change

Every metric, its source and its trap: [references/metrics.md](references/metrics.md).
Turning a stall signal into a cause: [references/stalls.md](references/stalls.md).

## 1. Fix the window and its epochs

Take the window the user named; default 7 days, ending now. Run `python3 $M --days N` and read
its CHANGES list: every commit in the window touching `city.toml`, `pack.toml`, `agents/`,
`prompts/`, `formulas/`, `orders/`, `hooks/` or the routing and pacing scripts, plus owner
rulings from `dispatch/ledgers/decisions.tsv`. Also read `git -C ~/city log --since=<window>
--format='%h %ad %s' --date=iso` for changes outside those paths the user mentions.

Mark as an **epoch boundary** every change that alters who runs a lane or how: a provider pin,
model, effort, pool size or suspension, slot cap, resource reservation, routing or fallback
rule, prompt or formula. Cosmetic commits (docs, ledgers, tests) are not boundaries.

Done when you hold the window, a list of epoch boundaries with sha, UTC time and one-line
effect, and the changes the user asked about are on it.

## 2. Make the sources cover the window

`fleet-metrics.py` prints `coverage` and a WARNING line per gap. Clear each:

| Warning / stale source | Refresh | Cost |
|---|---|---|
| session-facts older than window end | `python3 dispatch/session_facts.py collect --since <days+1>` | minutes; ssh to Dell and GTX |
| `session_ledger_age_h` over 6 | `python3 dispatch/session-ledger.py report --since <days>` | minutes; ssh |
| Mergify rows still queued | `python3 dispatch/mergify-metrics.py --reconcile --since <date>` | one gh call per PR |
| events.jsonl rotated inside window | lifecycle counts start at the rotation; older ones are in `.gc/events.jsonl.archive-*.gz` | read only if the user needs them |
| route.log starts after window | older lines are in `.gc/runtime/route.log.*.gz` (the script reads them) | — |

Done when `coverage` prints no WARNING, or each remaining warning is copied into the report
beside the figures it limits.

## 3. Collect

Run these in parallel; each is read-only. Keep their raw output in the scratchpad.

| Collector | Gives |
|---|---|
| `python3 $M --days N --json` | per agent type and per node tables, stalls, lifecycle events, bottleneck ranking |
| `python3 dispatch/city-metrics.py report --days N --json` | flow, queue/run by resource class, yield and grades, Ryzen/Dell/GTX slot saturation, reservation peaks and OOM, trains, PRs merged, rework, order yield, board size, mayor handoffs |
| `python3 dispatch/run-costs.py --since N --top 15` | $ by role and model across gc sessions and fleet lanes, top runs, **cost per task** (every dispatch on a work bead) |
| `python3 dispatch/mergify-metrics.py --since <date>` | merge queue: queued, landed, dequeue rate and causes, queue→merge p50/p90 |
| `python3 dispatch/claude-usage.py --json`, `codex-usage.py --host all --json`, `agy-usage.py --json` | subscription windows: % used and reset time per login and host |
| `python3 dispatch/hopscotch-usage.py --weeks 2` | real $ of the metered Muse dev credit (Ryzen only; wrangler) |
| `gc analyze reliability` | session crash / idle-kill / drain rates by model and prompt version |
| `.gc/runtime/fleet/session-facts/report-latest.md`, `.gc/runtime/fleet/mayor-flow/report-latest.md` | nightly 7-day pages: where session time goes, command-family failures, waste, mayor turn slowdowns |

Done when every collector has output or a recorded failure line (its stderr) — a failed
collector makes its section UNREAD in the report, never absent.

## 4. Split by epoch

For each epoch boundary from step 1 that falls inside the window, run
`python3 $M --around <sha> --hours H`, with H the smaller of 24 and the gap to the
neighbouring boundary, so neither side crosses another change. An after-side younger than the
node's `run90` still has lanes in flight: its pass and completion rates are biased toward fast
lanes. Say so, or shorten H on both sides.

Attribute a before→after move to the change only when the agents it touched moved and the
others held still; a move every agent shares is the load or the hour of day.

Done when every boundary has a before→after table or a stated reason it has none (low_n,
inside a source gap, too recent).

## 5. Diagnose stalls and bottlenecks

From the BOTTLENECKS ranking, the STALLS table, LIFECYCLE EVENTS and every STUCK line, name the
top three places lanes lose time, each with the signal, its count, the host or agent it sits on,
and the probe that confirms it (references/stalls.md maps signal to probe). Run the probe for
each; a cause you did not probe is labelled a hypothesis.

Done when each of the top three has a probed cause or is marked hypothesis, and every STUCK
lane is listed with its id, host and age.

## 6. Write the report

Save it as `reports/fleet-metrics-<UTC date>.md` and print it. Owner-facing times are Toronto
time; ids, shas and ledger rows stay UTC. Sections, in order:

1. **Headline** — window; lanes filed / completed / WORKED %; $ total and $ per WORKED lane;
   PRs merged; the single biggest bottleneck.
2. **Changes and epochs** — each boundary and its before→after deltas on the agents it touched.
3. **Agents** — one row per agent type: sessions, dispatches, sessions per dispatch, hosts, model,
   effort, wall h, idle %, p50/p90 minutes, $, $ per dispatch, $ per WORKED, pass %, WORKED %,
   waste minutes, low_n. Then cost per task (median, p90, top 5 tasks) from run-costs.
4. **Nodes** — per host: filed, launched, completed, prepared, failed, blocked, completed %,
   WORKED %, unjustified blocks, queue p50/p90, run p50/p90, slot saturation and idle %
   (city-metrics `capacity`), OOM and reservation peaks, top failure classes, stuck lanes.
5. **Stalls and bottlenecks** — step 5's top three with evidence, then the STALLS table.
6. **Flow beyond the lane** — merge queue (dequeue %, queue→merge p90), trains, PR open→merge,
   rework (fix-round share, retry %), board size, mayor handoffs per day.
7. **Quota** — each subscription login: % of 5-hour and 7-day windows used and reset time; Muse
   credit spent. Rank providers by allowance share consumed, not list $.
8. **Coverage and caveats** — every UNREAD, low_n and source gap from steps 2-4.
9. **Recommendations** — at most five, ranked by expected gain, each naming the metric and the
   value that would prove it worked.

Done when every section carries numbers or an UNREAD with its reason, every comparison names
its epoch, and each recommendation names a metric to watch.

## 7. Record the baseline

When the window ends at a clean seam (no train landing, no fleet reload in flight), append one
row with `python3 dispatch/city-metrics.py record --days N`, so the next run compares against
it. If the user will share the report, offer to publish it as an artifact.
