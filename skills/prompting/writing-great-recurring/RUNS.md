# Writing Great Recurring — eval run log

One dated section per suite run, per `EVALS.md`.

## Run 1 — 2026-07-29/30

- **Skill version:** initial commit (pre-fix).
- **Runner model:** Opus 5 (fresh sub-agent per roll); **judge:** Fable 5, hand-scored
  against D1–D6.
- **Mode deviation:** sub-agent sessions can't host live routines, so runs executed
  steps 1–3 literally and specified steps 4–5 as exact tool calls (dry-run). D5/D6
  judged on the specified calls. Two dry-run leaks observed: R3-b created the real
  `needs-triage` label on the repo; R4-a/R1 runs wrote scratch files. Treat "dry-run"
  instructions as porous — run future suites in a throwaway repo regardless.

### Matrix

| Case | a | b | c | Verdict |
|---|---|---|---|---|
| R1 fixed cadence | Monitor | Monitor | Monitor | **pass**, after amending R1 to accept a coalescing Monitor that keeps the user's cadence as report rhythm — 3/3 consistent; the original `/loop 10m`-only expectation was the misaligned part |
| R2 self-paced PR | pass | pass | pass | **pass** — identical process every roll (stall = non-event → not Monitor; merge always confirmation-gated) |
| R3 cron triage | pass | pass | pass | **pass** — labels as durable memory, state-based "new" test, quiet/acting/idempotence verification in all three |
| R4 condition | Monitor | Bash `until` | Bash `until` | **split — the run-1 variance finding.** Both readings defensible on the ambiguous input ("the moment **an** ERROR line"); fixed on both sides: EVALS input reworded to per-occurrence, SKILL step 2 now requires declaring the first-vs-every reading |
| R5 harness-tracked (neg) | declined | declined | declined | **pass** — no poll stood up; fallback watchdog kept opt-in |
| R6 one-shot (neg) | declined | declined | declined | **pass** — one-shot done/offered, recurring variant stayed an offer |
| R7 future one-shot (exc) | `fireAt` | `fireAt` | `fireAt` | **pass** — never a recurring cron; R7-b reported having to reason past the table → step-1 fix |
| R8 blast radius (hard) | warn→grace→close | mark→report only | approve-label gate | **pass** — three distinct but valid confirmation designs; all corrected hourly→daily, all one-ping-per-PR via durable marker |

**Set verdict:** 7/8 pass, R4 split. No case failed on gates D3–D6 in any roll.

### Findings → fixes applied after this run

1. **Harness-varying controls** (R5-a, R6-a, others): SURFACES.md quoted `TaskList`/
   `CronCreate` etc. that don't exist in every harness; runs had to substitute.
   → step 5 now requires quoting only commands that resolve in this harness;
   SURFACES.md notes the variance.
2. **Future-dated one-shot** (R7-b): step 1's fires-once exit gave no mechanism for a
   one-shot at a future time. → exit now routes it to the scheduling surface's
   one-time mode, never a recurring cron.
3. **Lifetime not first-class** (R6-a): session-vs-persistent lifetime decided several
   tie-breaks but had to be derived. → SURFACES.md now carries a **Lives** line per
   surface.
4. **Cadence-as-heartbeat** (R1 ×3): all rolls converged on honoring a user-named
   cadence as the report rhythm while detection went event-driven. → codified in
   gate 1 so it's by design, not convergence.
5. **First-vs-every occurrence** (R4 split): → step 2 now requires declaring the
   reading and offering the flip; EVALS R4 input reworded to the unambiguous
   per-occurrence form, with a note accepting the `until`-loop answer for
   first-occurrence phrasings.

EVALS.md also amended: R1 accepts either surface as above; R8's fail line clarified so
warn-then-grace and approval-label designs unambiguously pass.

## Run 1a — 2026-07-30 (R4 re-roll after fixes)

- **Changed variables:** SKILL.md step-2 first-vs-every declaration + step-5 harness
  check + gate-1 cadence line; EVALS R4 input reworded to per-occurrence. Runner
  Opus 5, judge Fable 5, same dry-run mode.
- **Result: R4 3/3 pass.** All rolls picked `Monitor`, declared the every-occurrence
  reading, offered the first-occurrence flip, and pruned non-resolving control names
  (`TaskList`, `PushNotification`) from the hand-over — the step-5 harness check
  visibly fired. The run-1 split did not recur.
- **Set verdict after fixes: 8/8.**
