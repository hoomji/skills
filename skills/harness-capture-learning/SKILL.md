---
name: harness-capture-learning
description: Turn repeated agent friction, review corrections, failed runs, or human interventions into the narrowest durable repository improvement. Use when the same mistake recurs, a workflow needed hidden knowledge, or feedback should compound into guidance, documentation, a skill, a script, enforcement, tooling, or an explicit decision not to encode.
---

# Harness Capture Learning

Read [`../harness/references/contracts.md`](../harness/references/contracts.md).

## 1. Capture the episode

Record the observed behavior, expected behavior, evidence, frequency, impact, and task
context. Distinguish one-off preference from a repeated or high-impact capability gap.
Use raw review comments, failed-run output, or intervention records as evidence; do not
upgrade recollection into a recurrence count.

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

Use [`assets/learning-ledger-entry.md.template`](assets/learning-ledger-entry.md.template)
and append one entry to the repository's existing learning ledger. Record one disposition:
implemented, proposed, or not encoded. The workflow's maximum class is R1: when the user
authorized it, make only a directly related reversible local improvement. Hand mechanical
enforcement, runtime tooling, shared workflow changes, pushes, and external mutations to
the relevant follow-on skill with the proposed scope and risk class. Link completed local
changes to their evidence and update the manifest only when evidence supports a
capability-level change.

Set a concrete review date from `freshness.review_after_days` in the harness manifest.
When the manifest has no freshness window, use 90 days from the entry date and label that
as the default. A `not encoded` disposition still gets reviewed when new recurrence
evidence appears or that date arrives.

Completion criterion: the learning is traceable from episode to disposition without
duplicating the rule across layers.

Appending the ledger is R1. Stop after the ledger entry and handoff when the improvement
requires R2–R4 authority.
