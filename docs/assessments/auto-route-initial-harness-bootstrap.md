I have the assessment, the delta, and the current-branch evidence. Before mutating anything, here is the preview — plus three decisions that are genuinely yours.

## Gate check

| | |
|---|---|
| Target | `henry/ai-workflow` @ `7d03534`, working tree **clean** |
| Assessment | `docs/generated/assessment/2026-08-11-harness-assessment.md`, assessed ref `2ae706c` ≠ target — **delta already run** (§9), re-verified on this branch below |
| Risk boundary | R1: unstaged local edits only. No `git add`, commit, push, or PR |
| Re-verified here | 6 import-linter contracts active (`pyproject.toml:80-162`) — same as assessed; Makefile targets `setup/run/verify/test/lint/lint-imports/test-unit-ci` all present; Makefile differs from assessed branch by one `.PHONY` line only |

## Preview — 7 files, 3 groups

**Add (5)**
| Path | Purpose | One authoritative source? |
|---|---|---|
| `docs/harness/manifest.yaml` | Evidenced capability facts | new — no existing manifest |
| `docs/harness/learning-ledger.md` | Harness-friction ledger (see Q1) | overlaps `ai/LEARNINGS.md` — **decision needed** |
| `docs/harness/tracer-ready-for-agent-issue.md` | Tracer workflow w/ acceptance + evidence | new; points at `.sandcastle/implement-prompt.md`, doesn't restate it |
| `scripts/harness_validate.py` | Repo-owned validator, dependency-free | new; matches the 13-file `scripts/*.py` convention |
| — | | |

**Edit (3)**
| Path | Change | Why |
|---|---|---|
| `Makefile` | `+harness-validate` target + `.PHONY` entry | validator requires `commands.validate` to resolve to a real target |
| `.gitignore` | `+!/docs/harness/` after line 20 | **`/docs/*` is ignored** — without this the whole harness tree is invisible, same trap as `docs/generated/` |
| `AGENTS.md` | add a Commands block (see Q2) | validator requires every manifest command verbatim in the guidance entrypoint |
| `CLAUDE.md` | reconcile (see Q3) | validator errors today: `CLAUDE.md` never mentions `AGENTS.md` |

**Leave unchanged:** `ai/AGENTS.md`, `ai/ARCHITECTURE.md`, `ai/LEARNINGS.md`, `ai/PLAN.md`, `docs/agents/*`, `.sandcastle/*`, `README.md`, `CONTEXT.md`, `docs/adr/*`, `pyproject.toml`, CI. No template overwrites an existing guidance file.

**Commands to advertise — each verified on this branch**

| Manifest key | Command | Evidence |
|---|---|---|
| `setup` | `make setup` | `Makefile:24` |
| `start` | `make run` | `Makefile:142` |
| `check` | `make verify` | `Makefile:91` — the gate `.sandcastle/implement-prompt.md:46` already names |
| `test` | `make test` | `Makefile:60` |
| `validate` | `make harness-validate` | **new target — this is the one thing I add, not describe** |

**Architecture entrypoint:** `ai/ARCHITECTURE.md`. It self-declares as the durable invariants doc; `README.md` is setup+layout and `audit/03_target_architecture.md` is migration-era. Say so if you disagree — I won't ask, I'll just note the choice.

**Validator:** `make harness-validate` → expects `docs/harness/manifest.yaml`, `docs/harness/learning-ledger.md`, and every `entrypoints.*`/`evidence` path to resolve.

**Excluded from bootstrap** (out of R1 or out of scope): the `develop` ruleset (R2 — repo settings, blocker B2); runtime observability (B3 — needs real code); import-linter contract 1a activation (code moves); the two stale `ai/PLAN_M*` README lines (unrelated); merging this harness into the working branches (R2).

**Change groups, all left unstaged**

| Group | Files | Suggested message | Verify with |
|---|---|---|---|
| G1 | `docs/harness/manifest.yaml`, `learning-ledger.md`, `scripts/harness_validate.py`, `Makefile`, `.gitignore` | `chore(harness): add manifest, learning ledger, and validator` | `make harness-validate` |
| G2 | `AGENTS.md`, `CLAUDE.md` | `docs(agents): advertise commands in AGENTS.md, route CLAUDE.md to it` | `make harness-validate` |
| G3 | `docs/harness/tracer-ready-for-agent-issue.md` | `docs(harness): record the ready-for-agent tracer workflow` | `make harness-validate` |

