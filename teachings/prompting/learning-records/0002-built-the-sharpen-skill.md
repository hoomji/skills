# Built the `sharpen` skill — course operationalized

Henry asked for (and we built) a user-invoked Claude Code skill, `sharpen`
(`~/.claude/skills/sharpen/SKILL.md`), that rewrites a rough prompt and recommends
model + effort. It operationalizes the five course moves — **explicitness, decision
frame, don't lead the witness, altitude, show-don't-tell** — as a fixed diagnostic
run, plus the Lesson 5 model/effort decision rule.

Why this matters for teaching:
- Wanting to turn the lessons into a reusable tool is strong evidence the five moves
  have landed as working vocabulary (they're now the skill's leading words *and* in
  [[GLOSSARY.md]]). Reasonable to treat the core spine (L1–L5) as internalized.
- The skill is the canonical home of the moves for his day-to-day work; future
  lessons/refinements should stay consistent with its wording.
- Design choices worth remembering: user-invoked (zero context load, fires by hand);
  points to `/claude-api` for model facts rather than duplicating (single source of
  truth); leaves `[blanks]` for private context rather than fabricating intent.

Next natural teaching step is the meta-skill: **iterating/debugging prompts &
lightweight evals** — which is also how he'd refine `sharpen` itself from real use.

See [[MISSION.md]].
