# Teaching Notes — preferences & working notes

## How Henry wants to be taught
- **Start from basics** (he said "assume I don't know the basics yet") — but he's a heavy, sophisticated Claude Code user with a whole LLM-maintained wiki system. Build the floor, don't patronize. Move briskly.
- Ground every lesson in his real work: steering Claude Code, and authoring skills / system prompts / `CLAUDE.md`-style instruction files.
- Lessons short, one tangible win each.

## Context about Henry
- Works at Uniblock (blockchain unified-request API company), email henry.tran@uniblock.dev.
- Uses Claude Code daily; has many custom skills and a work + personal Obsidian wiki maintained by Claude.
- Current session model: Opus 4.8.

## Pedagogy reminders (from the teach skill)
- Split fluency vs storage strength; build storage via retrieval, spacing, interleaving.
- Quiz answers: same word count (ideally same char count) across options — no formatting tells.
- Each lesson: cite a primary source, link to reference docs + other lessons, remind Henry he can ask the teacher (me) follow-ups.

## Real examples to reuse in lessons
- Henry works with **S3-stored VCR-style "cassettes"** (recorded HTTP interactions / provider responses replayed in tests). Keeping them fresh, plus analytics/processing over them, is a live concern — good grounding for lessons on decomposition, decision-framing, and agentic file-reading prompts.

## Course-specific decisions
- "Fable" here = **Claude Fable 5**, positioned as Anthropic's most capable widely released model (frontier reasoning / long-horizon agentic). Not the default Opus upgrade — pricier. Thinking always on; prompts written for older models are often *too prescriptive* for it.
- Model facts sourced from the in-repo `claude-api` skill (authoritative, current) — NOT parametric memory.
