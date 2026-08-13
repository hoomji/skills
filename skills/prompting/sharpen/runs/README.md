# Sharpen — eval run log

Every run of the [`EVALS.md`](../EVALS.md) suite, kept so the loop can compare across
versions (the Lesson-8 discipline: change one variable, run the suite, keep or revert).
One file per run. Newest last.

## Runs

| Run | Skill version / variable changed | Commit | Runs/case | File |
|-----|----------------------------------|--------|-----------|------|
| v0  | baseline — no already-sharp handling | `d7c2d70` | 3 | [v0-baseline.md](v0-baseline.md) |
| v1  | + already-sharp handling (Steps 1 & 4) | *(uncommitted intermediate, folded into `a527096`)* | 3 | [v1-already-sharp.md](v1-already-sharp.md) |
| v2  | + Step-1 materiality threshold | `a527096` | 5 | [v2-materiality-threshold.md](v2-materiality-threshold.md) |
| v3  | + Step-5 adjacent branching, Step-6 always-print / D5 tightened, +C11/C12 / D6 | `54f362e` | 3 | [v3-branching-always-print.md](v3-branching-always-print.md) |
| v4  | + four root-cause fixes (bracket-and-deliver, over-edit guard, heavyweight trigger, effort dial) | *(uncommitted on `4b3c378`)* | 3 | [v4-four-root-cause-fixes.md](v4-four-root-cause-fixes.md) |

## Pass-count matrix (all runs)

Pass count = runs where **all** rubric dimensions + the case checks held (D1–D5 for v0–v2;
**D1–D6** from v3, when D6 branch-quality was added). Denominators differ (v0/v1 = 3, v2 = 5,
v3 = 3). Case-level PASS = majority of runs. C11/C12 did not exist before v3.

| Case | Target | v0 | v1 | v2 | v3 | v4 |
|------|--------|----|----|----|----|----|
| C1 | explicitness | 3/3 | pass | 5/5 | 0/3 | **3/3** |
| C2 | decision frame | 3/3 | pass | 5/5 | 0/3 | **3/3** |
| C3 | don't-lead | 3/3 | pass | 3/5 | 2/3 | 3/3 |
| C4 | altitude | 1/3 | 2/3 | 0/5 | 3/3 | **1/3** |
| C5 | show-don't-tell | 2/3 | 3/3 | 4/5 | 0/3 | 0/3 |
| C6 | blank trap | 3/3 | pass | 3/5 | 1/3 | **3/3** |
| C7 | already-sharp | 0/3 | 0/3 | 5/5 | 0/3 | **3/3** |
| C8 | survey exception | 3/3 | pass | 5/5 | 3/3 | 3/3 |
| C9 | heavyweight + escalate | 1/3 | 3/3 | 5/5 | 0/3 | **3/3** |
| C10 | security + effort | 3/3 | pass | 5/5 | 3/3 | 3/3 |
| C11 | branch: clear intent | — | — | — | 0/3 | 1/3 |
| C12 | branch: wide-open | — | — | — | 0/3 | **3/3** |

**v4 (four root-cause fixes): 4/12 → 9/12.** Targets hit: C6, C7, C9 flipped to pass; interview-path
cases (C1/C2/C12) hold. Residual: C5 (fifth issue — show-don't-tell not executed), C11 (effort +
divergence stragglers), and **C4 regressed 3/3→1/3** — Fix 4's `high`-for-"writing" bucket
mis-catches "write tests"; disambiguate to recover.

## Reading the loop

- **v2 fixed C7** (0/3 → 5/5) via the Step-1 materiality threshold; v1's already-sharp
  scaffolding alone never moved it.
- **No gate case regressed to fail under v2.** The C3/C6 3/5 and C5 4/5 were all **D4
  (effort-dial) misses in Step 3**, surfaced by the larger 5-run denominator, not caused by
  the fix.
- **v3 bundled three changes** (branching Step 5, always-print/D5-tightened, +C11/C12/D6) and
  **SET FAILed (4/12)**. Two gains — **C4 recovered 0/5 → 3/3** (altitude choreography finally
  dropped) and the new branching (D6) works wherever a deliverable was produced. Two regressions
  — **C7 5/5 → 0/3** (over-edit trap) and **C9 5/5 → 0/3** (model selection).
- **v3's dominant failure is structural:** the new D5 requires a fenced prompt *in every case*,
  but Step 2 still halts to interview on a blank — so C1/C2/C5/C6/C12 fail the moment the model
  asks a question. Resolved by decision to **bracket-and-deliver-then-ask** (make it a skill
  fix, keep D5).
- **Next target (priority):** (1) bracket-and-deliver in Steps 2+6, (2) re-anchor the C7
  already-sharp guard, (3) fix C9 model selection, (4) the effort dial — now shown *unanchored
  in both directions* (`xhigh` too high on diagnostics C3/C6; `low`/`medium` too low on bounded
  coding C11). One variable at a time; re-run between each.

## Provenance

- **v3** carries full per-case, per-run D1–D6 detail (12-case workflow fan-out, 3 independent
  runs each, judged by independent per-run LLM-as-judge against the verbatim rubric, on Opus).
- **v2** carries full per-case, per-run detail (10-case fan-out, 5 independent runs each,
  self-judged against the verbatim rubric, on Opus).
- **v0 / v1** carry only the summary pass-count matrices produced in earlier sessions;
  per-run D1–D5 detail for those two was not retained and is **not** reconstructed here.
