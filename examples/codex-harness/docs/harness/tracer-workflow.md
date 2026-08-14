# Representative workflow: add status-summary behavior

## Outcome

Change one aggregate-state rule or output field and carry it from product intent through implementation, runtime evidence, review, and durable learning.

## Preconditions and boundary

- Required local state: clean or understood worktree; Python 3.11+
- Credentials or services: none
- Maximum risk class: R1 reversible local
- Stop and escalate when: product intent conflicts, evidence is ambiguous, an external action is required, or a protected invariant needs an exception

## Flow

1. Read `CONTEXT.md`, the product spec, relevant design doc, ADR, and active ExecPlan.
2. State the desired observable behavior and acceptance criterion.
3. Add or revise a failing behavior test.
4. Make the smallest domain or adapter change.
5. Run `python scripts/check.py`.
6. Run `python scripts/test.py`.
7. Run `python scripts/start.py` when structured output changes.
8. Run `python scripts/harness-validate.py .`.
9. Complete an evidence bundle and self-review against intent and architecture.
10. Record repeated friction in the learning ledger; do not encode one-off taste.
11. Stop before branch push, PR, merge, deployment, secret access, or destructive action unless separately authorized.

## Acceptance criteria

- The changed behavior is owned by the product spec and covered by a focused test.
- The aggregate-state precedence and deterministic ordering remain intact unless the spec explicitly changes them.
- Domain dependency direction remains intact.
- Runtime output remains structured and task-namespaced.
- All completion claims map to command output or a named repository artifact.
- Residual risk and skipped checks are explicit.

## Evidence

- Focused verification: `python scripts/check.py` reports `PASS: static and structural checks`
- Repository gate: `python scripts/test.py` exits zero with all tests passing
- Runtime evidence: `python scripts/start.py` emits a `status_summary.completed` JSON event
- Harness contract: `python scripts/harness-validate.py .` reports `PASS`
- Handoff: completed `docs/harness/evidence-template.md` fields in the task or PR

## Recovery

Revert the scoped product spec, tests, implementation, and evidence changes. No external or shared runtime state is mutated.
