# Prompting Claude Opus 4.8

Read this only after selecting Opus 4.8. Apply the smallest relevant subset to the
sharpened prompt.

Source: [Anthropic's Claude Opus 4.8 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8)

## Prompt adaptations

- State scope literally, including whether an instruction applies to one item or
  every item. Put the task, intent, and relevant constraints in the first prompt
  when autonomy or token efficiency matters.
- Explicitly trigger tools when the task depends on retrieval, inspection, or
  execution. State why the tool is needed and what evidence it should obtain.
- Explicitly trigger subagents when useful. Reserve them for genuine fan-out such
  as independent items or multiple files; keep directly visible work local.
- Specify desired response length or voice only when the output depends on it.
  Prefer positive examples over lists of unwanted tendencies.
- Let normal progress updates happen naturally. Specify cadence, content, or
  examples only when the product needs a particular update contract.
- For frontend work, either provide a concrete visual direction or ask for several
  distinct directions before implementation. Generic aesthetic adjectives do not
  reliably override the model's house style.
- For code review, separate finding from filtering when recall matters. Ask for
  broad coverage with confidence and severity, then verify or rank findings in a
  later pass; otherwise define the reporting threshold concretely.

At `xhigh` or `max`, allow a large output budget for tool and subagent work.
Adaptive thinking must be enabled separately when the harness uses it.
