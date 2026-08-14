---
name: status-summary
description: Deliver a change to the example status-summary behavior from product intent through reproducible evidence. Use when modifying check parsing, aggregate-state rules, structured output, or their tests.
---

# Status Summary

1. Read `CONTEXT.md`, `ARCHITECTURE.md`, `docs/design-docs/status-summary.md`, and `docs/product-specs/status-summary.md`.
2. Update the active ExecPlan when the change has multiple dependent steps or decisions.
3. Add or revise an acceptance test before changing behavior.
4. Keep domain calculation pure and boundary validation explicit.
5. Run `python scripts/check.py`, then `python scripts/test.py`.
6. Run `python scripts/start.py` when output shape or observability changes.
7. Record results using `docs/harness/evidence-template.md`.
8. Stop before shared-state, deployment, secret, or policy actions without explicit authorization.
