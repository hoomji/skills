# Status-summary design

- State: Verified
- Owner: Example maintainers
- Last verified: 2026-08-13
- Verification evidence: `src/status_summary.py`, `src/app.py`, `tests/test_status_summary.py`, `tests/test_app.py`, `scripts/check.py`
- Review trigger: changes to status precedence, input/output contracts, dependency direction, or runtime evidence
- Product specification: [`../product-specs/status-summary.md`](../product-specs/status-summary.md)
- Related decision: [`ADR-0001`](../adr/0001-pure-summary-core.md)

## Context

The example needs one small but complete workflow that agents can understand, change, run,
observe, and verify without credentials or shared infrastructure.

## Goals

- Keep summary behavior deterministic and easy to test.
- Make invalid boundary input fail explicitly.
- Emit structured runtime evidence carrying a worktree-derived task namespace.
- Preserve a dependency direction that can be checked mechanically.

## Non-goals

- Demonstrating a persistent server, database, frontend, or production integration.
- Generalizing the status model beyond the product specification.
- Replacing ADR-0001's record of why the pure-core decision was accepted.

## Design

`src/status_summary.py` owns domain values and the pure summary calculation.
`src/app.py` is the adapter: it parses JSON-like input, invokes the domain function, and
emits newline-delimited JSON.

```text
input -> adapter validation -> pure summary -> structured output
```

The domain module uses only the Python standard library and does not import adapters,
scripts, or tests. Unexpected states fail at the adapter boundary instead of being
silently coerced.

## Alternatives

A persistent HTTP service would provide a richer runtime surface, but would add ports,
process lifecycle, and isolation concerns unrelated to this tracer. Embedding parsing in
the domain function would reduce files but weaken the boundary and make invalid-input
behavior harder to distinguish.

## Failure and operational behavior

Validation failures are explicit and testable. The finite self-check requires no teardown
or shared mutable service. Task namespaces derive from worktree paths so concurrent runs
can be distinguished.

## Verification

Behavior tests verify precedence and validation. Adapter tests verify structured output.
`scripts/check.py` verifies the protected dependency direction. The design remains
`Verified` only while those evidence paths agree with this document.
