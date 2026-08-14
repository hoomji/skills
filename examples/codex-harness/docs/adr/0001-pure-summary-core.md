# ADR-0001: Pure status-summary core

- State: Accepted
- Date: 2026-08-13
- Owners: Example maintainers

## Context

The example needs observable behavior without introducing network, datastore, dependency-installation, or teardown complexity. It must also demonstrate a boundary between product logic and runtime adapters.

## Decision

Implement summary calculation as a pure function over validated immutable values. Keep JSON parsing, CLI exit behavior, worktree namespace calculation, and structured logging in the adapter layer.

## Consequences

- Domain behavior is deterministic and easy to test.
- Runtime evidence can be produced without shared services.
- Boundary errors remain explicit.
- The example does not demonstrate a persistent server; repositories that need UI, logs, metrics, traces, databases, or external APIs must add those surfaces for a real tracer.

## Enforcement

`python scripts/check.py` rejects imports from `scripts` or `tests` inside `src/status_summary.py`. Behavioral tests cover precedence and validation.
