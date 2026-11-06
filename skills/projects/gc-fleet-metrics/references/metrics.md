# Metric catalogue

Each metric: what it measures, where it comes from, and the trap that makes it lie.
Definitions shared with the mayor's scorecard live in `docs/city-metrics.md`; this page adds the
per-agent, per-node and per-epoch views and the traps met while building them.

## Identity: what an "agent type" is

| Kind | Example agent names | Type (as printed) |
|---|---|---|
| Fleet lane pools on each rig | `gateway-llm-gtx/dsh-muse-3`, `gateway-llm/codex-sol-1` | `dsh-muse`, `codex-sol`, `claude-review`, `codex-browser` |
| City seats | `mayor`, `ci-controller`, `receipt-grader`, `fleet-watcher`, `backlog-curator` | same |
| Pack agents | `bd.dog-1`, `gateway-llm/bmad.edge-case-reviewer` | `bd.dog`, `bmad.edge-case-reviewer` |
| No agent bound | the owner's own Claude/Codex sessions | `(interactive)` |

The type strips the rig prefix and the slot number, so one pool on three hosts is one row; its
`hosts` column splits it again. The configured roster (provider per agent) is
`gc config explain | grep -A2 '^Agent:'`; suspended agents are in `gc agent list`. A configured
agent with no row ran nothing in the window — report it as idle, never drop it.

## Volume

| Metric | Source | Trap |
|---|---|---|
| sessions | session-facts rows by `start` in window | dsh writes many session files per dispatch: `dsh-muse` runs ~20 per dispatch, so compare dispatches, not sessions, across providers |
| dispatches | distinct fleet dispatch ids joined to a session (by `dispatch_id`, else receipt `session_id` ∈ `gc_sessions`) | seats (mayor, ci-controller) have none by design |
| sessions per dispatch | sessions / dispatches | a rise after a change is restart churn: see `gc-session-churn` |
| filed / launched / receipts per node | jobs `created`, route.log ROUTED, receipts | a job is placed on the host in its ROUTED line; `requested_host` is a wish |

## Completion and yield

| Metric | Definition | Trap |
|---|---|---|
| completed | receipt verdict PASS or ALREADY-FIXED | PREPARED is a stage (prepare → validate), counted separately, never as done or failed |
| completed % | completed / receipts | read lanes (reviews) PASS more than write lanes; compare nodes by class (`by_class`) before blaming a host |
| WORKED % | mayor grade WORKED / graded (`dispatch/ledgers/model-grades.tsv`) | **the** yield number: raw FAIL includes false FAILs on delivered work (memory: fail-receipt-can-wrap-delivered-work) |
| BLOCKED-UNJUSTIFIED | lanes that stopped when they could have continued; cause column says why | the actionable part of BLOCKED |
| failure_class | receipt field: task, environment, external-permanent, unverified-pass, missing-evidence, launch-stall, resource | `environment` and `resource` are fleet faults; `task` is the lane's |
| delivered | a PR head on the remote, never a closed bead (memory: bare-closed-is-not-delivery) | count merged PRs from gh, not bead closes |

## Cost

| Metric | Source | Trap |
|---|---|---|
| $ per agent | session tokens re-priced from `city.toml [[pricing]]` (`dispatch/prices.py`) | Claude and Codex are flat subscriptions: $ is list-price **equivalent**, used to compare, not a bill |
| unpriced | model with no rate | Muse (`meta/muse-spark-*`) has no rate: its real $ is the dev credit in `hopscotch-usage.py` |
| $ per dispatch, $ per WORKED | agent $ / dispatches, / WORKED grades | $ per WORKED is the efficiency figure: cheap lanes that fail cost more per delivered lane |
| cost per task | `run-costs.py`: every dispatch on one work bead (implementation, lenses, retries) | one runaway bead (50+ dispatches) dominates the mean: report median and p90 |
| quota share | `claude-usage.py`, `codex-usage.py`, `agy-usage.py` | compare providers by share of allowance burned (memory: subscription-discount-ratios), and note each reset time |

## Time

| Metric | Source | Trap |
|---|---|---|
| queue wait | jobs `created` → route.log ROUTED | a job re-QUEUED every tick logs one QUEUED line per tick: count distinct ids |
| lane run | ROUTED → receipt mtime | a receipt rewritten later (re-grade, reseal) moves its mtime |
| wall / idle % | session-facts `wall_s`, `idle_s` (silence > 5 min with no tool running) | high idle on codex-sol and bmad lanes is waiting on a resource scope or a child, not thinking |
| by resource class | city-metrics `speed_min.by_resource` | build and test lanes wait for 8 GiB reservations only Ryzen holds |
| PR open → merge, queue → merge | city-metrics `merged`, mergify-metrics | merges queued outside land.sh are not in mergify.jsonl |

## Waste and health

| Metric | Source | Meaning |
|---|---|---|
| waste fail min | session-facts `waste.fail_s` | seconds spent in commands that failed |
| waste poll min | `waste.poll_repeat_s + stale_repeat_s` | re-running the same status check |
| ctx peak, compactions | session-facts | a lane near its window compacts and loses its plan |
| rework | city-metrics `fix_round_share_pct`, `retry_pct`, `write_same_title_refile_pct` | work paid for twice |
| capacity | city-metrics `capacity.<host>`: saturated / idle / unavailable / veto % of sampled minutes | idle while the queue is non-empty is placement loss; check `coverage_pct` first |
| reservation use, OOM | city-metrics `capacity.reservation_use` | `peak_over_limit` near 1 is OOM risk; OOM kills by class |
| lifecycle events | `.gc/events.jsonl` | rotates daily-ish; `gc analyze reliability` gives rates but its model column is empty here (worker.operation carries no model) |
| board | city-metrics `board` | open beads per store; goal is down |
| mayor | city-metrics `mayor.handoffs_per_day`, mayor-flow report | restarts and slow turns |

## Epoch comparison

`fleet-metrics.py --around` compares the same metrics in equal windows either side of a change.
Read it with three checks: both sides have n ≥ 20 for the agent in question; the after-side is
older than the node's run p90 (else in-flight lanes bias it); and the agents the change did not
touch held still. A change made while another was in flight cannot be separated — say so.