Three things I won't decide for you — each changes what gets written:

All three recommended options. Preparing the changes now.

All evidence paths resolve. Writing the change set.

Now the Makefile target and the two guidance files.

Now the guidance reconciliation.

Now verification.

Bootstrap prepared. Everything is **unstaged** — no `git add`, no commit, no push.

## Validator

```
PASS: harness contract is internally consistent (0 warning(s)).
```

## What changed — 4 edits, 4 new files

```
 M .gitignore    1 +      !/docs/harness/ — without it the whole tree is invisible
 M AGENTS.md    75 +-     Commands block, where-things-are map, completion expectations
 M CLAUDE.md    30 +-     reduced to pointer + Code comments (its only non-duplicated section)
 M Makefile      8 +-     harness-validate target, .PHONY, help group
?? docs/harness/manifest.yaml
?? docs/harness/learning-ledger.md
?? docs/harness/tracer-ready-for-agent-issue.md
?? scripts/harness_validate.py
```

Nothing else moved. `ai/AGENTS.md`, `ai/ARCHITECTURE.md`, `ai/LEARNINGS.md`, `docs/agents/*`, `.sandcastle/*`, `README.md`, `CONTEXT.md`, CI and `pyproject.toml` are untouched — no template overwrote an existing guidance file.

## Commands run

| Command | Result |
|---|---|
| `make harness-validate` | **PASS**, 0 warnings |
| `.venv/bin/ruff check scripts/harness_validate.py` | All checks passed |
| `.venv/bin/ruff format --check scripts/harness_validate.py` | already formatted |
| `.venv/bin/pytest tests/contracts/test_coverage_config.py -q` | **6 passed** — the only test coupled to `Makefile` |
| `make help` | new target renders under Code Quality |
| `git check-ignore docs/harness/manifest.yaml` | not ignored — negation works |

Placeholder/secret/personal-path scan over the new files: clean.

## Change groups — commit each narrowly

**G1 — harness contract** `docs/harness/manifest.yaml` `docs/harness/learning-ledger.md` `scripts/harness_validate.py` `Makefile` `.gitignore`
`chore(harness): add manifest, learning ledger, and validator` → verify `make harness-validate`

**G2 — guidance** `AGENTS.md` `CLAUDE.md`
`docs(agents): advertise commands in AGENTS.md, route CLAUDE.md to it` → verify `make harness-validate`

**G3 — tracer** `docs/harness/tracer-ready-for-agent-issue.md`
`docs(harness): record the ready-for-agent tracer workflow` → verify `make harness-validate`

G1 must land before or with G3 — the manifest's `entrypoints.tracer` points at G3's file, so G1 alone fails validation. G2 is independent.

**Rollback:** G1 `git checkout Makefile .gitignore && rm -rf docs/harness scripts/harness_validate.py` · G2 `git checkout AGENTS.md CLAUDE.md` · G3 `rm docs/harness/tracer-ready-for-agent-issue.md`

**Review:** `git diff` · `git diff --stat` · `cat docs/harness/manifest.yaml`

## Honest notes

**Skipped:** `make verify` — several minutes, and nothing under `app/` or `tests/` changed. The two checks that could plausibly break from this diff (repo-wide `ruff` over the new script; the Makefile-reading contract test) I ran individually and both pass. Run `make verify` before committing if you want the full gate.

**The manifest records two capabilities as `missing`, with evidence** — `runtime_observability` (`app/core/observability.py`) and `merge_gate` (`lint-and-format.yaml:3`). That's deliberate: the contract says record facts, not aspirations, and an honest `missing` is what makes the `verified`/`automated` entries worth believing.

**Q3 follow-through:** you chose "reduce to a pointer," so Code comments stayed in `CLAUDE.md` rather than moving to `AGENTS.md`. I briefly wrote it into both and removed the duplicate.

**Next weakest plane: Policy.** Blocker B2 is untouched and unreachable from here — requiring the 5 existing check-runs on `develop` is a repo-settings change (R2) that needs your authority. Every gate this bootstrap advertises still cannot stop a bad merge. After that, Feedback (B3) — a read-only log-query target against the e2e stack.

**Still branch-scoped.** This harness lives on `henry/ai-workflow`, which is not an ancestor of the working branches. Agents on `henry/heartbeat-control-durability` and the `sandcastle/issue-NN` stack still see none of it. Propagation is R2 and remains your call.