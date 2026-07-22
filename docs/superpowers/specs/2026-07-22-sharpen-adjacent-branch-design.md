# Design: Sharpen "Branch into adjacent prompts" step

**Date:** 2026-07-22
**Skill:** `skills/sharpen/SKILL.md`
**Status:** Approved, ready for implementation plan

## Problem

`sharpen` currently produces exactly one faithful rewrite of the user's prompt.
It never surfaces that the original prompt may admit more than one reasonable
reading of what the user wants. When intent is genuinely ambiguous, the single
rewrite silently commits to one interpretation.

## Goal

Add a step that, using the original prompt, the resolved context, and the main
sharpened prompt, produces 2–3 **adjacent** prompts — each a different reading of
intent/scope — and recommends one, with reasoning. The branch is additive: it
never edits or replaces the faithful main rewrite.

## What "adjacent" means

Each alternative reinterprets **what the user might really want** — a broader,
narrower, or sideways framing of the goal. Example, from "fix the bug in auth.ts":

- (main) fix the specific bug as described
- (narrower) reproduce and fix only the reported symptom, no refactor
- (broader) fix the bug and add a regression test guarding it
- (sideways) diagnose why this *class* of bug reaches auth.ts and fix the root cause

Alternatives vary **intent/scope only** — not style, altitude, or run-strategy.

## Placement in the skill

New **Step 5: Branch into adjacent prompts**, inserted between the current
*Rewrite* (step 4) and *Present/execute*. The former step 5 becomes **step 6**.

Inputs consumed: the original prompt, the resolved context / explicit blanks from
step 2, and the main sharpened prompt from step 4.

## Behavior

### Always fires

The step runs on every invocation. It does **not** gate on detected ambiguity.

### Guard against the C7 over-editing trap

- The main sharpened prompt from step 4 stays **faithful and untouched**.
  Branches are *additional options*, never edits to it.
- When the original intent is genuinely unambiguous, the step does **not**
  manufacture artificial divergence. It states that intent is narrow and presents
  the alternatives as honest minor scope variations
  (e.g. "intent here is narrow; these are small scope variations").
- Never invent private context to create a fork; the same no-fabrication rule as
  step 2 applies.

### Each alternative

- A real, **fenced runnable prompt** — any alternative could be executed as-is.
- A one-line **"why you'd want this"** naming the interpretation it serves.

Alternatives stay lightweight: prompt + why only. No per-alternative run-line.

### The recommendation

- Ranks **main + alternatives together** and names one winner, with a one-line why.
- The full step-3 run-line (model · effort · escalate) is computed **only for the
  recommended prompt**. If an alternative wins, its run-line may differ from the
  main's.

## Fast-path interaction (step 6)

- The **recommended** prompt — main *or* an alternative — is what the fast-path
  executes when its three existing conditions hold.
- **Consent guard (always):** before executing, print all options, state which one
  is being run and why, so an unwanted reinterpretation is visible and
  interruptible before any action. Consistent with the skill's existing
  "always print the sharpened prompt before executing" rule.
- **High-confidence guard on alternatives:** when the recommended prompt is an
  *alternative* (a reinterpretation) rather than the faithful main, the fast-path
  runs it only if the recommendation is **high-confidence**. A low-confidence
  branch win falls back to presenting, not auto-running. (Recommending the main
  prompt carries no extra confidence bar — it is the faithful rewrite.)

## Output order (non-fast-path presentation)

1. Main sharpened prompt (fenced)
2. The 2–3 adjacent options (fenced, each with its one-line why)
3. The recommendation + its run-line (model · effort · escalate)
4. The per-move change bullets (what changed and why), as today

Lead with the main sharpened prompt; keep the rest brief.

## Evals (out of scope for this change unless folded in)

The C1–C10 regression suite does not cover branching. Add 1–2 cases:

- **Clear-intent prompt:** assert branches stay honest near-variants and the main
  rewrite is unchanged (extends the C7 over-editing guard).
- **Wide-open prompt:** assert the alternatives are genuinely distinct intents and
  the pick is justified.

Run per the existing eval method (5 runs/case, fan out via subagents on Opus,
append a new `vN-*.md` under `skills/sharpen/runs/`).

## Non-goals

- Not varying style, altitude, or run-strategy across alternatives (intent/scope
  only).
- Not gating the step on ambiguity detection (it always fires).
- Not giving every alternative a full run-line (only the recommended one).
- Not editing or replacing the faithful main rewrite.
