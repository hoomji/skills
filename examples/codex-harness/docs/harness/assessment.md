# Initial harness assessment

- Assessment type: illustrative read-only baseline
- Scope: `examples/codex-harness/` at the reviewed commit
- Tracer: status-summary behavior change
- Assessor: Example maintainers
- Date: 2026-08-13

This file demonstrates the expected assessment shape. It is not evidence about another repository.

| Plane | Level | Confidence | Present capability | Gap / next capability | Evidence |
| --- | --- | --- | --- | --- | --- |
| Intent | 3 verifiable | High | Product spec maps behavior to tests | Add change-history evidence after real iterations | `docs/product-specs/status-summary.md` |
| Knowledge | 3 verifiable | High | Map, language, architecture, indexed design docs, ADRs, operations | Measure cold-start navigation with independent agents | `AGENTS.md`, `CONTEXT.md`, `ARCHITECTURE.md`, `docs/design-docs/index.md` |
| Execution | 3 verifiable | High | Standard-library setup/start/check/test commands | None for tracer | `scripts/` |
| Feedback | 3 verifiable | High | Tests and structured runtime output | Add UI/metrics/traces only for a tracer that needs them | `tests/`, `docs/operations/observability.md` |
| Policy | 4 enforced | Medium | Dependency and harness contracts fail mechanically | Add policies only from repeated failures | `scripts/check.py`, `scripts/harness-validate.py` |
| Isolation | 1 documented | High | Worktree namespace contract exists | Prove namespaced services when a persistent runtime exists | `docs/operations/isolation.md` |
| Lifecycle | 2 executable | Medium | Artifact flow and stable commands exist | Trial the full flow on a real PR | `docs/harness/lifecycle.md` |
| Hygiene | 2 executable | Medium | Garden and quality commands exist | Add trend history after repeated runs | `scripts/garden.py`, `scripts/quality_report.py` |
| Governance | 1 documented | High | Risk and escalation contract exists | Integrate repository-host permissions before R2 work | `docs/harness/governance.md` |

## Ranked next capabilities

1. Trial the tracer through an independently reviewed pull request.
2. Record quality trends across repeated runs.
3. Add persistent-runtime isolation and observability only when a real workflow requires them.

## Risk boundary

The example proves R0 and R1 behavior. It documents but does not execute R2 through R4 actions.
