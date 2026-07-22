---
name: sharpen
description: Rewrite a rough prompt into a sharper one and recommend how to run it — model, effort level, and whether to escalate to a multi-agent workflow. User-invoked — type /sharpen with the prompt to improve.
disable-model-invocation: true
argument-hint: "The rough prompt to sharpen, or nothing to use the last one"
---

# Sharpen

Take a rough prompt and return a sharper one, plus how to run it — model, effort,
and whether to escalate to a workflow. Apply the **same five moves every run** — the
rewrite is a fixed process, not improvised, so the same weak prompt gets sharpened
the same way each time.

The prompt to sharpen is whatever the user passes in, or the most recent prompt
they're pointing at. If nothing is supplied, ask for the prompt (or a description
of what they were trying to get Claude to do).

## Invocation

The user invokes `/sharpen` with the rough prompt they want improved, or nothing to
reuse the most recent prompt they're pointing at. Interpret the request and act.
Examples:

- "/sharpen make the login page look nicer"
- "/sharpen fix the bug in auth.ts and tell me how to run it"
- "Sharpen the last thing I asked you to do"
- "/sharpen" (with no argument — use the most recent prompt in context)

## Steps

### 1. Diagnose against all five moves
Assess the prompt against **every** move in the reference below — not just the
first weakness you spot. For each move, note: present, missing, or misapplied.
Flag a move as missing or misapplied only if fixing it would **materially change
what the model does** — not merely make the prompt marginally tighter. A prompt
that a competent engineer would run as-is has no gaps: mark every move
**present** — a satisfied move is a finding, not a gap, so never upgrade one into
a weakness to justify a change. Suggestions such as "could add an example" or
"could name a type" are optional refinements, not weaknesses; leaving them
unchanged is correct.

*Done when:* all five moves are assessed and the specific weaknesses named. If no
move is missing or misapplied, record the prompt as **already sharp**.

### 2. Resolve the load-bearing blanks
Separate missing context into what can be retrieved and what only the user can
supply. Retrieve available context from the conversation, workspace, and named
sources before asking for it.

When unresolved blanks would materially change the prompt — especially the
**referent** (which file / PR / range), the **why**, the **win condition**, or a
**load-bearing constraint** — use the [`grilling`](../grilling/SKILL.md) skill to
interview the user one focused question at a time, and the
[`domain-modeling`](../domain-modeling/SKILL.md) skill to retain the resulting
project context (glossary and decisions). Follow each answer until the ambiguity is
resolved, then resume sharpening. For a prompt outside a codebase, run the same
focused interview directly without creating project docs.

If a blank is not load-bearing, or the user wants a template instead of an
interview, leave a `[bracketed blank]` for them to fill. Never invent private
context.

*Done when:* every load-bearing blank is filled from retrieved or elicited context,
and every remaining private-context dependency is bracketed rather than fabricated.

### 3. Recommend how to run it — model, effort, and whether to escalate
Apply the decision rules in [`RUNNING_IT.md`](RUNNING_IT.md), in order: pick the model,
tune the effort (naming a sweep when the level isn't obvious), then make the
escalate-or-not call.

Once the model is chosen, read exactly one model-specific reference:

- **Fable 5:** [`FABLE_5.md`](FABLE_5.md)
- **Opus 4.8:** [`OPUS_4_8.md`](OPUS_4_8.md)

Identify only the guidance that bears on this prompt; the reference does not license
unrelated scaffolding.

*Done when:* one model is named with a one-line why; a starting effort level is named
(or a candidate sweep when unclear), each with a one-line why; and the escalate call
is explicit — either a workflow with the justifying need and how to trigger it, or a
plain statement that a single agent at the recommended effort suffices. The matching
model reference has been read and its relevant guidance identified.

### 4. Rewrite
If step 1 found the prompt **already sharp** (no missing or misapplied move), return
it unchanged and say so in one line; offer any refinement as an explicit, bracketed
suggestion, never imposed. Never manufacture a weakness to justify a rewrite.

Otherwise, produce the sharpened prompt carrying every fix from step 1, the resolved
context or explicit blanks from step 2, and the applicable model-specific guidance
from step 3. Keep the user's voice and intent; change only what those sources require.

*Done when:* an already-sharp prompt is returned essentially unchanged with a one-line
note; otherwise the rewrite reflects every diagnosed weakness and applicable
model-specific instruction, without importing irrelevant reference material or
inventing weaknesses.

### 5. Present — or execute directly
**Fast path — run it here.** Carry out the sharpened prompt yourself in this session,
skipping the presentation, when *all three* hold:

1. **The user wants it done now.** The invocation is an implement-or-fix request the
   user wants carried out — not a prompt to hand off elsewhere, a design or exploration,
   or a survey.
2. **The running model is the one you'd recommend.** This session's model is the step-3
   model pick.
3. **The running effort is within ±1 of your pick.** This session's effort sits within
   one step of the step-3 effort on the `low → medium → high → xhigh → max` ladder.

When all three hold, say in one line that you're running it here because the model and
effort already match the recommendation, then execute the sharpened prompt from step 4
directly.

**Otherwise, present** for the user to run elsewhere, in this order: the **sharpened
prompt** (fenced, ready to copy) · one bullet per move you changed, saying what and why ·
the **run line** — model + effort + escalate-or-not call. Lead with the sharpened
prompt; keep the rest brief.

*Done when:* either the sharpened prompt has been executed in this session under a
one-line rationale (fast path), or all three presentation parts are shown with the
sharpened prompt first.

## The five moves — reference

Applied in this order. Each gives what to check and the positive fix.

**Explicitness** — Are scope, format, and constraints stated? A model acts on what's
written, not what's meant. *Fix:* name what to touch and what to leave alone, the
output shape, and the hard constraints.

**Decision frame** — Does the prompt say what the user will *do* with the answer and
what counts as a win? *Fix:* state the choice being made and the win condition — as a
blank when only the user knows it.

**Don't lead the witness** — Does the prompt pre-name a solution or ask for a survey?
A capable model defends a solution you hand it instead of comparing. *Fix:* ask for
the options first with the user's idea as one candidate, and for a recommendation
plus its main risk rather than a pros/cons list. Leave a survey ask alone when the
user genuinely wants the landscape.

**Altitude** — Is method dictated where the model could choose it, or is forceful
`CRITICAL / ALWAYS / NEVER` scaffolding present? Current models follow such phrasing
literally and over-trigger. *Fix:* state the outcome and only the load-bearing
constraints; say each rule once, plainly, with the why; drop to step-by-step only
where the method itself is load-bearing.

**Show, don't tell** — Is a format or tone described in prose that an example would
pin down? *Fix:* replace the description with 3–5 representative examples in identical
structure, including the hard case. Watch for accidental regularities the examples
would teach.
