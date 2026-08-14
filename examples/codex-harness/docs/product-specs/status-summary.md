# Status summary

## Document control

- State: Active
- Owner: Example maintainers
- Created: 2026-08-13
- Review trigger: Aggregate-state, accepted-state, or output-contract changes
- Related decision: [`../adr/0001-pure-summary-core.md`](../adr/0001-pure-summary-core.md)
- Delivery plan: [`../exec-plans/active/status-summary.md`](../exec-plans/active/status-summary.md)

## User and problem

Repository automation needs one deterministic summary of several checks. Callers should not reimplement precedence rules or guess whether missing evidence means health.

## Outcome

Given ordered named check results, return a serializable status summary with an aggregate state, total counts, and the ordered names of failed and unknown checks.

## Required behavior

- Accept only non-empty names and the states `pass`, `fail`, and `unknown`.
- Reject malformed input at the boundary with an actionable error.
- Produce `degraded` when at least one check fails.
- Otherwise produce `unknown` when at least one check is unknown or input is empty.
- Produce `healthy` only when every check passes.
- Preserve input order in `failed_checks` and `unknown_checks`.
- Produce stable JSON keys suitable for logs, tests, and downstream tooling.

## Failure behavior

- Invalid states raise `ValueError` naming the accepted values.
- Missing or blank names raise `ValueError` identifying the name constraint.
- Invalid CLI JSON exits non-zero and emits a structured error event without a traceback by default.

## Compatibility

- Python 3.11 or newer.
- Standard library only.
- Output fields are additive within version 1; removing or retyping fields requires a product-spec revision.

## Non-goals

- Running checks, service discovery, monitoring, alerting, persistence, network APIs, dashboards, or production deployment.
- Treating empty input as healthy.
- Automatically retrying failed or unknown checks.

## Acceptance criteria

1. All-pass input returns `healthy` with correct counts and empty failure lists.
2. Any failure returns `degraded`, even when unknown checks are also present.
3. Unknown input without failures returns `unknown`.
4. Empty input returns `unknown` with zero counts.
5. Failed and unknown names preserve input order.
6. Invalid state and blank name inputs fail at the boundary with actionable messages.
7. `python scripts/start.py` emits structured JSON containing `event`, `task_namespace`, and `summary`.
8. The full repository validation commands pass without third-party dependencies.

## Rollout and recovery

The feature is local and reversible. Roll back the domain module, adapter, tests, and linked documentation as one change group. Do not claim completion if any acceptance criterion lacks evidence.
