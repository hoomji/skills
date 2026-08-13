# v4 — the four root-cause fixes (bracket-and-deliver, over-edit guard, model trigger, effort dial)

- **Skill version:** four working-tree edits on top of `4b3c378` (uncommitted at run time)
- **Variables changed vs v3 (four fixes, applied across two sub-runs):**
  1. **Fix 1 — bracket-and-deliver** (`SKILL.md` steps 2 & 6): on a load-bearing blank, always
     emit a fenced prompt with `[bracketed blanks]` + branches + run-rec, *then* ask — never halt
     to interview with nothing delivered.
  2. **Fix 2 — already-sharp / over-edit guard** (`SKILL.md` step 4): the already-sharp prompt
     *is* the original verbatim; prose→bullets reformatting, spec-restatement, and folded-in
     constraints (secrets/PII, control-flow policy, added examples) are forbidden edits.
  3. **Fix 3 — heavyweight trigger** (`RUNNING_IT.md` model rule): a large unattended batch job
     ("migrate all N X end-to-end… over a weekend") is the signature heavyweight case — name the
     heavyweight as *the* rec, not a fallback/reserve/pilot.
  4. **Fix 4 — effort dial** (`RUNNING_IT.md` effort rule): match effort to the *kind* of task —
     `xhigh` bounded coding (a short diff is still coding), `high` diagnostic/decision/writing +
     unpinnable-win — and recommend what the *task* needs, not what the session is running at.
- **Runs/case:** 3 (independent), workflow-judged (`scratchpad/sharpen-suite.js`)
- **Model / judge:** Opus 4.8; independent per-run judge, verbatim D1–D6 rubric + case checks
- **Checkpoints:** Fix 1 alone = **7/12** (run `wooou02gl`); Fixes 2+3+4 combined = **9/12**
  (run `wvemwkbo0`, this file)

## Summary — SET FAIL, 9/12 (v3 was 4/12)

| Case | v3 | Fix1 | v4 | Failing dims (v4) |
|------|----|------|----|-------------------|
| C1 explicitness | 0/3 | 3/3 | **3/3** ✅ | — |
| C2 decision frame | 0/3 | 3/3 | **3/3** ✅ | — |
| C3 don't-lead | 2/3 | 3/3 | **3/3** ✅ | — |
| C4 altitude | 3/3 | 2/3 | **1/3** ❌ | D3 (2×), D4 (2×), D1 (1×) |
| C5 show-don't-tell | 0/3 | 0/3 | **0/3** ❌ | D3 (3×), D1 (2×), D6 (1×) |
| C6 blank trap | 1/3 | 1/3 | **3/3** ✅ | — |
| C7 already-sharp | 0/3 | 0/3 | **3/3** ✅ | — |
| C8 survey | 3/3 | 3/3 | **3/3** ✅ | — |
| C9 heavyweight | 0/3 | 0/3 | **3/3** ✅ | — |
| C10 security | 3/3 | 3/3 | **3/3** ✅ | — |
| C11 branch clear | 0/3 | 0/3 | **1/3** ❌ | D4 (1×), D6 (1×) |
| C12 branch wide | 0/3 | 3/3 | **3/3** ✅ | — |

## Per-run grid (v4 combined)

```
C1   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C2   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C3   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C4   1/3  ✓✓✓✓✓✓ | ✓✓✗✗✓✓ | ✗✓✗✗✓✓        (D1 D2 D3 D4 D5 D6)
C5   0/3  ✗✓✗✓✓✓ | ✓✓✗✓✓✗ | ✗✓✗✓✓✓
C6   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C7   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C8   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C9   3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C10  3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
C11  1/3  ✓✓✓✓✓✗ | ✓✓✓✗✓✓ | ✓✓✓✓✓✓
C12  3/3  ✓✓✓✓✓✓ | ✓✓✓✓✓✓ | ✓✓✓✓✓✓
```

## Verdict

**Every fix hit its primary target.** C6 (1/3→3/3), C7 (0/3→3/3), C9 (0/3→3/3) all flipped, and
Fix 1's five interview-path cases (C1/C2/C12 fully; C6 via effort) hold. The Step-5 branching
(D6) passes wherever a deliverable is produced.

**Two residuals + one self-inflicted regression:**

- **C4 regressed 3/3 → 1/3 — Fix 4 is the likely cause.** The effort discriminator's `high`
  bucket says "for writing"; "write a test for **every** function" trips that word, so the model
  buckets test-writing as *writing → `high`* when the case wants *coding → `xhigh`* (D4 misses on
  runs 2–3). The long-standing altitude-choreography weakness (D3: keeps run→read→fix→re-run,
  recasts the standing rule as a one-off) also resurfaced. **Fix:** disambiguate — `high` =
  prose/doc writing; writing **code or tests** is coding → `xhigh`. C4 is historically noisy
  (v2 0/5, v3 3/3); confirm with 5 runs.
- **C5 (0/3) — the fifth issue, untouched by the four.** Show-don't-tell is *named but not
  executed*: the rewrite says "include 3–5 examples" instead of embedding concrete example commit
  messages (with a breaking-change edge case); D3 fails all 3 (over-edit into an enforcement/
  audit/history-rewrite spec), one run fabricates divergent forks (D6). Needs its own fix in
  step 4 / the show-don't-tell move: *demonstrate the format inline, don't describe it.*
- **C11 (1/3) — mostly fixed by Fix 4, two stragglers.** Run 2 still under-calls effort
  (`medium`/`low` on bounded coding); run 1 forces a divergent fork (env-configurable dressed as
  an "alternate intent") on the narrow prompt — the C11 forced-divergence trap.

## Next target (priority)

1. **Fix 4b** — disambiguate "writing" (recover C4 D4); revisit the altitude-choreography D3
   weakness (pre-existing, independent of the four).
2. **Fix 5** — show-don't-tell must embed examples inline, not describe them (C5).
3. **C11 stragglers** — bounded-coding effort floor + forced-divergence guard on narrow prompts.
4. Re-run at **5 runs/case** to separate real state from 3-run variance on C4/C11.
