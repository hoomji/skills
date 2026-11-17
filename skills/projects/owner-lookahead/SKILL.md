---
name: owner-lookahead
description: Owner look-ahead brief — high-priority work (epics, CI/CD, merging, Gas City) in flight now, queued next, and planned later, plus the decisions ahead on it, each with an exec summary and recommendation.
disable-model-invocation: true
---

# Owner look-ahead

Write the owner a **brief** on the road ahead: what is *in flight*, what is *next*, what is *later*, and the decisions that work will hit before it lands. The forward twin of `owner-catchup` — same reader, same bar: every line stands on its own without opening a link.

Horizons:
- **Now** — a live lane, an open PR, a bead `in_progress`.
- **Next** — ready or queued to dispatch within ~3 days: `ready` beads, held dependents, PRs waiting on a gate.
- **Later** — planned but not yet ready: released epics, ledger-only epics, parked work.

The argument narrows scope (`epic 51`, `ci`, `gas city`); none means everything high-priority.

## 1. Harvest the pipeline

Evidence is live state, never a plan's claim: a lane is in flight only if its session is alive or its branch moved in the last 24h; a PR is open only per `gh`. Sweep every source; a source you could not read is named in the brief as a gap.

- **Gateway-LLM PRs** — `gh pr list -R Uniblock-dev/Gateway-LLM --state open --json number,title,labels,isDraft,mergeStateStatus,reviewDecision,updatedAt,body`. Read the merge-queue state (Mergify) for each.
- **Hoppy-city PRs** — same query with `-R Uniblock-dev/Hoppy-city` (PRs target `main`; the mayor merges them per R-20261101-02). Plans live in its repo (`_bmad-output/` on `main`) and Linear HOP-* issues. Report it as its own line in each horizon.
- **Beads** — `gc bd list --status in_progress` and `--status open` for rigs `gateway-llm`, `hoppy-city` and `city`; `gc bd ready` for what dispatches next. Keep epics, P0/P1, and anything blocking them. `gc bd show` for notes and deps.
- **Lanes** — `gc session list` and `.gc/runtime/fleet/jobs/` for live dispatches; flag any stalled >30m.
- **Plans** — the sprint tracker (`sprint-status.yaml` on `origin/develop`), released/parked epic ledgers, the mayor memory's *Active work* entries, open `OWNER-DECISION:` beads.
- **CI/CD and merging** — the latest `develop` and `main` runs, `merge-queue-health.jsonl`, any billing wall or pending gate/ratchet change.
- **The owner's Linear queue** — `~/city/.gc/runtime/my-linear/latest.json` when under 12 h old, else `python3 ~/city/dispatch/my_linear.py --json` (rules: `~/city/docs/my-linear.md`), and the first pass's verdicts in `firstpass.json` beside it. A fresh `needs_owner` verdict is a decision ahead with its question and recommendation already written; a `no_change` summary often names the release or person an item waits on, which is its blocker. Place each bucket like this. `moving` items with an open bead or PR are Now. A started `orphan` says In Progress while nothing runs, so it is never Now: put it in AT RISK. `decide` items and Spec Review go to DECISIONS AHEAD as owner. `parent` items marked `stale` and the epics under the owner's initiatives (the Linear connector's `list_initiatives`, owner `me`) are Later, with the next sub-issue named.

Filter CodeRabbit before counting anything.

Done when: every source was read or named as a gap, and every kept item carries its evidence (PR #, bead id, session, or ledger line).

## 2. Place and rank

Put each item on exactly one horizon. Keep it only if it will move an epic's completion, production behavior (deploys, money paths, customer data), the merge pipeline, or fleet capacity. Collapse trains into one line per outcome with an ETA or the blocker standing in its way — "Epic 51: 2 stories left, both in lens; lands ~Mon if gate 4 passes" beats a list of beads.

Done when: each line names an outcome, a horizon, and either an ETA or its blocker.

## 3. Find the decisions ahead

A decision ahead is a fork the work will hit before it lands — scope, approach, sequencing, spend, risk. Look for it in blockers, BLOCKED receipts, spec open questions, competing PRs on one file set, epics whose next story has two plausible shapes, and anything touching the four reserved subjects (`agents/mayor/prompt.template.md` "Authority and parking").

Mark each one **owner** (a reserved subject — the owner must rule) or **mayor** (the mayor will decide and act on its recommendation unless the owner overrides). Give every decision an exec summary:
- *Question* — one sentence.
- *Horizon & deadline* — when the work hits the fork, and what stalls if it is unsettled by then.
- *Context* — 2–3 lines: why it arises, what it touches.
- *Options* — 2–3, each with its cost.
- *Recommendation* — one option and why.

Done when: every Now and Next item was checked for a fork, and every decision has a recommendation the reader could rule on without opening anything.

## 4. Deliver

Reply in this shape, times in Toronto time:

```
Look-ahead as of <now, Toronto>

DECISIONS AHEAD (n)    ← owner-marked first, then by deadline
NOW                    ← in flight: outcome · evidence · ETA/blocker
NEXT                   ← ~3 days
LATER                  ← planned
AT RISK                ← stalls, walls, red develop; one line each
GAPS                   ← sources not read
```

Lead with DECISIONS AHEAD even when empty ("no forks ahead"). Then append `<UTC ts>\tlookahead\tbrief\t<n now/next/later, n decisions>\t-\tdelivered` to `dispatch/ledgers/decisions.tsv`.
