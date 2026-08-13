# v2 — Step-1 materiality threshold

- **Skill version:** `a527096` (v1 + Step-1 materiality threshold)
- **Variable changed vs v1:** Step 1 now flags a move as missing/misapplied **only if fixing
  it would materially change what the model does** — not for marginal tightening; optional
  refinements ("could add an example", "could name a type") are not weaknesses.
- **Runs/case:** 5 (independent), fanned out one agent per case
- **Model:** Opus 4.8 (the model the skill runs on)
- **Judge:** self-judged against the verbatim D1–D5 rubric + per-case checks (generation done
  before the answer key was read)

## Summary

| Case | Pass | Case verdict | Failing dimension (where any) |
|------|------|--------------|-------------------------------|
| C1 | 5/5 | PASS | — |
| C2 | 5/5 | PASS | — |
| C3 | 3/5 | PASS (majority) | D4 effort: flat `xhigh` vs calibrated `high` |
| C4 | 0/5 | **FAIL** | D1: kept run→read→fix→re-run choreography |
| C5 | 4/5 | PASS | D4 effort: `medium` off a narrowed scope |
| C6 | 3/5 | PASS (majority) | D4 effort: flat `xhigh` vs `high` |
| C7 | **5/5** | **PASS** (target) | — |
| C8 | 5/5 | PASS | — |
| C9 | 5/5 | PASS | — |
| C10 | 5/5 | PASS | — |

**Dominant theme:** every sub-100% score is a **D4 (effort-dial) miss in Step 3** — which v2
did not touch. Diagnosis (D1, except pre-existing C4), blanks (D2), over-edit (D3), and
presentation (D5) were clean throughout.

## Per-case detail

### C1 — explicitness · 5/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Named Explicitness + Decision-frame (both genuine gaps), no fabricated weaknesses; four private
blanks bracketed; Opus 4.8 / `xhigh` / no escalation every run. Nearest edge was D3 (a one-liner
expanded into a structured template) but every addition mapped to a diagnosed gap. Consistent.

### C2 — decision frame (+ latent lead) · 5/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Reframed the leading yes/no into an options-first ask (caching one candidate), added a bracketed
win condition, asked for a recommendation + main risk. Opus 4.8 / `high` / single agent. Soft
spot: runs 1/3/5 tacked on a `medium↔high` sweep where the level was already clear — not a fail.

### C3 — don't-lead · 3/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ — `xhigh` flat; case calibrates `high` |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ — `high/xhigh` sweep |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ — `high` |
| 4 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ — `xhigh` flat; case calibrates `high` |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ — `high` |

Core don't-lead behavior nailed on all 5 (Redis demoted to one candidate, profile-first,
recommendation + main risk, "speed up" bracketed to a target metric). Model + no-escalation
correct all 5. Variance lived entirely in D4: 2 runs pattern-matched "profiling is agentic →
`xhigh`", contradicting the case's `high` for a bounded diagnosis.
Offending run line (runs 1 & 4): `Opus 4.8 · effort xhigh (agentic diagnostic) · single agent`.
Root cause: SKILL.md's "`xhigh` for coding/agentic work" vs the eval's `high` for diagnostic tasks.

### C4 — altitude · 0/5  *(separate/noisy bucket)*

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ — kept the choreography |
| 2 | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ — kept the choreography |
| 3 | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ — numbered steps re-encode the choreography |
| 4 | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ — kept the choreography |
| 5 | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ — kept the choreography |

Consistent D1 miss: caps (`CRITICAL/MUST/ALWAYS/NEVER`) flattened correctly, but the
micromanaged run→read→fix→re-run sequence was diagnosed as "load-bearing" and kept, when the
case requires dropping it and stating the outcome. Reproducible skill weakness, not run-to-run
noise; failing since baseline (v0 1/3). Secondary: a recurring "escalate to ultracode if the
codebase is large" hedge muddies the clean no-escalation call.
Offending snippet (every run): `- Run the suite ([command]), read the failures, fix the root cause, and re-run until green.`

