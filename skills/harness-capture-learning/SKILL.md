---
name: harness-capture-learning
description: Turn repeated agent friction, review corrections, failed runs, or human interventions into the narrowest durable repository improvement. Use when the same mistake recurs, a workflow needed hidden knowledge, or feedback should compound into guidance, documentation, a skill, a script, enforcement, tooling, or an explicit decision not to encode.
---

# Harness Capture Learning

Read [`../harness/references/contracts.md`](../harness/references/contracts.md).

## 1. Capture the episode

Record the observed behavior, expected behavior, evidence, frequency, impact, and task
context. Distinguish one-off preference from a repeated or high-impact capability gap.

Completion criterion: the episode is concrete enough that another maintainer could
recognize its recurrence.

## 2. Diagnose the missing plane

Classify the cause as intent, knowledge, execution, feedback, policy, isolation,
lifecycle, hygiene, governance, or irreducible judgment. Identify why the existing
harness failed to prevent, expose, or route it.

Completion criterion: the cause explains the mechanism, not merely the undesirable
output.

## 3. Choose the durable layer

Use the placement table in the shared contract. Prefer the narrowest layer that changes
future behavior. Promote repeated review rules to mechanical enforcement only when they
are consistently testable. Preserve human judgment when encoding would create brittle
policy.

Completion criterion: the proposal names one authoritative home, owner, evidence of
closure, and review date—or records why no durable change is justified.

## 4. Record and optionally implement

Append the learning-ledger entry. Implement the improvement only when the user authorized
that mutation and risk class; otherwise return a proposed patch scope. Link completed
changes to their evidence and update the manifest when capability level changes.

Completion criterion: the learning is traceable from episode to disposition without
duplicating the rule across layers.
