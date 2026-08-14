---
name: harness-deliver-work
description: Deliver a repository change through baseline, implementation, verification, and evidence-backed review. Use when the user wants an existing spec, issue, or plan implemented using the repository harness while composing installed debugging, TDD, implementation, merge-conflict, and review skills.
---

# Harness Deliver Work

Read [`../harness/references/contracts.md`](../harness/references/contracts.md) and
[`../harness/references/composition.md`](../harness/references/composition.md).

## 1. Establish the contract

Resolve the originating goal/spec, acceptance criteria, repository guidance, dirty state,
verification commands, risk ceiling, and required runtime evidence. Use `harness-plan-work`
first when the change lacks an executable contract.

When the contract is an ExecPlan slice, that file is the whole brief: execute it from the
slice and the working tree without reading the parent plan or sibling slices. Treat a slice
that cannot be executed on those terms as an authoring defect and return it to
`harness-exec-plan` rather than reconstructing the missing context from elsewhere. Respect
its out-of-scope list — record adjacent defects in the Execution Record and escalate them
instead of fixing them here.

Completion criterion: scope and done conditions are checkable; user-owned changes and
unauthorized actions are protected.

Read the relevant domain glossary and use its canonical terms in code, tests, and handoff
evidence. Route a newly resolved meaning or contradiction through `harness-model-domain`;
do not silently let implementation invent a competing vocabulary.

Read ADRs relevant to the touched boundary. If delivery would contradict an accepted
decision, stop that implementation path and route the trade-off through
`harness-record-decision`; do not silently treat the code change as supersession.

## 2. Select the specialist

Wrap the installed Matt Pocock skill matching the work:

- `diagnosing-bugs` before modifying a poorly understood failure;
- `tdd` for behavior changes and bug fixes that need a red/green loop;
- `implement` for execution from an established spec;
- `resolving-merge-conflicts` for an active merge or rebase conflict.

Do not restate the specialist’s method. Supply it with the repository contract, then
resume this harness lifecycle with its artifacts and evidence.

Completion criterion: the selected specialist owns the actual change method and every
modified behavior traces to an acceptance criterion.

## 3. Verify in layers

Run the narrowest relevant checks during iteration, then the repository gate. Exercise
UI, logs, metrics, traces, or performance paths required by the acceptance criteria.
Separate product failure, repository failure, environment failure, and skipped evidence.

Completion criterion: every acceptance criterion has reproducible evidence or an explicit
unverified status and reason.

## 4. Review and repair

Wrap `code-review` against both repository standards and the originating spec. Repair
actionable findings and rerun affected checks. Classify repeated corrections for
`harness-capture-learning` without expanding the requested implementation scope.

Completion criterion: no unresolved correctness or spec finding remains inside the
authorized scope; judgment calls are escalated.

## 5. Hand off

Return the shared evidence bundle. Perform branch, commit, push, PR, merge, or deploy
actions only when the user authorized that risk class. Otherwise leave a reviewable local
change set and exact next commands.
