# Harness assessment — `unified-request`

> Read-only (R0) harness-engineering baseline produced by `/harness-assess` on
> 2026-08-11. Scored against
> [`~/.claude/skills/harness/references/contracts.md`](https://github.com/Uniblock-dev/unified-request).
> Every factual claim below cites a path, a command result, or an explicit `unknown`.
> This document is a dated snapshot, not a living file — re-run the assessment rather
> than editing it in place.

## 1. Scope and state

| | |
|---|---|
| Repository | `/Users/hoomji/Documents/VS/Github/unified-request` |
| Branch assessed | `henry-sandcastle` @ `b44764ea5` (1393 commits ahead of `origin/develop`) |
| Dirty state | one untracked dir, `.seed-henry-sandcastle/` — untouched |
| Tracer workflow | "add a provider surface and prove it" — `.claude/skills/add-provider-to-unified-endpoint` → `yarn ci:local` → PR queue |
| Risk class | R0 throughout. No installs, no writes to the repo, no external mutations |
| Excluded | `node_modules`, `dist`, `generated`, `coverage`, `.yarn`, 21 sibling worktrees, `.env*` |

Commands executed during the assessment, all read-only in effect:

```
git rev-parse / branch / status / worktree list / cat-file -e / ls-tree / log
python3 scripts/inventory.py <repo-root>
yarn ci:local --list
yarn cassette:status
gh issue list --state open --limit 5 --json …
gh label list --limit 100
node node_modules/jest/bin/jest.js --config ./test/jest-unit.js \
  test/unit/ci/suite-boundary.spec.ts \
  test/unit/ci/typecheck-and-format-gates.spec.ts \
  test/unit/docs/pr-queue.spec.ts --runInBand
```

**Scope decision worth stating up front:** the checked-out branch was scored, not
`develop`. That turned out to be the most important finding on its own — see §3.1.

## 2. Plane matrix

| Plane | Level | Confidence | One-line basis |
|---|---|---|---|
| Intent | **3** verifiable | medium | Issues + ADRs + gated PR-queue graph; no AC→change link |
| Knowledge | **3** verifiable | medium | Excellent `CONTEXT.md` + 31 ADRs, drift-gated generated docs; one dead pointer |
| Execution | **4** enforced | high | `yarn ci:local` mirrors 13 CI gates, self-guarded, reports SKIPPED honestly |
| Feedback | **3** verifiable | high | 701 specs / 6 tiers / cassette replay; runtime signal exists but gates nothing |
| Policy | **4** enforced | high | 24 `test/unit/ci/*` guardrails + drift gates; remediation strings missing |
| Isolation | **2** executable | medium | Worktrees + Docker + jest ignore-paths; fixed ports, no per-task namespacing |
| Lifecycle | **4** enforced | high | `sandcastle:sync`/`harvest` exit non-zero as checks; PR-queue graph gated |
| Hygiene | **3** verifiable | high | `cassette:status` is a genuine drift detector — and it is firing right now |
| Governance | **2** executable | medium | Per-artifact prose gates, no shared risk vocabulary or manifest |

Deliberately not averaged. Execution, Policy and Lifecycle are unusually strong;
Isolation and Governance are the floor.

Level scale: `0 opaque` · `1 documented` · `2 executable` · `3 verifiable` ·
`4 enforced` · `5 adaptive`.

## 3. Findings

### 3.1 The harness is on the branch, not on `develop` — top blocker

```
                              develop   henry-sandcastle
scripts/ci-local.js              ✗            ✓
scripts/cassette-status.js       ✗            ✓
docs/pr-queue/README.md          ✗            ✓
docs/sandcastle-branch-sync.md   ✗            ✓
.husky/pre-push                  ✗            ✓
docs-index-drift.yml             ✗            ✓
provider-verify.yml              ✗            ✓
CLAUDE.md                        ✗            ✓
test/unit/ci/*.spec.ts           7           24
```

Verified with `git cat-file -e origin/develop:<path>` per file and
`git ls-tree -r --name-only origin/develop test/unit/ci | wc -l`.

`CONTEXT.md`, `docs/agents/*`, `test/e2e/README.md`, `.sandcastle/CODING_STANDARDS.md`
and ADR-0001 *are* on `develop`. But an agent cloning `develop` gets **no
`yarn ci:local`, no pre-push hook, no cassette health tool, no PR-queue gate, and 7 of
24 guardrails**. Every plane score in §2 is 1–2 levels lower from that starting point.

This is the highest-leverage item in the report. It also means §2 describes a harness
most consumers of the repo cannot currently reach.

### 3.2 The hygiene loop detects drift but nothing runs it

`yarn cassette:status` output, verbatim from this run:

```
refill loop: STALLED — the last completed refill ledger rebuild was 4d ago
(2026-08-07T06:16:18.505Z), over the 2d liveness threshold — the refill loop
is not running [62/66 spec files]
all-providers health: 2299 missing row(s) · 288 shape change(s) ·
76 rate-limited · 1124 chronic-failure combo(s) · 61 other failing
1 stale
```

The detector is excellent — it separates *staleness*, *drift*, *chronic failure* and
*loop liveness* as four distinct concepts, each defined precisely in
[`CONTEXT.md:215-241`](../../../CONTEXT.md). The `--check` gate is wired into
[`.github/workflows/cassette-refill.yml`](../../../.github/workflows/cassette-refill.yml),
whose header comment claims it "replaces the local Claude Code task."

It does not. `git cat-file -e origin/develop:.github/workflows/cassette-refill.yml`
→ **absent**. GitHub Actions `schedule:` only fires from the default branch, so this
workflow has never run and cannot run. The loop has been dead for 4 days with the
detector correctly shouting into an empty room.

### 3.3 Dead pointer in the reviewer agent's declared source of truth

[`.sandcastle/CODING_STANDARDS.md:3-5`](../../../.sandcastle/CODING_STANDARDS.md):

> "Source of truth for the full picture is `ai/AGENTS.md`, `ai/LEARNINGS.MD`, and
> `ai/ARCHITECTURE.MD`."

`find ai -maxdepth 3` returns only `ai/shred/__pycache__/`. And
`git check-ignore -v ai/AGENTS.md` → `.gitignore:509:ai/`. Those three files do not
exist in any clone and cannot be committed. The reviewer agent loads this file on every
Sandcastle review and is pointed at nothing.

Cheapest high-value fix in the report.

### 3.4 Guardrails fail mechanically, but without remediation

Three were executed and pass fast and for real:

```
PASS unit test/unit/docs/pr-queue.spec.ts
PASS unit test/unit/ci/typecheck-and-format-gates.spec.ts
PASS unit test/unit/ci/suite-boundary.spec.ts
Tests: 138 passed   Time: 2.373 s
```

The 24 specs in [`test/unit/ci/`](../../../test/unit/ci) cover suite boundaries,
workflow-vs-manifest agreement, focused/skipped detection, jest config governance, and
sandcastle harvest/sync — a genuinely strong policy plane.

But the assertions are bare: `test/unit/ci/suite-boundary.spec.ts:44` is
`expect(stray).toEqual([])`. `grep -rn "Run \`yarn" test/unit/ci/*.spec.ts` returns
nothing. The contract requires enforcement to fail *with remediation*; a failing agent
sees the offending path and must infer the fix.

`scripts/ci-local.js` does better — it names the gate and the workflow it mirrors —
which is why Execution scores 4 and this is a gap inside Policy rather than a demotion.

### 3.5 Isolation has no runtime namespacing

Strong parts: 21 live worktrees under `.claude/worktrees/` and `.sandcastle/worktrees/`,
Docker-backed Sandcastle, and the jest tier configs explicitly `modulePathIgnorePatterns`
both agent trees so worktree copies cannot poison the unit tier
(`test/jest-component.js:19`). `E2E_ENV` defaults to `local` "so a forgotten variable
never bills CU against production" — a real, deliberate isolation invariant.

Weak parts: the local stack is fixed at ports 3007/3009/3010
([`test/e2e/README.md:23-29`](../../../test/e2e/README.md)), so two agents cannot run it
concurrently — the tracer workflow serializes on one machine. `git worktree list` shows
3 `prunable` entries, i.e. no cleanup discipline. No task-local telemetry: a failing
agent run leaves no scoped log to read back.

### 3.6 Runtime feedback exists but gates nothing

Synthetic probes → BigQuery → Grafana, with `probe:dashboard:verify` as a reproducible
check; k6 load tests; Jaeger tracing behind `TRACE_DISABLED=false`; an
`X-Unified-Provider-Latency` header. All real, all documented in
[`CONTEXT.md:151-211`](../../../CONTEXT.md).

None of it is reachable from a repo command an agent can run without credentials, and no
probe outcome fails any build. `logs/` holds 117 chain logs dated 2025-10/11, untracked
and un-gitignored — output nobody collects.

Whether `.github/workflows/e2e-test.yml` currently runs is **unknown**: it needs
`E2E_API_KEY` / `E2E_API_GATEWAY_URL` repository secrets, which R0 cannot inspect.

### 3.7 Governance has no shared vocabulary

Good instincts appear per-artifact:
[`smoke-test.yml`](../../../.github/workflows/smoke-test.yml) names an owner for all 16
secrets; a plan file carries an explicit human gate — *"Do not run the `*:record`
scripts … without the user confirming it's fine to hit live staging right now"*
(`docs/superpowers/plans/2026-07-04-cassette-coverage-gaps.md:16`); live workflows are
deliberately kept outside the PR gate with the reasoning written down.

Missing: any risk-class vocabulary, `docs/harness/manifest.yaml`, or
`docs/harness/learning-ledger.md` (all three searched, all absent). The only permission
surface is `.claude/settings.local.json` with two allow entries — a local file, not
shared policy. Nothing tells an agent which operations are shared-reversible versus
consequential.

## 4. Recommended adoption sequence

| # | Action | Plane | Risk | Why here |
|---|---|---|---|---|
| 1 | Fix or delete the `ai/AGENTS.md` pointer in `CODING_STANDARDS.md` | Knowledge | R1 | Two-line edit; unblocks every review run |
| 2 | Carve `ci-local.js` + `cassette-status.js` + the 17 extra guardrails onto `develop` | all | R2 | Raises the floor for every clone; the carve-out machinery already exists |
| 3 | Land `cassette-refill.yml` on `develop` so its `schedule:` can fire | Hygiene | R2 | The detector is built and correct; only the runner is missing |
| 4 | Add remediation strings to the 24 `test/unit/ci` guardrails | Policy | R1 | Converts "you broke a rule" into "run this" |
| 5 | Namespace the local-stack ports via env with documented defaults | Isolation | R1 | Unblocks concurrent agents on the tracer workflow |
| 6 | Write `docs/harness/manifest.yaml` recording what actually exists | Governance | R1 | Do this *after* 2–3 so it records facts, not aspirations |
| 7 | Open `docs/harness/learning-ledger.md` | Hygiene | R1 | This repo generates recurring friction worth compounding |

## 5. Safe first bootstrap boundary

Items 1, 4, 5, 6, 7 are **R1** — workspace edits verified by existing commands, no
shared state.

Items 2 and 3 are **R2**: branch push and PR against `develop`. Both should route
through the documented carve-out process
([`docs/sandcastle-carve-out-harvest.md`](../../sandcastle-carve-out-harvest.md)) rather
than a fresh branch, because a PR harvested *from* the branch is the older copy and
`sandcastle-branch-sync`'s "PR wins" direction rule inverts for it.

Nothing in this sequence needs R3 or above.

## 6. Unknowns

| Unknown | How to resolve |
|---|---|
| Whether `e2e-test.yml` / `provider-verify.yml` actually execute | `gh run list --workflow=e2e-test.yml` — needs Actions read |
| Whether required repo secrets are populated | Repo settings; outside R0 |
| Whether the pre-push hook currently passes | Would require running the full unit tier (minutes, and it mutates the prettier cache) |
| Whether the 1124 chronic-failure combos are provider outages or contract breaks | `yarn cassette:status --combos` — read-only, worth running next |
| Whether `develop` carries the ADR/CONTEXT freshness an agent would need | Partially resolved: `CONTEXT.md` and `docs/adr/0001` confirmed present on `develop` |

## 7. Comparison

No second assessed repository with equivalent evidence, so no comparison is offered.

---

**Bottom line:** the strongest capabilities here are the command aggregator, the
guardrail suite, the PR-queue and branch-sync lifecycle machinery, and the cassette
health model — the last of which is better than most repositories have. The three
blockers are that most of it is stranded on one branch, that the hygiene loop it built
has no runner, and that governance and isolation never got a shared vocabulary.
