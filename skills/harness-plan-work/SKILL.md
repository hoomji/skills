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
missing capabilities before prescribing code.

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

Completion criterion: the chosen method matches the uncertainty instead of mechanically
creating a plan-shaped document.

## 3. Build the execution contract

Define ordered milestones with observable completion criteria, dependency edges, target
files or seams, verification commands, runtime evidence, rollback, and escalation points.
Include a progress log and decision log for multi-hour work. Make the first milestone a
thin end-to-end tracer where possible.

Completion criterion: another agent can start the first milestone, determine when every
milestone is done, and identify every human decision without reconstructing chat history.

## 4. Validate and hand off

Check the plan against repository standards, current commands, dirty state, and harness
capabilities. Return the plan location or in-chat plan, unknowns, prerequisite harness
work, and the highest authorized risk class.
