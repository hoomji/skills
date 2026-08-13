# v3 — adjacent branching + always-print, first D1–D6 run

- **Skill version:** `54f362e` (working tree clean at run time)
- **Variables changed vs v2 (bundled — not a clean single-variable step):**
  1. New **Step 5 "Branch into adjacent prompts"** (always fires); old present/execute is now
     **Step 6**, whose fast path runs the *recommended* prompt.
  2. **Step 6 "always print the fenced prompt"** + rubric **D5 tightened** to require a fenced
     main prompt *"in every case, no elicitation exception."*
  3. Suite grew to **12 cases** (added C11/C12 branching) and **D6 branch-quality** dimension.
- **Runs/case:** 3 (independent), fanned out via workflow (`scratchpad/sharpen-suite.js`,
  36 skill runs + 36 judges = 72 agents)
- **Model:** Opus 4.8 (skill runs assume session = Opus 4.8 @ `high` for fast-path logic)
- **Judge:** independent LLM-as-judge per run, verbatim D1–D6 rubric + per-case checks

## Summary

**SET: FAIL — 4/12 cases passed** (C3, C4, C8, C10).

| Case | Pass | Case verdict | Failing dimension(s) |
|------|------|--------------|----------------------|
| C1 explicitness | 0/3 | **FAIL** | D5, D6 (D4 1×) — interview-path |
| C2 decision frame | 0/3 | **FAIL** | D4, D5, D6 — interview-path |
| C3 don't-lead | 2/3 | PASS (majority) | D4 1× (`xhigh` vs `high`) |
| C4 altitude | 3/3 | PASS | — |
| C5 show-don't-tell | 0/3 | **FAIL** | D5, D6, D4, D1 2× — interview-path + didn't execute the move |
| C6 blank trap | 1/3 | **FAIL** | D4, D5, D6 (2×) — interview-path |
| C7 already-sharp **[trap]** | 0/3 | **FAIL** | D1, D3, D4 (3×) — over-edit trap regressed |
| C8 survey exception **[trap]** | 3/3 | PASS | — |
| C9 heavyweight + escalate | 0/3 | **FAIL** | D4 (3×) — wrong model |
| C10 security + effort **[trap]** | 3/3 | PASS | — |
| C11 branch: clear intent | 0/3 | **FAIL** | D4 (3×) — effort below band |
| C12 branch: wide-open | 0/3 | **FAIL** | D4, D5, D6 (3×) — interview-path |

## Four root causes

1. **Rubric ↔ skill contradiction — the biggest bucket (C1, C2, C5, C6, C12).** D5 now demands
   a fenced main prompt *in every case*, but Step 2 still says to **halt and interview** on a
   load-bearing blank. When the model takes the ask-path it emits no fenced prompt → auto-fails
   D5 + D6 (no branches yet) + usually D4 (run-rec deferred). Judging is inconsistent — C6-run3
   *passed* by ruling the ask-path acceptable.
   **DECISION (Henry, 2026-07-22): bracket-and-deliver-then-ask.** Sharpen must always emit a
   fenced prompt with `[bracketed blanks]` + branches + run-rec, *then* ask. → these 5 are **skill
   fixes** (align Step 2 + Step 6; keep D5), not rubric fixes.
2. **Effort-dial instability (C3, C6, C7, C9, C11)** — the long-standing Step-3 target. Efforts
   scatter every direction vs the case band: `xhigh` where `high` wanted (C3, C6), `high` where
   `xhigh` wanted (C7), `medium`/`low` where `high`/`xhigh` wanted (C11), a `low↔med` sweep where
   `high`/`xhigh` wanted (C9).
