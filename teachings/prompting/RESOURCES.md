# Prompting Resources

High-trust sources for this workspace. Knowledge for lessons is drawn from here,
not from parametric guesses.

## Knowledge

- [Anthropic — Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
  The canonical guide. Use for: the core technique ladder (be clear & direct, examples, chain-of-thought, roles, prefill, chaining, long-context tips).
- [Anthropic — Be clear, direct, and detailed](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/be-clear-and-direct)
  The single most important beginner technique. Use for: Lesson 1.
- [Anthropic — Use examples (multishot / few-shot)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/multishot-prompting)
  Use for: designing few-shot examples that actually steer behavior.
- [Anthropic — Let Claude think (chain of thought)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/chain-of-thought)
  Use for: when/how to elicit reasoning (and why it's different on always-thinking models).
- [Anthropic — Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
  Use for: forcing JSON/schema output (the modern replacement for assistant prefill).
- [Anthropic — Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)
  Use for: steering agentic coding sessions, `CLAUDE.md` files, planning.
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/skills)
  Use for: authoring skills — structure, `SKILL.md`, progressive disclosure.
- **In-repo `claude-api` skill** (`/claude-api`)
  Authoritative, current model facts + Anthropic's own model-specific prompting guidance (Opus 4.7/4.8, Fable 5, Sonnet 5). Use for: anything about a specific model's behavior, effort levels, or migration-era prompt tuning. **Trust this over memory for model claims.**

## Wisdom (Communities)

- [r/ClaudeAI](https://www.reddit.com/r/ClaudeAI/) and [r/ClaudeCode](https://www.reddit.com/r/ClaudeCode/)
  Active practitioner communities. Use for: real-world prompt/skill critique, seeing how others steer agentic sessions. (Signal-to-noise varies — treat as field notes, not doctrine.)
- [Anthropic Discord](https://www.anthropic.com/discord)
  Use for: closer-to-source discussion, builder Q&A.

## Gaps
- No single canonical "prompting for agentic coding" long-form guide beyond the best-practices post; may need to synthesize from that + community.
- Fable-5-specific public prompting guidance is thin outside the in-repo skill's migration notes — lean on those and Henry's own experiments.
