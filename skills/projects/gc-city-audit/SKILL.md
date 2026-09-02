---
name: gc-city-audit
description: Audit a Gas City (`gc`) city and repair its drift — autonomy (wake orders, lane caps, merge policy), context (window knobs, hooks, prompt weight), efficiency (provider pins, idle sessions, store and log growth), config sediment. Use when the user asks to audit, tune, health-check or improve a city, when a mayor stalls or stops waking, or after an owner instruction changes lanes or caps.
---

# Gas City audit

A city accumulates **claims** — comments in `city.toml`, memory rows, prose in the
autonomy contract — and the runtime quietly stops matching them. The audit treats every
claim as a hypothesis and every `gc` command as the **probe** that tests it. **Drift** is
the gap between the two, and the report is a ranked list of drift with the probe that
proved it. Never grade a plane from a comment, a memory row, or `last_active`.

Read [`references/probes.md`](references/probes.md) before step 2: it carries the exact
command and pass condition per check, and the traps that make a probe lie.

## 1. Scope

Resolve the city root (`gc --city` or walk up), the rigs, `gc version`, and the autonomy
contract in force (any `*AUTONOMY*.md` or `MAYOR-STATE.md` at the root). Confirm the
controller is live with `gc status`; a status probe timeout is itself a finding, not a
reason to stop. Mode is **audit** (read-only, the default) unless the user said fix,
repair, or improve — then it is **fix**, and step 4 runs.

Done when: city root, gc version, rig list, contract file, controller state, and mode are
written at the top of the report draft.

## 2. Probe every plane

Run every check in every plane below. Record per check: probe run, observed value, claim
it tests (file:line or memory row, or "none"), verdict PASS / DRIFT / UNKNOWN. A probe
that cannot run is UNKNOWN with the error text, never a silent PASS.

**Autonomy** — can the city make progress with nobody watching?
- Wake: every wake the contract names is in `gc order list` output, not just on disk. A
  file under `orders/` that the controller does not list is the highest-severity drift.
- Standing authority: the contract states what may be dispatched, merged, and parked
  without asking, and the park protocol clears routing metadata (not only status).
- Lane caps: live session count per provider versus the cap the contract states. Pools
  auto-spawn for routed beads and breach caps silently; count sessions, not slings.
- Merge policy: `[[github.pr_monitor]].merge_queue`, repair route, and whether anything
  can create repair beads for PRs the owner does not author.
- Stranded work: detached worktree HEADs and unpushed branch tips in each rig.

**Context** — does each session see what it needs and hand off before it drowns?
- Window knobs: `GC_CONTEXT_*` in `.gc/settings.json` against the model each lane
  actually resolves to (probe the provider, do not read the comment).
- Hooks: PreCompact hands off; SessionStart primes exactly once (guarded against the
  double-delivery); UserPromptSubmit drains nudges and mail with a timeout.
- Prompt weight: bytes of the mayor prompt template, the state file, and the memory
  index, and how much of each is live versus archive. Prose carrying counts or dates
  that a probe can produce is a cache that goes stale.
- Handoff path: the contract names `gc handoff`, never `gc session reset` on a live
  controller.

**Efficiency** — is spend going to work?
- Provider pins: for each `[providers.*]` and `[[patches.agent]]`, what the lane really
  launches (process args, `claude -p` probe, provider log), versus the pinned intent.
- Idle sessions: sessions whose peek tail is unchanged across two samples two minutes
  apart, and sessions of roles the config says have no consumer.
- Usage facts: `gc costs` coverage per provider; a provider with no facts is unmetered,
  not free.
- Store and log growth: dolt size and live-row ratio, `events.jsonl` size, open bead
  census (notification and tracking beads versus claimable), retention policies set.
- Review budget: CodeRabbit reviews remaining and whether fix pushes are batched.

**Config hygiene** — is the config one source of truth?
- Resolved versus written: `gc config show` and `gc config explain` for every value a
  comment claims; unknown-field warnings; option values the loader accepts but does not
  validate.
- Sediment: backup copies beside live files (`*.bak*`, `*.pre-*`, `*.prev-*`), patches
  naming roles no pack provides, providers with no consumer, disabled orders that are
  still in a scanned directory, `packs.lock` fetch age against upstream.
- Pack cache: the copy `packs.lock` pins is the one on disk.

**Liveness** — can the operator tell alive from dead?
- `last_active` is a heartbeat, so session liveness comes from hashed peek tails.
- `gc analyze reliability` instrumentation gaps; dead-letter nudges in `gc nudge status`.
- Wait registry: `gc wait list` for waits nothing will ever mark ready.

**Safety** — what can go wrong unattended?
- Dangerous-permission prompts skipped; git guardrails on shared checkouts; formulas
  whose default expands a bare sling into a non-isolated worktree; secrets referenced by
  env name only.

Done when: every check above has a verdict row, and every DRIFT row cites its probe
output and the claim it contradicts.

## 3. Rank and report

Rank DRIFT by blast radius: stalls the whole city (a wake that does not tick, a lane
that is logged out) → wastes spend (idle sessions, unmetered lanes, unbounded logs) →
misleads the next operator (stale comments, sediment). For each, one paragraph: the
drift, the probe that proved it, the fix, and whether the fix is reversible.

Write the report to `<city>/audits/<YYYY-MM-DD>-gc-audit.md`. Retire prior reports
into `<city>/archive/` rather than leaving siblings in `audits/`.

Done when: the report exists, every row from step 2 appears in it, and the ranked
section lists fixes with a reversibility flag.

## 4. Fix (fix mode only)

Apply fixes in rank order, reversible ones only, one at a time, using the recipes in
[`references/fixes.md`](references/fixes.md). After each: `gc config show` loads
clean, `gc doctor` reports no new failure, the probe that proved the drift now passes.
Irreversible fixes (deleting beads, pruning sessions, purging logs, rewriting shared
checkouts, changing merge policy) are **parked**: listed under OWNER-DECISION in the
report with the exact command, never run.

A fix that changes a claim also updates the claim: edit the comment or memory row the
probe contradicted, in place. Back up a config file once into `<city>/archive/` with a
dated name; never as a sibling `.bak`.

Done when: every reversible fix is applied and re-probed PASS, every irreversible one is
parked with its command, and the report's ranked section shows the post-fix verdict.
