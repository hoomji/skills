# Stall signals → probe → likely cause

A stall signal says where a lane waited, not why. Each row names the probe that turns the
signal into a cause. Memory names are files under
`~/.claude/projects/-home-coolhenrylinux-city/memory/`; skills are `gc-*`.

## route.log verbs (STALLS table)

Lines repeat once per backlog tick while the condition holds, so rank by **distinct**, not lines.

| Verb | Means | Probe | Usual cause |
|---|---|---|---|
| QUEUED … no free slot in X | job waited for a slot | city-metrics `capacity.<host>` saturated % and `speed_min.by_resource` queue p90 | build/test reservations (8 GiB) fit only Ryzen; a typecheck burst fills Dell/GTX |
| QUEUE-FULL | backlog queue at its cap | `grep QUEUE-FULL .gc/runtime/route.log \| tail` for the cap; open + queued jobs | filing outran capacity; the cap is policy, not a fault |
| REQUEUED … host capacity exhausted | launch refused after placement | `dispatch/fleet-baselines.sh` (load, RAM, swap per host) | host over its memory veto |
| FAIR-WAIT | small job held behind an aged peak reservation | the named aged job: is it itself waiting on a running scope? | head-of-line blocking (docs/city-metrics.md backlog item 8) |
| LAUNCH-STALL | launched, nothing claimed it | the reason text: `pool-suspended` → `gc agent list`; otherwise peek the pool's pane | suspended pool; quota wall shown as a create loop (memory dsh-quota-wall-is-a-session-create-loop); orphaned finalize (memory orphaned-finalize-blocks-control-dispatcher) |
| UNREACHABLE host | backlog scan skipped that host's store | `ssh <host> true`; skill `gc-host-health` | ssh, dolt, or import-cache drift on the remote |
| ORPHAN NEEDS-REPO / MAYOR-QUEUE / UNROUTED | bead eligible but nothing routes it | the bead's `gc.repo`, `gc.routed_to` | missing repo label (memory city-work-needs-repo-city); `routed_to=mayor` waits for the mayor (memory gate-bead-route-clear-needs-routed-to-mayor) |
| HELD completion mail | routing paused on unread completion mail | mayor inbox count | mayor behind on mail; skill `gc-mail-backlog` |
| RETRY | a dispatch re-filed after FAIL/BLOCKED | the failed receipt's `failure_class` (`dispatch/receipt-show.py <id> --receipt-only`) | environment or resource class → fleet fault; task → brief or model |
| PR-CONFLICT, STRANDED-BASE, PARENT-GONE | PR needs a rebase or lost its stack parent | `gh pr view <n> --json mergeable,baseRefName` | develop moved; stacked parent closed |
| WITHDRAWN | mayor or rule pulled a job | the reason text | deliberate; count only if it rises after a change |

## Lifecycle events (LIFECYCLE EVENTS)

| Event | Probe | Usual cause |
|---|---|---|
| session.demand_claim_divergence | per pool: does demand exist with no live claimer? | dead fleet step spawning pool sessions (memory dead-fleet-step-spawns-pool-sessions) |
| session.drain_acked_with_assigned_work, bead.dead_assignee_reopened | `git ls-remote origin \| grep <bead>` for stranded pushes | session churn discarding work: skill `gc-session-churn` |
| session.idle_killed | was the session holding a claim? | normal reaping when idle; a fault only with a claim |
| bead.claim_rejected | repeating for one bead? | actor shadowing (memory claim-rejected-loop-is-beads-actor-shadowing) or re-served claim (memory re-served-claim-loops-the-guard) |
| session.crashed | the pane's last lines | provider or harness error |
| order.failed | `gc order history <name>` | the order's own exit; an order that ran is not proof it worked (memory order-executed-is-not-evidence-of-effect) |

## Node-level shapes

| Shape | Read | Usual cause |
|---|---|---|
| one host's run p90 far above the others | its `by_class` mix and city-metrics `by_resource` | that host takes the long classes (build, test); not slower hardware |
| completed % low on one host, WORKED % normal | false FAILs or read-heavy mix | grade is the yield; check failure_class |
| STUCK lane (running past the node's p90, floor 60 min) | `dispatch/receipt-show.py <id> --job-only`; peek the lane pane | quota wall at prompt (memory codex-walled-lane-idles-at-prompt-after-reset), waiting on a child scope, or lost session |
| spawning stops on one host while queue holds | dispatcher trace tail | wisp_gc stall after reload (memory reload-resets-wisp-gc-and-stalls-spawning); orphaned convoy controller (memory orphaned-convoy-controller-blocks-ryzen) |
| high idle % on an agent | session-facts `partition_s` for that agent | waiting on resource scopes or polling |

## Beyond the lane

A lane can finish fast and its PR still wait. Read `mergify-metrics.py` dequeue rate and
queue→merge p90, city-metrics `merged.open_to_merge_p90_h` and `trains`. Repeated check
dequeues on the same test file across PRs is a flake (`dispatch/flake-lanes.py --dry-run`); a red
PR with no fix round is `dispatch/red-fix-rounds.py --dry-run`.
