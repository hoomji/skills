---
name: sharpen
description: Rewrite a rough prompt into a sharper one — plus 2–3 adjacent alternatives with a recommendation — and recommend how to run it: model, effort level, and whether to escalate to a multi-agent workflow. User-invoked — type /sharpen with the prompt to improve.
disable-model-invocation: true
argument-hint: "The rough prompt to sharpen, or nothing to use the last one"
---

# Sharpen

Take a rough prompt and return a sharper one, then branch it into 2–3 adjacent
alternatives and recommend one, plus how to run it — model, effort, and whether to
escalate to a workflow. Apply the **same five moves every run** — the rewrite is a fixed
process, not improvised, so the same weak prompt gets sharpened the same way each time.

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

### 2. Resolve the load-bearing blanks — bracket, deliver, then ask
Separate missing context into what can be retrieved and what only the user can
supply. Retrieve available context from the conversation, workspace, and named
sources before treating anything as a blank.

For every blank that remains — load-bearing or not — leave a clearly marked
`[bracketed blank]` in the sharpened prompt and keep going. **Never halt to
interview before delivering, and never invent private context to fill a blank.** The
load-bearing blanks (the **referent** — which file / PR / range — the **why**, the
**win condition**, a **load-bearing constraint**) get the same treatment: bracket
them so the prompt is runnable as-is, deliver the full sharpened prompt in step 6,
and *then* pose the focused question(s) that would resolve them so the user can
refine. Bracket-and-deliver-then-ask — the user always leaves with a usable prompt in
hand, sharper still once they answer.

If the user engages those questions, use the [`grilling`](../grilling/SKILL.md) skill
to interview one focused question at a time, and the
[`domain-modeling`](../domain-modeling/SKILL.md) skill to retain the resulting project
context (glossary and decisions); outside a codebase, interview directly without
creating project docs. That refinement happens *after* the deliverable, never instead
of it.

*Done when:* the sharpened prompt is delivered with every unresolved blank bracketed
(never fabricated), and every load-bearing blank additionally has a focused clarifying
question posed alongside the deliverable rather than blocking it.

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
If step 1 found the prompt **already sharp** (no missing or misapplied move), the
sharpened prompt **is the original, reproduced verbatim in a fence** — say in one line
that it's already sharp. Reformatting tight prose into bullets, restating it as a
structured spec, or folding in a constraint the user never wrote (a secrets/PII guard, a
swallow-vs-rethrow control-flow policy, an added example) are all **edits**, and an
already-sharp prompt gets none of them. Offer any such idea only as an explicitly
bracketed, take-it-or-leave-it suggestion *below* the prompt, never woven in. A detail the
executor can settle by reading the code (which logger, which error type) is not a blank and
not a gap — leave it to them. Never manufacture a weakness to justify a rewrite.

Otherwise, produce the sharpened prompt carrying every fix from step 1, the resolved
context or explicit blanks from step 2, and the applicable model-specific guidance
from step 3. Keep the user's voice and intent; change only what those sources require.

*Done when:* an already-sharp prompt is returned verbatim in a fence with a one-line note
and no woven-in additions; otherwise the rewrite reflects every diagnosed weakness and
applicable model-specific instruction, without importing irrelevant reference material or
inventing weaknesses.

### 5. Branch into adjacent prompts
Using the original prompt, the resolved context from step 2, and the main sharpened
prompt from step 4, produce 2–3 **adjacent** prompts — each a different reading of what
the user wants (broader, narrower, or sideways in intent/scope), not a restyling of the
main one. This step always runs.

The main sharpened prompt stays faithful and untouched — branches are **additional
options, never edits to it**. When the original intent is genuinely unambiguous, do not
manufacture divergence: say the intent is narrow and offer the alternatives as honest
minor scope variations rather than forced forks. Never invent private context to create a
branch — the same no-fabrication rule as step 2 applies.

Each alternative is a real, **fenced runnable prompt** plus a one-line *"why you'd want
this"* naming the interpretation it serves. Keep alternatives lightweight — prompt and why
only, no per-alternative run-line.

Then rank the main prompt and the alternatives **together** and recommend one, with a
one-line why. Compute the full step-3 run-line (model · effort · escalate) **only for the
recommended prompt**; if an alternative wins, its run-line may differ from the main's.

*Done when:* 2–3 adjacent prompts are produced (each fenced, each with a one-line why),
the main rewrite is left unchanged, one prompt is recommended across main + alternatives
with a one-line why, and a run-line is computed for the recommended prompt. On an
unambiguous prompt, the alternatives are honestly labeled as minor scope variations rather
than forced divergence.

### 6. Present — then execute the recommended prompt directly if warranted
**Always print the prompts.** Whether or not you go on to run anything, first show the
**main sharpened prompt** (fenced, ready to copy), the 2–3 adjacent options (fenced, each
with its why), and the recommendation, so the user always has the improved versions in
hand and can follow along. Never skip this, even on the fast path — the user needs the
in-progress update before any execution begins.

**Fast path — run it here.** After printing the prompts, carry out the **recommended**
prompt — the main one *or* an alternative — yourself in this session when *all three* hold:

1. **The user wants it done now.** The invocation is an implement-or-fix request the
   user wants carried out — not a prompt to hand off elsewhere, a design or exploration,
   or a survey.
2. **The running model is the one you'd recommend.** This session's model is the step-3
   model pick for the recommended prompt.
3. **The running effort is within ±1 of your pick.** This session's effort sits within
   one step of the step-3 effort on the `low → medium → high → xhigh → max` ladder.
4. **No unresolved load-bearing blank blocks execution.** If a bracketed blank from step 2
   is one you'd have to guess to proceed — an unidentified referent, an unknown win
   condition — present and ask instead of running; do not fabricate it to unlock the fast path.

When the recommended prompt is an **alternative** (a reinterpretation of intent), the fast
path *also* requires the recommendation to be **high-confidence**; a low-confidence branch
win falls back to presenting, not auto-running. Recommending the faithful main prompt
carries no extra bar.

When the conditions hold, print everything above, add a one-line note stating which prompt
you're running and why — the model and effort already match the recommendation, and, for an
alternative, why it beats the main — then execute that prompt directly.

**Otherwise, present** for the user to run elsewhere, in this order: the **main sharpened
prompt** (fenced, ready to copy) · the 2–3 adjacent options (fenced, each with its why) ·
the recommendation plus its **run line** — model + effort + escalate-or-not call · one
bullet per move you changed, saying what and why · any focused **clarifying question(s)**
for load-bearing blanks from step 2. Lead with the main sharpened prompt; keep the rest brief.

*Done when:* the main sharpened prompt and the adjacent options have been printed (fenced)
in every case; any load-bearing clarifying questions from step 2 are surfaced alongside; and
either the recommended prompt was executed in this session under a one-line rationale (fast
path, with the high-confidence bar met if it was an alternative and no blocking blank open),
or the presentation parts are shown with the main sharpened prompt first.

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
