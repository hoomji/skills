---
name: harness-expose-runtime
disable-model-invocation: true
description: User-invoked only. Make one runtime surface directly inspectable and verifiable by coding agents. Use when agents cannot reproduce or prove UI behavior, query task-local logs, inspect metrics or traces, check performance, observe database state, or safely exercise an external API during engineering work.
---

# Harness Expose Runtime

## Invocation

Run only when the user explicitly invokes this skill by name (for example,
`$harness-expose-runtime` in Codex or `/harness-expose-runtime` in Claude Code). A matching task or a reference from another skill is not an
invocation. References to other harness skills below are recommendations; run
those skills only when the user explicitly invokes them as well. Continue the
authorized task directly when a recommended skill has not been invoked.

Read [`../harness/references/contracts.md`](../harness/references/contracts.md). Expose one
surface that closes one concrete feedback loop.

## 1. Define the observation

Name the tracer workflow, question the agent must answer, source of truth, data sensitivity,
freshness, and required environment. Classify read and mutation paths separately.

Completion criterion: a successful observation has a reproducible input and an objective
signal; secret, production, and destructive boundaries are explicit.

## 2. Choose the narrow interface

Prefer an existing CLI, browser surface, log query, metrics query, trace search, fixture,
or typed SDK. Add a script or connector only when it removes a repeated manual loop. Make
worktree/task identity visible in ports, data, logs, and teardown where concurrency matters.

Completion criterion: the interface exposes only the minimum state required for the
question and has a safe failure mode.

## 3. Implement a closed loop

Add setup, one representative query or drive path, expected evidence, and teardown.
Demonstrate failure and success when feasible. Keep credentials outside tracked files and
report environment limits separately from application failure.

Completion criterion: an agent can reproduce the observation from repository guidance
and distinguish pass, fail, and unavailable states.

## 4. Record and hand off

Update feedback/isolation evidence in the manifest. Return the shared evidence bundle,
access boundary, cost/retention implications, and next useful runtime surface.
