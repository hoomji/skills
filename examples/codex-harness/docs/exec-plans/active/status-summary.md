# ExecPlan: status summary tracer

## Purpose

Deliver the representative status-summary behavior while demonstrating the repository's full intent-to-evidence lifecycle.

## Scope

- Product contract and canonical language
- Pure domain model and CLI adapter
- Behavior and architecture tests
- Structured runtime evidence
- Harness manifest, validation, governance, hygiene, and quality artifacts

## Non-scope

Network services, deployment, secrets, external connectors, production mutations, and auto-merge.

## Progress

- [x] Define product outcome and acceptance criteria.
- [x] Record pure-core architecture decision.
- [x] Establish deterministic commands.
- [x] Implement domain and CLI adapter.
- [x] Add behavior and structural tests.
- [x] Add manifest, governance, evidence, and maintenance surfaces.
- [ ] Move this plan to `completed/` after an independent evidence review.

## Decisions

- Use standard-library Python to keep setup deterministic.
- Use a finite CLI self-check instead of a persistent service.
- Derive the task namespace from the worktree path without writing shared state.
- Keep shared-state and production actions outside the example's automated boundary.

## Verification

- `python scripts/setup.py`
- `python scripts/start.py`
- `python scripts/check.py`
- `python scripts/test.py`
- `python scripts/harness-validate.py .`
- `python scripts/garden.py`
- `python scripts/quality_report.py`

## Recovery

All changes are repository-local R1 artifacts. Revert the example directory as one change group. No database, service, credential, or external state requires rollback.

## Open questions

None block the tracer. A real adopter must select runtime surfaces and deployment gates appropriate to its own repository.
