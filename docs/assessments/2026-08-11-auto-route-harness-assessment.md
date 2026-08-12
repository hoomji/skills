# Harness Assessment — `auto-route`

> **Scope banner — read first.** This assessment was run against
> **`henry/heartbeat-control-durability` @ `2ae706c`**, not against the branch it is stored
> on. `henry/ai-workflow` is **not an ancestor** of that commit
> (`git merge-base --is-ancestor henry/ai-workflow 2ae706c` → false), and it carries a
> substantially more complete harness. Several findings below — B1, the Lifecycle finding,
> and four of the six "dead pointers" — **do not hold on this branch**. See
> [§9 Delta on `henry/ai-workflow`](#9-delta-on-henryai-workflow) for the verified
> differences before acting on anything in §3.

**Date:** 2026-08-11
**Assessed branch:** `henry/heartbeat-control-durability` @ `2ae706c`
**Stored on:** `henry/ai-workflow`
**Assessed by:** `/harness-assess` (R0 inspect)
**Contracts:** `~/.claude/skills/harness/references/contracts.md`

**Run class: R0 (inspect).** No repository files were modified during assessment, no
dependencies installed, no services started, no caches mutated, no external write calls.
`gh` was used read-only (`issue view`, `label list`, `api .../protection`). This document
is the only artifact written, at the destination the maintainer authorized.

---

## 1. Scope and state

| | |
|---|---|
| Repository | `/Users/hoomji/Documents/VS/Github/auto-route` (`Uniblock-dev/auto-route`) |
| Branch / HEAD | `henry/heartbeat-control-durability` @ `2ae706c` |
| Dirty state | 2 untracked dirs only: `.sandcastle/`, `.worktrees/` — no modified tracked files |
| Worktrees | 12 attached (`git worktree list`): 8 `agent-<hash>` detached, 2 `sandcastle/issue-*`, 2 named-slug detached |
| Scale | 959 files scanned, 303 `.py`, 133 `test_*.py` files |
| Excluded | `.venv/`, `node_modules/`, `__pycache__`, `.git`, all sibling worktrees, `.env`, `gcp-credentials.json` (present in tree, gitignored — not read) |

### Tracer workflow

**Take a `ready-for-agent` issue (e.g. #129), implement it in an isolated worktree,
verify, open a PR, land it in the stack.**

This is the repo's actual observed loop — `.sandcastle/logs/` holds per-issue
implementer/reviewer logs for #112–#118, and HEAD is a chain of `sandcastle/issue-NN`
merges. All bottleneck ranking below is against this workflow.

### Commands executed

`git rev-parse/status/branch/worktree/ls-files/check-ignore/grep`,
`.venv/bin/{python,ruff,mypy,pytest,lint-imports} --version`, `find`, `grep`, `gh` reads,
`python3 <skill>/scripts/inventory.py`.

**No repository gate was executed.** `make verify`, `make test`, `ruff`, `mypy`, and
`lint-imports` all write caches (`.ruff_cache`, `.mypy_cache`, `.pytest_cache`,
`.import_linter_cache`), which R0 excludes. Their scoring rests on static evidence plus
CI wiring, and this is stated wherever it affects a level.

---

## 2. Plane matrix

| Plane | Level | Confidence | Anchor evidence |
|---|---|---|---|
| Intent | **2** executable | high | GitHub Issues carry structured specs; `gh issue view 129` shows What-to-build + 7 checkbox acceptance criteria + Blocked-by; 25 labels incl. `ready-for-agent`, `Sandcastle`, P0–P5 |
| Knowledge | **1** documented | high | `CONTEXT.md` (224 lines, 40+ terms with `_Avoid_`), `README.md`, 3 ADRs, 4 subsystem docs — but no AGENTS.md, and `CLAUDE.md` is 29 lines that never mention README or any command |
| Execution | **3** verifiable | medium-high | `Makefile` 50 targets; `verify`, `test-unit-ci`, `coverage`, `lint-imports`; `.venv` toolchain matches CI pins exactly (ruff 0.15.12, mypy 1.5.1, import-linter 2.11) |
| Feedback | **2** executable | medium | 133 test files, 3 tiers, contract/drift suite — but `app/core/observability.py` is a 14-line empty placeholder |
| Policy | **3** verifiable | high | 6 active import-linter contracts + ruff + mypy in CI and pre-commit — but no branch protection and no required checks |
| Isolation | **2** executable | medium | Worktrees in active use; `docker-compose.e2e.yml` namespaces ports (16379/18080) and mocks upstream — but Redis/BigQuery are shared, not task-local |
| Lifecycle | **1** documented | high | The loop demonstrably works (`.sandcastle/logs/`, stacked branches) but exists entirely outside the repo |
| Hygiene | **0** opaque | high | 6 dead doc pointers, 12 accumulated worktrees, 3 STAGED contracts carried since Phase 7; no ledger, no freshness check, no scan |
| Governance | **1** documented | medium | Application surface is genuinely enforced; agent-facing authority is absent from the repo entirely |

Scored independently and deliberately not averaged. Each level is the lowest fully
evidenced one for that plane; where a plane splits sharply across sub-capabilities
(Feedback, Governance) the split is named in the findings rather than hidden in the number.

---

## 3. Findings

### 3.1 Strongest capabilities

**Domain language is precise and enforced by contract tests.** `CONTEXT.md` defines ~45
terms each with an explicit `_Avoid_` list that names the *wrong* synonyms, including
near-misses that matter (`Strict Uptime` vs `Traffic Reliability`; `Provider+Route` vs
`Provider+Chain`; `Escalated Cadence` vs `Strike Escalation`). This is the single best
asset for an agent writing code that reads like the surrounding code.

**Architecture is mechanically enforced, not just described.** `pyproject.toml:82-179`
declares 6 active import-linter contracts — `scoring.math is pure` (forbids `redis`,
`google`, `aiohttp`, `fastapi`, `celery`), heartbeat domain isolation, infra-adapter
independence, API zone separation, admin-router back-edge lock. It runs in CI
(`.github/workflows/lint-and-format.yaml:33`), in `make lint-imports`, and in a pre-commit
hook whose `entry` explicitly prefers `.venv/bin` with a comment explaining why
(`.pre-commit-config.yaml:28-33`).

**The test tiering is deliberate and credential-honest.** `pytest.ini` declares 4 markers;
`UNIT_LANE_MARKERS` in `Makefile:58` deselects
`integration or requires_gcp or requires_redis or requires_firebase` so one lane runs with
zero secrets, and CI runs exactly that lane (`lint-and-format.yaml:86`). Coverage is
measured and explicitly never gated, with the decision written down in two places
(`pyproject.toml:193-201`, `lint-and-format.yaml:106`). `tests/contracts/` holds 8
drift-detection suites (gateway parity, BQ schema, SQL, rankings payload, shard keyspace
owner).

**ADR quality is high.** `docs/adr/0003-flapping-score-cadence-band-scoping.md` reproduces
the 30-day dataset, names the prior explanation it overturns, identifies the three
affected consumers, and states which one already produced a wrong answer. A maintainer can
dispute it on the numbers.

---

### 3.2 Top 3 blockers, ranked by impact on the tracer workflow

#### B1 — A cold agent cannot find the verification gate. One `.gitignore` line blocks the fix.

```yaml
id: "knowledge.agent-entrypoint"
plane: "knowledge"
level: 1
confidence: "high"
evidence:
  - "git grep 'make verify' -- . → 0 hits in tracked files"
  - "Makefile:91"
  - "CLAUDE.md (29 lines total)"
  - ".gitignore:170"
  - "git check-ignore -v AGENTS.md → .gitignore:170"
gap: "No tracked file names the agent verification gate or the toolchain rules, and AGENTS.md cannot be committed."
impact: "Every agent rediscovers the toolchain, or runs a global ruff/mypy and gets CI-divergent results."
next_capability: "Un-ignore AGENTS.md; write it naming `make verify`, the three test tiers, the .venv rule, and the branch/PR convention."
risk: "R1"
```

`git grep "make verify"` over all tracked files returns **zero hits**. The gate exists —
`Makefile:91` describes it as "Agent/CI verification gate: unit tests + Ruff + Mypy +
import-linter" — but nothing an agent reads points at it. `CLAUDE.md` is 29 lines covering
the issue tracker, labels, `docs/adr/`, and comment style; it never names `README.md`, the
`Makefile`, the test tiers, or the `.venv`-over-PATH rule that `Makefile:109-111` says
exists precisely because a stale global ruff reports different results than CI.

There is no `AGENTS.md` anywhere in the repo — and there cannot be one: `.gitignore:170`
ignores `AGENTS.md` with no negation, confirmed by `git check-ignore -v AGENTS.md`. Root
`CLAUDE.md` survives only via the `!/CLAUDE.md` negation at line 174. `.claude/` is also
ignored (line 168), so no shared skill, command, or settings file can be committed either.

#### B2 — Every mechanical guarantee is advisory at the merge boundary.

```yaml
id: "policy.no-merge-gate"
plane: "policy"
level: 3
confidence: "high"
evidence:
  - "gh api repos/:owner/:repo/branches/develop/protection → 404 Not Found"
  - "gh api repos/:owner/:repo/rulesets → []"
  - ".github/workflows/lint-and-format.yaml:3-5 (pull_request only)"
  - "pyproject.toml:57-65, 70-77, 155-159 (3 STAGED contracts)"
gap: "Checks run and can fail without blocking a merge; a direct merge to develop runs nothing."
impact: "The stacked-branch merge chain at HEAD inherits red without a stop; a real architecture violation can land."
next_capability: "Require the 5 existing check-runs on develop via a ruleset."
risk: "R2"
```

`gh api repos/:owner/:repo/branches/develop/protection` → **404 Not Found**.
`gh api repos/:owner/:repo/rulesets` → **`[]`**. The workflow triggers on `pull_request`
only (`lint-and-format.yaml:3-5`) — no `push`, no merge queue. So ruff, mypy,
import-linter, the unit lane, and the e2e tier all run and can all fail without blocking
anything, and a direct merge to `develop` runs no checks at all.

Secondary: 3 of the 9 declared architecture contracts are **STAGED** — commented out at
`pyproject.toml:57-65, 70-77, 155-159`. Contract 1a (`Entrypoints are independent`) is
documented as *currently violated* by two known edges (`app.api.ops.*` →
`app.admin.services.audit_log`, and `app.admin.deps` → `app.api.dependencies`), with the
fix deferred out of Phase 7 scope and no owner or date since.

#### B3 — Agents can prove logic but cannot observe the running system.

```yaml
id: "feedback.runtime-opacity"
plane: "feedback"
level: 1
confidence: "high"
evidence:
  - "app/core/observability.py:1-14 (explicit empty placeholder)"
  - "grep basicConfig app → 2 hits; grep structlog app → 0; grep getLogger → 60 modules"
  - "grep -rln 'playwright|selenium' tests app → 0 hits"
  - "Makefile:301-311 (grafana targets require GCP ADC + Grafana Cloud token)"
gap: "No structured logs, traces, metrics, agent-queryable log surface, or UI inspection outside the e2e stack."
impact: "Issue #129's criteria about logged warnings during a BigQuery outage can only be checked via caplog, never against a running heartbeat."
next_capability: "A read-only log-query make target scoped to the e2e compose stack."
risk: "R1"
```

`app/core/observability.py` is 14 lines of docstring stating it is a placeholder on the
audit's defer list and that "importing this module is a no-op." Concretely: no structured
logging (two `logging.basicConfig` calls, in `app/heartbeat/analytics/run_daily.py:413`
and `app/workers/heartbeat/__main__.py:882`, against 60 modules calling `getLogger`), no
`structlog`, no traces, no metrics exporter, no agent-queryable log surface. The htmx admin
UI at `/admin/*` has **no** browser-driven tests.

The Grafana dashboards-as-code (8 boards, `make grafana-verify`, `make rollup-verify`,
`tests/test_grafana_dashboards.py`) are real and well-built, but they read BigQuery and
need GCP ADC plus Grafana Cloud tokens — unavailable to a credential-free agent.

---

### 3.3 Further findings

#### Lifecycle — the working loop is invisible to the repo

```yaml
id: "lifecycle.unreconstructable"
plane: "lifecycle"
level: 1
confidence: "high"
evidence:
  - ".sandcastle/logs/ (52 files, paired implementer/reviewer logs for #112-#118)"
  - "git check-ignore -v package.json → .gitignore:195"
  - "ls .sandcastle/*.mts → no matches"
  - "find .github -type f → only workflows/lint-and-format.yaml"
gap: "The agent loop, its entrypoint, and the PR/recovery conventions are absent from the repository."
impact: "A second operator or a fresh clone cannot run or reason about the loop that produced HEAD."
next_capability: "Track the Sandcastle entrypoint (or document its operator-local status) and add a PR template requesting the evidence bundle."
risk: "R1"
```

The loop demonstrably runs: 52 files in `.sandcastle/logs/` including paired
`sandcastle-issue-NN-implementer.log` / `-reviewer.log` for #112–#118, and HEAD is a chain
of `sandcastle/issue-NN` merges. But none of it is reproducible from a clone:

- `package.json` — which defines `npm run sandcastle` → `npx tsx .sandcastle/main.mts` —
  is **gitignored** (`.gitignore:195`, confirmed by `git check-ignore`) and untracked.
- `.sandcastle/main.mts`, the entrypoint that script invokes, **does not exist** in this
  checkout (`ls .sandcastle/*.mts` → no matches; the dir holds only `.env`, `codex-home/`,
  `logs/`, `worktrees/`). `npm run sandcastle` would fail here today.
- `.github/` contains **only** `workflows/` — no `PULL_REQUEST_TEMPLATE`, no
  `ISSUE_TEMPLATE`, no `CODEOWNERS`.
- No recovery path is written down for the case the repo actually hits: a stacked branch
  inheriting red from its base.

#### Hygiene — drift is already misdirecting readers

```yaml
id: "hygiene.stale-pointers"
plane: "hygiene"
level: 0
confidence: "high"
gap: "Six doc pointers resolve to nothing; no ledger, freshness check, or cleanup pass exists."
impact: "An agent following README's heartbeat doc links reaches four missing files."
next_capability: "Fix the six pointers; add docs/harness/manifest.yaml and a learning ledger with a review date."
risk: "R1"
```

| Pointer | Source | Status |
|---|---|---|
| `ai/SPEC_heartbeat_analytics_usage.md` | `README.md:186` | missing |
| `ai/PLAN_M3_heartbeat.md` | `README.md:188` | missing |
| `ai/PLAN_M4_heartbeat_analytics.md` | `README.md:188` | missing |
| `ai/DECISIONS.md` | `CLAUDE.md:19`, `docs/adr/0003:7` | missing |
| `docs/agents/` | `.gitignore:18` negation | missing |

`ai/` holds exactly one file (`SPEC_heartbeat_testing.md`). Alongside: 12 accumulated
worktrees including 8 `agent-<hash>` detached heads; `.claude/optimization-report.md` and
`.claude/thermo-nuclear-code-quality-review/` as stray artifacts; `audit/` (39 files)
declared migration history but still the README's primary history pointer. There is no
learning ledger, no `docs/harness/`, no freshness date, and no cleanup pass. `make clean`
exists but scopes to `__pycache__`/`.mypy_cache`/`.pytest_cache` — build caches, not the
artifacts that rot.

#### Isolation — worktrees yes, task-local state no

```yaml
id: "isolation.shared-backing-services"
plane: "isolation"
level: 2
confidence: "medium"
evidence:
  - "tests/e2e/heartbeat/docker-compose.e2e.yml (namespaced ports, mock upstream, GCP creds pointed at /nonexistent)"
  - "README.md:138 (shared Memorystore 10.26.197.59, co-tenant with unified-request)"
gap: "Backing Redis and BigQuery are shared across tasks and repos; only the e2e stack is task-isolated."
impact: "Two agents exercising heartbeat control state concurrently collide."
next_capability: "Document a per-task Redis DB index or key-suffix convention for agent runs."
risk: "R1"
```

The e2e stack is properly isolated: env-overridable ports
(`HEARTBEAT_E2E_REDIS_PORT:-16379`, `HEARTBEAT_E2E_MOCK_PORT:-18080`), a built
`mock_uniblock` service, `GOOGLE_APPLICATION_CREDENTIALS: /nonexistent/path.json` to prove
no GCP reach, and BigQuery emitters flagged off. Outside it, `README.md:138` records that
Redis is **shared Memorystore at `10.26.197.59`, co-tenant with `unified-request`'s billing
and rate-limit**, namespaced only by an `auto_route:` prefix — not per task. No worktree
convention is tracked (`.worktrees/` untracked, `.claude/worktrees/` ignored).

#### Governance — strong on the application, absent for agents

```yaml
id: "governance.no-agent-authority"
plane: "governance"
level: 1
confidence: "medium"
evidence:
  - "Makefile:209-231 (unauth curl targets converted to pointer stubs)"
  - "README.md:70-73 (DEV/PROD reject default JWT secret and DEV_BYPASS_AUTH at startup)"
  - ".gitignore:168,177 (.claude/ and .claude/settings.local.json ignored)"
gap: "No risk classes, approval gates, escalation path, or committable permission policy for agents."
impact: "Agent authority is defined per-operator and cannot be reviewed or audited."
next_capability: "State risk classes and the human-gate boundary in AGENTS.md."
risk: "R1"
```

The application surface is genuinely well-governed and worth preserving: ops endpoints
require `AutoRoute.write` and are audit-logged on every call; `ENVIRONMENT=DEV/PROD`
rejects the default JWT secret and `DEV_BYPASS_AUTH` at startup; the old unauthenticated
`make run-cron`/`backfill`/`clear-cache` targets were converted to stubs that print a
pointer rather than curl a dead endpoint (`Makefile:209-231`). That is level-4 behavior on
that surface.

For agents there is nothing: no risk classes, no approval gates, no escalation path, and no
committable permission policy. Note also that `.env` and `gcp-credentials.json` sit in the
working tree — correctly gitignored, but any agent with repo-root read access reaches them.

---

## 4. Recommended adoption sequence

1. **Unblock and write the entrypoint** (R1). Remove `AGENTS.md` from `.gitignore`; add
   `AGENTS.md` naming `make verify`, the three test tiers, the `.venv`-over-PATH rule, and
   the branch/PR convention. Repoint `CLAUDE.md` at it. — *fixes B1*
2. **Gate the merge boundary** (R2). A ruleset on `develop` requiring the 5 existing
   check-runs. Nothing new to build; it makes what already runs count. — *fixes B2*
3. **Fix the six dead pointers and record the harness** (R1). Correct
   README/CLAUDE.md/ADR-0003, add `docs/harness/manifest.yaml` (facts only) and
   `docs/harness/learning-ledger.md`. Prune the 8 stale `agent-*` worktrees after
   confirming each is unneeded. — *moves Hygiene off 0*
4. **Make the lifecycle reproducible** (R1). Track the Sandcastle entrypoint (or document
   that the loop is operator-local and how to reconstruct it); add a PR template that asks
   for the evidence bundle; write the inherited-red recovery path.
5. **Open one runtime surface** (R1). A read-only log-query target against the e2e stack,
   so acceptance criteria phrased as "logs a warning" become checkable. — *starts on B3*
6. **Then** activate contract 1a with the two documented code moves, and decide 1b/6 with
   dates. — *closes B2's secondary*

Steps 1–3 are unstaged local edits plus one repo setting; none touch application code.

---

## 5. Safe first bootstrap boundary

**R1, no external state.** Permitted: creating `AGENTS.md`, `docs/harness/manifest.yaml`,
`docs/harness/learning-ledger.md`; editing `.gitignore`, `README.md`, `CLAUDE.md`,
`docs/adr/0003`; deleting stale worktrees after per-worktree confirmation. Everything
unstaged for review.

Outside the boundary without separate authorization: the `develop` ruleset (R2 — shared
repo settings), any push or PR (R2), any BigQuery/Redis/Grafana call (R3 — shared
services), and touching `.env` or `gcp-credentials.json` (R4).

---

## 6. Unknowns and how to resolve them

| Unknown | Why unresolved | Resolution |
|---|---|---|
| Does `make verify` pass on this checkout? | Writes 4 cache dirs — outside R0 | Run it once under R1 and record the result in the manifest |
| Does the Docker e2e tier run on this machine? | Requires starting services — outside R0 | Run `make test-e2e-heartbeat` under R1; if it stalls, read CI's `e2e-heartbeat` job as the authority |
| Is `.sandcastle/main.mts` recoverable? | Absent here; `package.json` is gitignored | Ask the maintainer whether it lives elsewhere or should be tracked |
| Real coverage percentage | `make coverage` executes the suite — outside R0 | Read the most recent CI `coverage` job summary |
| Are the 8 `agent-<hash>` worktrees abandoned? | Detached HEADs; abandonment isn't inferable from git | Confirm per worktree with the maintainer before pruning |
| Is contract 1a still violated? | `lint-imports` writes `.import_linter_cache` | Uncomment 1a in a scratch copy and run under R1 |

---

## 7. Cross-repository comparison

Not offered. No other repository has been assessed with equivalent evidence, and a
comparison drawn from recall rather than inspection would not be disputable.

---

## 8. Summary

`auto-route` has unusually strong *content* — a precise domain vocabulary, mechanically
enforced architecture contracts, honest test tiering, and ADRs that show their work. What
it lacks is the thin layer that makes that content reachable and binding: no agent
entrypoint (blocked by a single `.gitignore` line), no gate at the merge boundary (so every
check is advisory), and no runtime an agent can observe. The first two are hours of work
against a repo that has already done the hard part.

---

## 9. Delta on `henry/ai-workflow`

Verified by `git show`/`git ls-tree` against `henry/ai-workflow` @ `3ae2f8b` after the
assessment was written. **The harness is not missing — it exists on this branch and has not
propagated to the working branches.** That reframes the headline: the top blocker is
*propagation*, not *absence*.

### What exists here that the assessed branch lacks

| Artifact | On `henry/ai-workflow` | On assessed branch |
|---|---|---|
| `AGENTS.md` | tracked (via `.gitignore:176` `!/AGENTS.md`) | ignorable, absent |
| `ai/AGENTS.md` | tracked (via `.gitignore:177`), ~60 lines of orchestration + cross-cutting + style guidance | absent |
| `docs/agents/{domain,issue-tracker,triage-labels}.md` | tracked (via `.gitignore:18`) | absent |
| `ai/DECISIONS.md` | present | absent |
| `ai/LEARNINGS.md` | present — the learning-ledger convention `ai/AGENTS.md` mandates | absent |
| `ai/ARCHITECTURE.md`, `ai/PLAN.md` | present | absent |
| `ai/SPEC_heartbeat_analytics_usage.md` | present | absent |
| `.sandcastle/` | tracked: `main.mts`, `smoke.mts`, `plan-/implement-/review-/merge-prompt.md`, `CODING_STANDARDS.md`, `Dockerfile`, `.env.example` | untracked, `main.mts` absent |
| `docs/report/` | tracked (via `.gitignore:19`) | ignored |

### Findings that DO NOT hold on this branch

- **B1 (`knowledge.agent-entrypoint`) — largely resolved.** `AGENTS.md` is tracked and
  routes to `ai/AGENTS.md`, which names `Makefile`/`pyproject.toml` as the source of truth
  for build/test/lint and lists `make test`, `make lint-imports`, `make lint`. The
  `.gitignore` line that blocks `AGENTS.md` on the assessed branch is negated here at lines
  176–177.
- **`lifecycle.unreconstructable` — largely resolved.** `.sandcastle/main.mts` and the four
  agent prompts are tracked. `make verify` is documented in
  `.sandcastle/implement-prompt.md:43-60` and `.sandcastle/merge-prompt.md:41-51`,
  including the e2e-tier exclusion and the exit-137 tolerance — the two gotchas the
  assessed branch documents nowhere.
- **4 of 6 "dead pointers" — not dead.** `ai/DECISIONS.md`,
  `ai/SPEC_heartbeat_analytics_usage.md`, and `docs/agents/` all exist here. The
  README/`CLAUDE.md` references that dangle on the assessed branch are pointers to *this*
  branch's harness, not stale text. (`ai/PLAN_M3_heartbeat.md` and
  `ai/PLAN_M4_heartbeat_analytics.md` are still absent here — `ai/PLAN_heartbeat.md` and
  `ai/PLAN_M6_heartbeat_alerting_dashboards.md` exist instead, so those two README lines at
  `README.md:188` are genuinely stale on both branches.)

### Findings that still hold on this branch

- **B2 (`policy.no-merge-gate`)** — branch protection and rulesets are repository-level,
  not branch-level. `develop` has neither, and the workflow still triggers on
  `pull_request` only. Unchanged.
- **B3 (`feedback.runtime-opacity`)** — `app/core/observability.py` and the logging setup
  are the same here.
- **`isolation.shared-backing-services`** — shared Memorystore is a deployment fact.
- **`governance.no-agent-authority`** — partially softened: `ai/AGENTS.md` states secret-
  handling and generated-file rules, which is documented policy for agents. Still no risk
  classes, approval gates, or escalation path.
- **`hygiene.*`** — `docs/harness/` still does not exist on either branch, and the two
  stale `ai/PLAN_M*` README lines survive here.

### Revised top blocker

**Propagate the harness, or explain why it is branch-scoped.** `henry/ai-workflow` is not
an ancestor of the working branches, so every agent working on
`henry/heartbeat-control-durability` (and the `sandcastle/issue-NN` stack cut from it) runs
without `AGENTS.md`, without `ai/LEARNINGS.md`, and without the `make verify` gotchas. The
assessment in §1–§8 is an accurate picture of *what an agent on a working branch actually
sees* — which is the case for treating propagation, not authoring, as the gap.

A full assessment of `henry/ai-workflow` on its own terms has not been run; §1–§8 should
not be read as one. Re-run `/harness-assess` from this branch if that is wanted.

---

## Note on this file's location

`docs/generated/assessment/` is **gitignored** on both branches — `.gitignore:16` ignores
`/docs/*` with negations only for `adr/`, `agents/`, `report/`, and `superpowers/` (the
assessed branch lacks the `report/` negation). This file is therefore tracked via
`git add -f`: git honors tracked files inside ignored directories, so future edits show up
in `git status` normally, but a `!/docs/generated/` negation after `.gitignore:20` would be
the cleaner fix if more assessments land here. This matches
the stated intent of that rule ("Ignore generated/scratch docs, but keep the hand-written
trees tracked"), so the file is local-only and will not reach teammates or a fresh clone.
Two consequences worth knowing:

- To share or version this assessment, add a `!/docs/generated/` negation after
  `.gitignore:19`, or move the file under a tracked tree.
- The harness inventory script excludes any directory named `generated`, so a future
  `/harness-assess` run will not see this file as prior evidence.