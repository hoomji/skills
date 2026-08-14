# OpenAI: Harness engineering

## Provenance

- **Title:** Harness engineering: leveraging Codex in an agent-first world
- **Source:** https://openai.com/index/harness-engineering/
- **Publisher:** OpenAI
- **Author:** Ryan Lopopolo
- **Published:** 2026-02-11
- **Retrieved:** 2026-08-13
- **Owner:** Repository maintainers
- **Local-copy reason:** Preserve a concise, versioned summary of the external article that motivates and informs this repository's harness-engineering workflows without depending on browser context.
- **Repository consumers:** `skills/harness/` and its documentation in `docs/`.

## Sourced summary

OpenAI describes *harness engineering* as shifting engineers' leverage from directly writing code to designing the environment, repository knowledge, tools, constraints, and feedback loops that let coding agents work reliably.

The article presents these relevant practices:

- Keep the repository knowledge base structured and versioned in `docs/`; use a short agent entrypoint as a map rather than a monolithic instruction manual.
- Make runtime behavior directly inspectable by agents, including the UI, logs, metrics, traces, and isolated worktree environments.
- Encode architectural boundaries and recurring quality expectations mechanically with linters, structural tests, and actionable feedback.
- Capture review feedback and operational lessons as durable documentation or enforcement, then run recurring maintenance to limit drift.
- Treat increasing autonomy as dependent on repository-specific investments in validation, review, recovery, and escalation paths—not as a default property of an agent.

## Repository inference

This repository's `harness` skills operationalize the same broad approach: make intent, knowledge, execution, verification, and maintenance legible and enforceable for coding agents. This source is background material, not a normative specification for the workflows.

## Freshness

Review this note when the linked article changes materially, when `skills/harness/` changes its operating model, or by 2027-08-13.
