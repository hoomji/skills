# Prompting Claude Opus 5

Read this only after selecting Opus 5. Apply the smallest relevant subset to the
sharpened prompt.

Source: [Anthropic's Claude Opus 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

## Prompt adaptations

- Ask for the response length you want. Opus 5 answers at length by default, and
  effort tunes thinking rather than visible output, so state the target when brevity
  matters.
- Calibrate the length of written deliverables. Files the model writes to disk run
  long; say to cover the substance without filler sections or redundant summaries.
- Name the progress-update contract for agentic work. Give the cadence and shape —
  one sentence before the first tool call, a brief update on a real finding or a
  change of direction, outcome first at the end.
- Leave verification to the model. Strip instructions to verify, re-check, or
  double-check, and strip verify-with-a-subagent steps — Opus 5 already does this,
  and the instruction only buys over-verification.
- State the scope on a narrow task. Say to deliver what was asked at the intended
  scope, to raise a concern in a sentence rather than reshape the work around it, and
  to finish the whole task.
- Bound delegation when the harness has subagents. Opus 5 delegates readily, so name
  the cases that earn it — large, genuinely independent, parallelizable tracks — and
  keep spawn counts low.
- Limit correction narration in a user-facing product. Correct an earlier statement
  only when the error changes the reader's code, conclusions, or decisions.
- Give a long-horizon task its full specification up front. Opus 5 is strongest run
  end to end from one complete spec, so prefer that over a spec revealed turn by turn.
- Give vision work tools to crop, analyze, and visually verify. Tool use buys more
  here than added thinking, and prompt-side workarounds written for older models are
  often dead weight.
- Ask a code review for full coverage, with confidence and severity per finding, and
  filter in a later pass. A stated severity bar is followed literally and suppresses
  real findings.

When thinking must stay off, prefer `low` effort with thinking on instead. If it
genuinely cannot, add that the model may speak briefly before a tool call, should say
so when no tool fits the ask, and should keep internal or system XML tags out of the
response.
