# Design documentation

This index is the authoritative catalogue of system and feature design documents. Design
docs explain how and why a design works; [`../adr/index.md`](../adr/index.md) separately
records discrete architectural decisions.

| Design | State | Owner | Last verified | Evidence | Related authorities |
| --- | --- | --- | --- | --- | --- |
| [Core beliefs](core-beliefs.md) | Verified | Example maintainers | 2026-08-13 | `AGENTS.md`, `scripts/harness-validate.py` | [`ARCHITECTURE.md`](../../ARCHITECTURE.md) |
| [Status-summary design](status-summary.md) | Verified | Example maintainers | 2026-08-13 | `src/status_summary.py`, `tests/test_status_summary.py`, `scripts/check.py` | [Product spec](../product-specs/status-summary.md), [ADR-0001](../adr/0001-pure-summary-core.md) |

A proposed design is not evidence of current behavior. Verification compares its claims
with the linked implementation, tests, or operational evidence.
