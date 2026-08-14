# OpenAI Agents SDK

## Provenance

- **Title:** Agents SDK
- **Source:** https://developers.openai.com/api/docs/guides/agents
- **Publisher:** OpenAI
- **Documentation version:** Live documentation; no page version is published
- **Retrieved:** 2026-08-13
- **Owner:** Repository maintainers
- **Local-copy reason:** Preserve a concise, versioned orientation to the optional OpenAI agent runtime capabilities relevant to harness orchestration, tools, state, guardrails, observability, and evaluation without relying on browser context.
- **Repository consumers:** `skills/harness/` and the [harness engineering product specification](../product-specs/harness-engineering-system.md).

## Sourced summary

OpenAI describes agents as applications that plan, call tools, collaborate across specialists, and retain enough state to complete multi-step work. The Agents SDK is the code-first path in which an application owns deployment, tool implementations, state storage, and approval decisions while the SDK runs the agent loop and invokes tools.

The guide identifies these major capability areas:

- define agents and select models and providers;
- run agent loops with streaming and continuation strategies;
- use container-based sandbox agents when work needs files, commands, packages, mounts, snapshots, or provider links;
- orchestrate specialists and handoffs;
- add guardrails and human review around risky work;
- consume final output, resumable state, and next-turn results;
- connect hosted tools, function tools, and MCP servers;
- inspect traces and evaluate agent workflows;
- build voice-agent workflows where applicable.

The guide recommends the Agents SDK when an application wants typed TypeScript or Python code, direct control over tools and MCP servers, custom state or conversation storage, and tight integration with product infrastructure. It distinguishes this from the Responses API: use the Responses API when the application should own the loop, and the Agents SDK when the SDK should run it.

## Repository inference

The Agents SDK could implement parts of a harness-backed runtime, such as specialist orchestration, tool invocation, approval pauses, tracing, and evaluations. It does not by itself supply repository-local product intent, authoritative knowledge, deterministic development commands, policy ownership, risk classification, or evidence contracts. Those remain responsibilities of the harness system.

The SDK is therefore an optional integration surface, not a required dependency or the product architecture selected by this repository.

## Freshness

Review this note when OpenAI materially changes the linked overview, when the harness system adopts the Agents SDK, when the SDK's ownership of loops or state changes, or by 2027-08-13.

