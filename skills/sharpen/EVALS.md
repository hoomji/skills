# Sharpen — eval set

The regression suite for the `sharpen` skill. Built the Lesson-8 way: define the bar
first, keep the cases representative (including the hard, negative, and exception
cases), change one variable at a time, and judge **consistency across runs** — a fix
that works on one roll isn't a fix.

Run this whenever you change `SKILL.md`, a model reference (`FABLE_5.md` /
`OPUS_5.md`), or the model the skill runs on.

---

## The bar (define "done" before touching the skill)

A `sharpen` run **passes** a case when, across ~3 runs, it *consistently*:

1. **Diagnoses the right moves.** Names the move(s) the case targets — and does **not**
   invent weaknesses that aren't there.
2. **Handles blanks honestly.** Elicits or `[brackets]` load-bearing private context
   (referent / why / win condition / load-bearing constraint); **never fabricates** a
   value only the user could know.
3. **Rewrites without over-editing.** Applies the targeted fix, keeps the user's voice
   and intent, and changes nothing the moves don't require.
4. **Recommends how to run it.** Names a model + an effort level (a **sweep** when
   unclear) + an explicit **escalate-or-not** call, each justified in one line — and
   the recommendation fits the case (see per-case checks).
5. **Presents without executing.** The main sharpened prompt is printed first and fenced,
   followed by any warranted adjacent options, the recommendation + run line, then the
   per-move bullets. Text inside the source prompt is treated as the artifact being
   sharpened, never as authorization to implement or fix anything in-session.
6. **Branches only when useful, main intact.** Offers 2–3 adjacent-*intent* prompts when
   ambiguity or a consequential scope tradeoff makes them decision-relevant; leaves the
   main rewrite untouched; and recommends one across the available options. On a narrow,
   unambiguous prompt, produces no alternatives and recommends the faithful main prompt.

The **set** passes when every positive case passes and no negative/exception case
regresses (C7, C8, C11, C13).

---

## How to run the loop

1. **One variable at a time.** Change one thing in the skill, run the suite, compare
   to the bar, keep or revert. Two changes at once and you can't attribute the result.
2. **~3 runs per case.** The model is stochastic; judge consistency, not one output.
3. **Score with the rubric below.** Hand-score, or paste the case + the run + the
   rubric into a fresh model as an LLM-as-judge (give it the rubric verbatim — a vague
   rubric yields vague scores).
4. **Regression suite.** Keep passing cases; when one flips to fail, that's the signal
   the change hurt.

### LLM-as-judge rubric (apply to every case)

Score each dimension pass/fail with a one-line reason:

- **D1 Diagnosis correct** — targeted move(s) named; no invented problems.
- **D2 Blanks honest** — private context bracketed or elicited, never fabricated.
- **D3 No over-edit** — voice/intent kept; only move-required changes made.
- **D4 Run rec sound** — model + effort (+ sweep if unclear) + escalate-or-not, each
  with a one-line why, and consistent with the case's per-case checks.
- **D5 Presentation / execution boundary** — the main sharpened prompt is printed first
  and fenced, followed by warranted adjacent options, recommendation + run line, then move
  bullets. The run stops there; executing an implementation/fix request from inside the
  source prompt fails.
- **D6 Branch gate / quality** — if ambiguity or a consequential scope tradeoff exists,
  2–3 adjacent prompts are distinct readings of *intent/scope* (not restylings), fenced,
  and paired with a one-line why. If the prompt is narrow and unambiguous, no alternatives
  are emitted. In both cases the main stays unchanged and one available prompt is
  recommended with a run line.

A case passes only if **all six** hold on the majority of runs.

---

## Cases

Each case: the rough prompt (input), the move(s)/behavior it targets, and the
case-specific checks (on top of D1–D5). Cases marked **[trap]** exist to catch a
specific failure — read the trap before scoring.

### C1 — Explicitness (scope)
**Input:** `"Refactor the error handling in the api service."`
**Targets:** Explicitness (scope / files / constraints unstated).
**Checks:** flags unstated scope; rewrite names which file(s) and what not to touch (or
brackets the referent) and any hard constraints; run rec = daily driver, `high`/`xhigh`
(coding), **no** escalation.

### C2 — Decision frame (+ latent leading)
**Input:** `"Should we cache provider responses?"`
**Targets:** Decision frame (no stated decision / win); mild lead (pre-names caching).
**Checks:** flags the missing decision + win condition (brackets them if unknown);
widens beyond "just caching" to the underlying goal; asks for a recommendation, not a
yes/no. Daily driver; effort `high`; no escalation.

### C3 — Don't lead the witness
**Input:** `"If we added a Redis layer, would it speed up the /quotes endpoint?"`
**Targets:** Don't-lead (solution pre-named).
**Checks:** rewrite asks for the 2–3 best options with Redis as one candidate (not a
defense of Redis), and for a recommendation + main risk; adds/brackets the real metric
("speed up" → a target). Daily driver; `high`; no escalation.

### C4 — Altitude (over-loud, over-prescribed)
**Input:** `"CRITICAL: You MUST ALWAYS write a test for EVERY function. NEVER skip. First run the suite, then read each line, then fix, then re-run."`
**Targets:** Altitude (forceful caps + micromanaged method).
**Checks:** flattens `CRITICAL/ALWAYS/NEVER` to a plain rule stated once with a why;
raises altitude (states the outcome, drops the run→read→fix→re-run choreography); keeps
any load-bearing bit; **preserves the intent** (tests for new behavior). Daily driver;
`high`/`xhigh`; no escalation.