3. **C7 over-edit trap regressed to 0/3.** On the already-sharp prompt every run invents gaps (a
   "which logger" fork, a show-don't-tell need) and expands a tight 3-sentence prompt into a long
   spec (D1 + D3 fail). The v2 materiality guard no longer holds under the 6-step/branching skill.
4. **C9 model selection 0/3.** A 40-integration weekend migration (textbook heavyweight/Fable)
   routed to the daily driver every run; one run explicitly said "no case for the heavyweight."

## Per-case detail (D1–D6 grid)

### C1 — explicitness · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| 2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |

Diagnosis/blanks clean (named the scope gap, refused to invent the referent). All 3 took the
ask-path → no fenced prompt, no branches. Case explicitly permits bracketing the referent, so
under bracket-and-deliver this is a skill fix.

### C2 — decision frame · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 3 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

De-led the yes/no and widened to the goal correctly, but paused to interview instead of
delivering a bracketed prompt — same interview-path failure across the board.

### C3 — don't-lead · 2/3  **PASS (majority)**

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — `xhigh` flat; case wants `high` |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Core don't-lead behavior + branching + presentation all solid. Sole miss is the familiar D4
effort slip (run 1 pattern-matched "diagnostic ⇒ `xhigh`").

### C4 — altitude · 3/3  **PASS** *(recovered from v2 0/5)*

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Notable turnaround: every run flattened the caps **and dropped** the run→read→fix→re-run
choreography (the exact v2 failure), stated the outcome, kept the tests-for-new-behavior intent.
Effort `xhigh` correct all 3.

### C5 — show-don't-tell · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |
| 2 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ — named the move, didn't execute it (kept prose specs) |
| 3 | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — invented forks to justify an interview |

Two failure flavors: the interview-path (runs 1, 3) and — even when it delivered — retaining
prose format specs instead of embedding 3–5 exemplars with a breaking-change edge case (run 2).

### C6 — blank trap · 1/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |
| 2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

**Trap held** — no run fabricated a bug/file. Failures are interview-path (D5/D6) + effort. Run 3
passed by delivering; the judge sanctioned deferring branches on a truly-unknown referent, which
is the tension bracket-and-deliver must resolve cleanly.

### C7 — already-sharp **[trap]** · 0/3  *(regressed from v2 5/5)*

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| 2 | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |
| 3 | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |

The over-edit trap fails on all 3: invents explicitness gaps (D1) and expands the tight prompt
into a verbose spec (D3), plus effort `high` where the case wants `xhigh` (D4). Presentation +
branching (D5/D6) are fine — the regression is squarely in Steps 1/4 under the new structure.
D2 still holds (logger left to "inspect the file", not fabricated).

### C8 — survey exception **[trap]** · 3/3  **PASS**

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

No run forced a single-pick recommendation; the landscape ask was preserved. Trap clean.

### C9 — heavyweight + escalate · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — picked daily driver, not Fable |
| 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — Fable right, but `low↔med` sweep vs `high/xhigh` |
| 3 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — daily driver, "no case for the heavyweight" |

Escalate=YES, altitude, branching, presentation all correct; the entire miss is model/effort in
Step 3. **Regression vs v2 (5/5).** Runs 1 & 3 wrong model; run 2 right model, wrong (too-low)
effort.

### C10 — security + effort **[trap]** · 3/3  **PASS**

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 3 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Daily driver (noting Fable refuses cyber-adjacent work), no reflexive `max`, opt-in escalation.
Both traps handled every run.

### C11 — branch: clear intent **[trap: forced divergence]** · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — effort `medium` (floats `low`) |
| 2 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — effort `medium` below band |
| 3 | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ — effort `low` |

**Branching worked as designed** (D6 ✓ all 3: honest minor scope variations, main unchanged, no
forced divergence) and presentation is clean. The only miss is D4 — effort sits *below* the
`high`/`xhigh` band for bounded coding. Note this is the opposite lean from C3/C6 (`xhigh` too
high there): the dial has no stable anchor for bounded coding edits.

### C12 — branch: wide-open · 0/3

| Run | D1 | D2 | D3 | D4 | D5 | D6 | pass |
|-----|----|----|----|----|----|----|------|
| 1 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |
| 2 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |
| 3 | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ — interview-path |

Handled the unpinnable win condition honestly (D2 ✓, no fabricated metric) but escalated the
ambiguity to a clarifying question and **skipped the very branch step this case exists to test**
(D5/D6 fail) plus withheld the run-rec (D4). The strongest argument for bracket-and-deliver: a
wide-open prompt is exactly where distinct fenced branches are most useful.

## Interpretation

- **Two genuine gains vs v2:** C4 recovered 0/5 → 3/3 (altitude choreography now dropped), and the
  Step-5 branching feature itself works — D6 passed wherever the skill actually produced a
  deliverable (C3, C4, C7, C8, C9, C10, C11).
- **Two regressions vs v2:** C7 (5/5 → 0/3, over-edit trap) and C9 (5/5 → 0/3, model selection).
  Both are Step-1/Step-3 behavior, not branching.
- **The dominant failure is structural:** the interview-path ↔ "fenced every case" contradiction
  (C1, C2, C5, C6, C12). Resolved by decision to **bracket-and-deliver-then-ask** → skill fix.
- **Effort dial is still the through-line** (C3, C6, C7, C9, C11) and now demonstrably *unanchored*
  in both directions (too high on diagnostics, too low on bounded coding).

**Next target (priority order):** (1) bracket-and-deliver in Steps 2+6, (2) re-anchor the C7
already-sharp/over-edit guard, (3) fix C9 model selection, (4) the effort dial. One variable at a
time; re-run between each.
