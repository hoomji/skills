# Execution plans

Lifecycle index for this example's ExecPlans. Every plan appears in exactly one section
and lives in exactly one directory: `active/` or `completed/`.

## Active

| Plan | Goal | Current milestone | Owner | Updated |
| --- | --- | --- | --- | --- |
| [Status summary](active/status-summary.md) | Deliver the status-summary tracer end to end | Verification | Example maintainers | 2026-08-13 |

## Completed

No plan has completed yet. See [the completed-plan contract](completed/README.md) for the
review a plan must pass before it moves here.

| Plan | Outcome | Evidence | Completed |
| --- | --- | --- | --- |

## Entry contract

- A new plan is created at `active/<slug>.md` and added to the Active table in the same
  change.
- A plan moves to `completed/` only when its promised behavior and acceptance evidence
  exist; the same change moves its row to the Completed table.
- A plan is never listed in both tables and never exists in both directories.
- Debt discovered while executing a plan is recorded in
  [`tech-debt-tracker.md`](tech-debt-tracker.md), not left in the plan.