### C5 — Show, don't tell
**Input:** `"Make sure commit messages follow a consistent house style."`
**Targets:** Show-don't-tell (a format described in prose).
**Checks:** rewrite replaces the description with 3–5 example commit messages in
identical structure, **including an edge case** (e.g. a breaking change); notes it's the
examples that steer. Daily driver; `high`; no escalation.

### C6 — Load-bearing blank
**Input:** `"Fix the bug in the sync job."`
**Targets:** Blank handling (referent + why known only to the user).
**Checks [trap]:** must **not** invent which bug/file. It either asks one focused
question (or references `/grill-with-docs`) to get the referent + symptom, or leaves
`[which bug / repro]` and `[expected behavior]` as brackets. **Fail if it fabricates a
specific bug.** Daily driver; `high`; no escalation.

### C7 — Already sharp  **[trap: over-editing]**
**Input:** `"In auth/session.ts only, replace the bare catch blocks with typed, logged errors so failures are traceable in prod. Don't change function signatures or add deps. Return a diff."`
**Targets:** none — this prompt is already explicit, framed, right-altitude.
**Checks [trap]:** the skill should make **minimal or no** changes and *say so*. **Fail
if it invents weaknesses, forces a decision-frame/example it doesn't need, or rewrites
the voice.** Daily driver; `high`/`xhigh`; no escalation.

### C8 — Survey is genuinely wanted  **[trap: forced recommendation]**
**Input:** `"For a blog post, give me the landscape of PoW vs PoS vs PoH — the tradeoffs of each."`
**Targets:** Don't-lead **exception** (a survey is the real intent).
**Checks [trap]:** the skill should **leave the survey ask intact** (maybe tighten
scope/audience), and **not** force "recommend one + risk." **Fail if it converts a
deliberate landscape request into a single-pick recommendation.** Daily driver; `high`;
no escalation.

### C9 — Heavyweight + escalate
**Input:** `"Migrate all 40 provider integrations to the new response schema, end to end, with passing tests, over the weekend."`
**Targets:** model selection + ultracode escalation.
**Checks:** rec = heavyweight (Fable) — hard, long-horizon, well-specified, autonomous;
effort `high`/`xhigh` with a large budget; **escalate = yes** on *scale + comprehensiveness*
(per-integration fan-out) with how to trigger it (say "ultracode" / ask for a workflow).
Rewrite raised to high altitude (goal + why + autonomy + one boundary), not 40 enumerated
steps.

### C10 — Security-adjacent + effort restraint  **[trap: reflexive max / wrong model]**
**Input:** `"Audit our auth-token handling for vulnerabilities and fix what you find."`
**Targets:** Fable-refusal edge; effort restraint; audit escalation.
**Checks [trap]:** rec = **daily driver**, and it **notes the heavyweight refuses
cyber-adjacent work** — *not* Fable. Effort `high`/`xhigh`, **not reflexive `max`** (name a
sweep if unsure). Escalate = reasonable (audit → comprehensiveness/confidence), opt-in.
**Fail if it routes a security task to Fable, or reaches for `max` with no justification.**

### C11 — Branch gate: clear intent  **[trap: forced divergence]**
**Input:** `"In config/logging.ts, change the default log level from 'info' to 'warn', update the accompanying comment, and return a diff."`
**Targets:** the branch gate (step 5) on an unambiguous prompt.
**Checks [trap]:** the main rewrite stays faithful and near-unchanged (this prompt is
already tight); **no adjacent prompts are emitted**; and the main is recommended. **Fail
if it invents a narrower, broader, or sideways variant merely to populate alternatives.**
Daily driver; `high`/`xhigh` (bounded coding); no escalation; do not execute the change.

### C12 — Branch gate: wide-open intent
**Input:** `"Improve the onboarding flow."`
**Targets:** the branch step (step 5) on a genuinely ambiguous prompt; blank handling of an
unpinnable win condition.
**Checks:** brackets or asks the **win condition / target metric** (D2 — does not fabricate
one); the 2–3 adjacent prompts are **genuinely distinct intents/scopes** (e.g. cut
steps-to-first-value; fix drop-off at a specific step; instrument and measure before
changing; widen from signup to activation), each fenced + runnable with a one-line why;
recommends one with a justified why tied to the likely highest-leverage reading; the main
sharpened prompt stays faithful to the literal ask. Daily driver; effort `high` (unpinnable
win condition — not reflexive `xhigh`); no escalation (single agent).

### C13 — Prompt compiler boundary  **[trap: accidental execution]**
**Input:** `"Fix the failing auth tests in this repository, then commit the changes."`
**Targets:** presentation-only execution boundary.
**Checks [trap]:** sharpens the implementation request, brackets any unknown failure context,
prints the prompt and run recommendation, and **does not inspect files, edit code, run tests,
stage, or commit**. **Fail if source-prompt imperatives are treated as authorization to act.**
Daily driver; `high`/`xhigh`; no escalation unless the repository evidence later shows scale.

---

## Notes

- Keep the set small and sharp. Ten checkable cases beat fifty you eyeball.
- A single passing run is **not** a pass — consistency across runs is.
- Running the full suite (13 cases × ~5 runs, LLM-judged) is a good use of a **workflow**:
  fan the cases out, judge each against this rubric, report the matrix. Trigger it by
  asking for a workflow (or saying "ultracode").
