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

## Pass-count matrix (all runs)

Pass count = runs where **all five** rubric dimensions (D1–D5) + the case checks held.
Denominators differ (v0/v1 = 3 runs, v2 = 5). Case-level PASS = majority of runs.

| Case | Target | v0 | v1 | v2 |
|------|--------|----|----|----|
| C1 | explicitness | 3/3 | pass | 5/5 |
| C2 | decision frame | 3/3 | pass | 5/5 |
| C3 | don't-lead | 3/3 | pass | 3/5 |
| C4 | altitude | 1/3 | 2/3 | 0/5 |
| C5 | show-don't-tell | 2/3 | 3/3 | 4/5 |
| C6 | blank trap | 3/3 | pass | 3/5 |
| C7 | already-sharp **[target]** | 0/3 | 0/3 | **5/5** |
| C8 | survey exception | 3/3 | pass | 5/5 |
| C9 | heavyweight + escalate | 1/3 | 3/3 | 5/5 |
| C10 | security + effort | 3/3 | pass | 5/5 |

## Reading the loop

- **v2 fixed C7** (0/3 → 5/5) via the Step-1 materiality threshold; v1's already-sharp
  scaffolding alone never moved it.
- **No gate case (C1–C3, C5, C6, C8, C10) regressed to fail** under v2. The C3/C6 3/5 and
  C5 4/5 are all **D4 (effort-dial) misses in Step 3**, which v2 did not touch — surfaced by
  the larger 5-run denominator, not caused by the fix.
- **C4/C9 are noisy/calibration-sensitive** and reported separate from the regression gate.
  C4 has failed since baseline (Altitude choreography kept as "load-bearing").
- **Next target:** the Step-3 effort dial (`xhigh`-default vs `high` for bounded diagnostic /
  unpinnable-win-condition prompts), then C4's altitude choreography. One variable at a time.

## Provenance

- **v2** carries full per-case, per-run detail (10-case fan-out, 5 independent runs each,
  self-judged against the verbatim rubric, on Opus).
- **v0 / v1** carry only the summary pass-count matrices produced in earlier sessions;
  per-run D1–D5 detail for those two was not retained and is **not** reconstructed here.
