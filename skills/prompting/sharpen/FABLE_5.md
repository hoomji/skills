# Prompting Claude Fable 5

Read this only after selecting Fable 5. Apply the smallest relevant subset to the
sharpened prompt.

Source: [Anthropic's Claude Fable 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)

## Prompt adaptations

- Give the larger purpose and what the result enables. Fable uses the reason to
  connect work across a long run.
- Grant autonomy once enough information exists. Define the genuine pause
  conditions: irreversible action, real scope change, or user-only input.
- State the action boundary. Distinguish assessment from implementation and name
  state-changing actions that require evidence or approval.
- Constrain scope at high effort. Ask for the simplest complete solution and name
  whether adjacent refactoring, abstractions, compatibility layers, or speculative
  validation belong in scope.
- For long runs, require progress and completion claims to cite tool evidence.
  Require explicit disclosure of failed checks, skipped steps, and unverified work.
- Delegate independent work when parallelism materially helps. Prefer a fresh
  verifier for long-running work and state what the verifier checks against.
- Name the durable memory location when future runs should retain lessons. Store
  corrections and confirmed approaches without duplicating repository facts.
- Lead user-facing updates with the outcome. After a long unattended run, make the
  final response self-contained and reintroduce any necessary terminology.
- Ask for execution rather than reproduced internal reasoning. Use verification
  artifacts and concise rationale when reasoning visibility is needed.

For an asynchronous run, provide non-blocking progress delivery and instruct the
model to finish reversible in-scope work before ending.
