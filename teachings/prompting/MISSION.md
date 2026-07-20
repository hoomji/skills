# Mission: Prompting Opus & Fable (and the craft generally)

## Why
Henry steers Claude Code all day and authors skills, system prompts, and
instruction files (e.g. his wiki `CLAUDE.md`). He wants those to *reliably*
control Claude — fewer re-rolls, less babysitting, more first-shot correctness —
and to understand the frontier techniques most people never learn. Fable is a
secondary curiosity: knowing when to reach for it vs Opus, and how prompting
differs.

## Success looks like
- Henry can take a vague request to Claude Code and turn it into one that lands on the first try.
- Henry can write a skill / system prompt that steers Claude consistently across many runs, and debug one that doesn't.
- Henry can name *why* a prompt failed (missing context? over-prescription? wrong altitude?) rather than just retrying.
- Henry can pick Opus vs Fable deliberately and adjust his prompting to the model.
- Henry knows several intermediate/advanced techniques (few-shot design, prefill-replacements, structured output, context/altitude control, eval-driven iteration) and when each applies.

## Constraints
- Start from the basics — build the floor properly, but move briskly (Henry is a sophisticated Claude Code user; don't be condescending).
- Lessons short and quick to complete; tied to real Claude Code / skill-authoring situations, not toy examples.

## Out of scope (for now)
- Building product AI features via the Claude API (SDK code, tool-use loops). Deferrable — revisit if the mission shifts.
- Image/vision prompting, computer use.
