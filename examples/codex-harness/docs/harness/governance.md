# Governance and autonomy

## Risk classes

| Class | Examples | Default |
| --- | --- | --- |
| R0 | Read files, inspect history, run read-only queries | Autonomous within scope |
| R1 | Edit files, run tests, create isolated worktrees | Autonomous with evidence and recovery |
| R2 | Push branch, open draft PR, update non-production issue | Explicit workflow authorization and audit |
| R3 | Merge, staging deploy, shared test-data mutation | Explicit gate and tested recovery |
| R4 | Production, destructive migration, secrets, policy change | Human approval at action time; normally out of scope |

## Mandatory escalation

Stop when:

- product authorities conflict or a value judgment is unresolved;
- evidence cannot distinguish success from failure;
- credentials or permissions exceed the requested workflow;
- an action is destructive, irreversible, or production-facing;
- a protected invariant needs an exception;
- recovery is absent or untested;
- private, customer, regulated, or secret data would enter an inappropriate artifact.

## Autonomy ladder

1. **Observe:** R0 discovery is reproducible.
2. **Assist:** R1 work succeeds manually with evidence.
3. **Repeat:** the exact R1 workflow is isolated and reliably repeatable.
4. **Schedule:** read-only recurrence is quiet; mutating recurrence has prior manual proof and isolation.
5. **Publish:** R2 actions have explicit authority and audit.
6. **Consequential action:** R3/R4 gates remain specific and human-controlled.

Never promote autonomy because a different workflow is mature.
