---
name: harness-plan-work
description: Create a repository-grounded execution plan with acceptance evidence and autonomy boundaries. Use when a software goal is multi-step, ambiguous, likely to span hours, crosses harness planes, or needs a durable plan that agents can execute without relying on chat context.
---

# Harness Plan Work

Read [`../harness/references/contracts.md`](../harness/references/contracts.md) and
[`../harness/references/composition.md`](../harness/references/composition.md).

## 1. Ground the goal

Read the repository map, domain language, architecture, originating issue/spec, relevant
decisions, harness manifest, and current state. Identify ambiguous product judgments and
missing capabilities before prescribing code. Freeze the planning baseline (ref/commit),
dirty state, and maximum authorized risk class so the plan cannot silently expand them.

Completion criterion: goal, non-goals, current behavior, constraints, and source-of-truth
paths are explicit; unresolved decisions are visible.

## 2. Wrap the planning method

Use an installed Matt Pocock capability where it fits:

- `grill-with-docs` or `grilling` for fuzzy intent;
- `domain-modeling` for terminology or boundary ambiguity;
- `to-spec` for a product/behavior contract;
- `wayfinder` for investigation-heavy work;
- `to-tickets` for tracer-bullet decomposition.

Retain harness responsibility for capability prerequisites, risk classes, evidence, and
artifact placement. If no preferred capability is available, use the same narrow sequence
directly.

The planning workflow's maximum class is R1. Inspect a specialist's mutation boundary
before invoking it. When `to-spec`, `to-tickets`, or another helper would publish issues,
labels, or external state, use its reasoning locally or in chat and record the R2 action as
a future human gate; do not publish from this skill.

Completion criterion: the chosen method matches the uncertainty instead of mechanically
creating a plan-shaped document.

## 3. Build the execution contract

Use [`assets/execution-plan.md.template`](assets/execution-plan.md.template). Adapt its
headings to repository convention while preserving its contract: ordered milestones,
observable completion criteria, dependency edges, touchpoints, verification commands,
runtime evidence, rollback, and escalation points. Include progress and decision logs for
multi-hour work. Make the first milestone a thin end-to-end tracer where possible.

Planning is R0 unless the user authorized writing a plan file (R1). A plan may describe
later R2–R4 work, but it must place an explicit human gate before that action.

Completion criterion: another agent can start the first milestone, determine when every
milestone is done, and identify every human decision without reconstructing chat history.

## 4. Validate and hand off

Check the plan against repository standards, current commands, dirty state, and harness
capabilities. Trace every acceptance criterion to at least one planned evidence source;
mark unavailable runtime proof and missing prerequisites explicitly. Return the plan
location or in-chat plan, unknowns, prerequisite harness work, and the highest authorized
risk class.

Completion criterion: another agent can execute the first milestone without chat history,
and no acceptance criterion, authorization boundary, or rollback path is implicit.