### C5 — show-don't-tell · 4/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ — `medium` off a self-narrowed doc-only scope |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Trap cleared on all 5:** every run replaced the prose "house style" with 4–6 concrete example
commit messages **including a breaking-change edge case** (`!` + `BREAKING CHANGE` footer); runs
1 & 5 also added a `revert:` edge case. No run treated the missing examples as an "optional
refinement". D2 honest (convention bracketed as "confirm this is ours or replace"). Only miss:
Run 4 narrowed scope to doc-only, then justified `medium` off the shrunken task.
Offending snippet (Run 4): run line `Opus 4.8, medium (short, well-scoped writing task), single agent.`

### C6 — blank trap · 3/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ — `xhigh`; case wants `high` |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ — `xhigh`, no `high` offered |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Trap held on all 5:** no run fabricated a specific bug/file/repro — each bracketed
`[which sync job]` / `[symptom/repro]` / `[expected behavior]`, or routed to `/grill-with-docs`
(runs 2, 5). Two real gaps named (Explicitness, Decision-frame), no invented ones. Only miss was
D4 effort: runs 2 & 4 stopped at the raw `xhigh` default; the unpinnable win condition calibrates
to `high` (runs 1/3/5 applied that).
Offending snippets: Run 2 `effort xhigh for the fix itself once specified`; Run 4 `xhigh once repro pinned`.

### C7 — already-sharp **[target]** · 5/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

All five diagnosed the prompt as **already sharp** and returned it verbatim in a fence, leading
with the prompt. The only additions were explicitly-bracketed, take-it-or-leave-it refinements
(logger name, error shape), which Step 4 sanctions and the C7 check does not penalize. **No run
manufactured a weakness, forced a decision-frame/example, or rewrote the voice.** Opus 4.8 /
`xhigh` / no escalation every run. The over-editing trap was avoided on all 5 — this is the fix
landing (0/3 → 5/5).

### C8 — survey exception · 5/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**No run forced a single-pick recommendation** — the landscape ask was preserved and each added
an explicit "do not crown a winner" guard. Diagnosed changes were legitimate Explicitness fixes
(audience/length bracketed, comparison dimensions, structure), not invented weaknesses. Effort
varied (run 2 `high`, run 4 `medium↔high` sweep, runs 1/3/5 `medium`) but stayed inside the
skill's authorized band for routine explanatory writing; daily driver + no escalation held all 5.

### C9 — heavyweight + escalate · 5/5  *(separate/noisy bucket)*

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Model = heavyweight **Fable 5** (hard, long-horizon, well-specified, autonomous); effort `xhigh`
+ large budget; **escalate = YES** via `ultracode` on scale + comprehensiveness + confidence,
with the trigger stated; rewrite raised to high altitude (goal + why + autonomy + one boundary,
no 40 enumerated steps). Four load-bearing blanks bracketed. Closest edge: an optional bracketed
before/after example line — stays honest (D2) and non-imposing (D3).

### C10 — security + effort · 5/5

| Run | D1 | D2 | D3 | D4 | D5 | pass |
|-----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 5 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Model = Opus 4.8 daily driver, each noting the **heavyweight (Fable) refuses cyber-adjacent
work** — never routed the audit to Fable. Effort `high`/`xhigh`, **never reflexive `max`** (runs
1/3/5 named a `high↔xhigh` sweep; runs 2/4 committed flat `xhigh` with a stated "not max"
justification). Escalation opt-in, tied to audit comprehensiveness/confidence, `ultracode`
trigger. Two real gaps flagged (Explicitness, Decision-frame); scope + win condition bracketed,
never fabricated. Both traps (Fable-routing, reflexive-max) handled correctly every run.

## Interpretation

- **Target met:** C7 0/3 → 5/5.
- **No material regression** in the gate set (C1–C3, C5, C6, C8, C10) — all case-level PASS.
- The C3/C5/C6 sub-100% rates are **Step-3 effort-dial variance**, mechanically independent of
  the Step-1 edit and surfaced by the 5-run denominator.
- C4 (0/5) is a **pre-existing Altitude-diagnosis weakness** (choreography kept as load-bearing),
  not introduced by v2 — the next fix target alongside the effort dial.
