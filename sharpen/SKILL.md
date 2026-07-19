---
name: sharpen
description: Rewrite a rough prompt into a sharper one and recommend the model and effort level to run it at. User-invoked — type /sharpen with the prompt to improve.
disable-model-invocation: true
---

# Sharpen

Take a rough prompt and return a sharper one, plus the model and effort to run it
at. Apply the **same five moves every run** — the rewrite is a fixed process, not
improvised, so the same weak prompt gets sharpened the same way each time.

The prompt to sharpen is whatever the user passes in, or the most recent prompt
they're pointing at. If nothing is supplied, ask for the prompt (or a description
of what they were trying to get Claude to do).

## Steps

### 1. Diagnose against all five moves
Assess the prompt against **every** move in the reference below — not just the
first weakness you spot. For each move, note: present, missing, or misapplied.

*Done when:* all five moves are assessed and the specific weaknesses named.

### 2. Mark the blanks
A rewrite must never invent the user's private context. Wherever a fix needs
something only the user knows — the **referent** (which file / PR / range), the
**why**, the **win condition**, or a **load-bearing constraint** — leave a
`[bracketed blank]` for them to fill instead of guessing a value.

*Done when:* every fix that depends on private context is a bracket, not a fabrication.

### 3. Rewrite
Produce the sharpened prompt carrying every fix from step 1 and every blank from
step 2. Keep the user's voice and intent; change what the moves require and nothing
more.

*Done when:* the rewrite reflects every weakness found and adds nothing the moves don't call for.

### 4. Recommend model and effort
Apply the decision rule in the reference below.

*Done when:* one model and one effort level are named, each with a one-line why.

### 5. Present
Show, in this order: the **sharpened prompt** (fenced, ready to copy) · one bullet
per move you changed, saying what and why · the **model + effort** line. Lead with
the sharpened prompt; keep the rest brief.

*Done when:* all three are present and the sharpened prompt is first.

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

## Model and effort — reference

For current model IDs, pricing, effort levels, and behavioral specifics, consult the
`/claude-api` skill — it is the source of truth and stays current. The decision rule
here is stable:

**Model.** Default to the **daily driver** (Opus 4.8): cheaper, faster, and it handles
almost everything. Reach for the **heavyweight** (Fable 5) only when the task is hard,
long-horizon, and well-specified enough to run autonomously, and its higher cost and
minutes-long turns are acceptable. Stay on the daily driver for anything routine,
latency-sensitive, interactive, or cyber/bio-adjacent — the heavyweight refuses those.

**Effort.** Default `high`. Use `xhigh` for coding and agentic work; `max` only when
correctness outweighs cost; `low`/`medium` for routine or latency-sensitive tasks.
The heavyweight's `low` roughly matches older models' `high`, so start lower than
instinct. When the right level is unclear, say so and suggest a two-level sweep.

**Prompt-to-model fit.** Match the rewrite's altitude to the chosen model — the
stronger the model, the higher you fly. For the heavyweight, de-prescribe further,
add the why, grant autonomy and parallelism, and set one boundary (it over-reaches).
For the daily driver, add explicit triggers and an autonomy grant (it under-reaches:
it asks a lot and won't reach for tools, subagents, or memory unless told).
