# External references

| Source | Retrieved | Consumer | Local-copy reason |
| --- | --- | --- | --- |
| [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) | 2026-08-13 | This example's repository knowledge, legibility, enforcement, autonomy, and hygiene flow | Preserve a bounded, repository-visible interpretation through this example |
| [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents) | 2026-08-13 | Optional orchestration, guardrail, tracing, and evaluation extension points | Clarify that an agent runtime can complement but does not replace repository harness contracts |

## Sourced observations

OpenAI describes an agent-first repository where humans design environments and feedback loops, repository knowledge is the system of record, runtime state is legible to agents, important architecture is mechanically enforced, and recurring cleanup limits entropy.

The Agents SDK offers a code-first agent loop with tools, orchestration, state, guardrails, tracing, and evaluation. Applications still own deployment, tool implementation, storage, and approval decisions.

## Repository interpretation

This example translates those ideas into a portable capability model. Its exact file tree, nine-plane vocabulary, manifest schema, risk classes, and sample application are repository-authored decisions, not representations of OpenAI's private implementation.

## Freshness

Review on material source changes, example-contract changes, or by 2027-08-13.
