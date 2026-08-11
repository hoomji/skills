---
name: harness
description: Route harness-engineering work for repositories. Use when the user wants to assess agent readiness, bootstrap agent guidance, improve repository legibility or enforcement, run an evidence-backed engineering lifecycle, capture repeated corrections, or maintain harness quality.
---

# Harness

Choose the narrowest harness skill that completes the requested job. Read
[`references/contracts.md`](references/contracts.md) when the task creates or consumes
harness artifacts. Read [`references/composition.md`](references/composition.md) when a
workflow can wrap an installed Matt Pocock engineering skill.

## Route

| Request | Skill |
|---|---|
| Audit a repository without changing it | `harness-assess` |
| Prepare the first agent-ready repository setup | `harness-bootstrap` |
| Improve one weak harness plane | `harness-deepen` |
| Turn a repeated rule into a mechanical check | `harness-encode-invariant` |
| Make UI, logs, metrics, traces, or runtime state inspectable | `harness-expose-runtime` |
| Turn a goal into an execution plan | `harness-plan-work` |
| Implement and verify a repository change | `harness-deliver-work` |
| Review a change against its spec and evidence | `harness-review-evidence` |
| Convert human correction into a durable improvement | `harness-capture-learning` |
| Find stale, broken, or conflicting harness artifacts | `harness-garden` |
| Report capability levels and trends | `harness-quality-report` |

If the request crosses several rows, begin with assessment or planning and name the
later skills as follow-on phases. Keep setup incremental: improve the capability that
blocks a real tracer workflow before adding broader machinery.

## Boundary

Treat Codex as the primary surface. Keep shared repository guidance agent-neutral in
`AGENTS.md`; use a minimal `CLAUDE.md` pointer for Claude Code. Prefer repository-local
skills and artifacts. Defer plugin packaging until the contracts work in both
`Uniblock-dev/unified-request` and `Uniblock-dev/auto-route`.
