---
name: harness-quality-report
description: Produce or update an evidence-backed harness capability report. Use when the user wants maturity levels by plane, trends between assessments, regressions, unknowns, autonomy readiness, human-intervention patterns, or a prioritized harness investment report without collapsing readiness into one score.
---

# Harness Quality Report

Read [`../harness/references/contracts.md`](../harness/references/contracts.md). Use current
evidence; invoke `harness-assess` when the baseline is missing or stale.

## 1. Establish comparable evidence

Resolve repository revision, report period, prior baseline, tracer workflows, and changes
to assessment method. Compare only evidence collected under equivalent definitions.

Completion criterion: the report identifies its revision, date, method, and comparison
limits.

## 2. Update plane levels

For each plane, cite current evidence, assign the lowest fully supported level, and explain
every change from the prior report. Preserve `unknown` rather than carrying a stale score
forward. Never average plane levels into one readiness number.

Completion criterion: all nine planes have current evidence or an explicit unknown and
every level transition has a causal explanation.

## 3. Report operational signals

Use available evidence for cold-start time, clean setup/worktree success, acceptance
criteria with executable proof, first-pass success, regressions, human interventions by
plane, time to reviewable evidence, promoted corrections, doc freshness, pre-review
invariant catches, background-task recovery, and rollback rate. Label unavailable metrics.

Completion criterion: metrics are reproducible and are not replaced by lines of code,
prompt length, runtime, or PR count.

## 4. Recommend the next investment

Rank at most three capability increments by tracer impact, human attention saved, risk,
and implementation size. State which workflows remain R0-only and which have enough
evidence for isolated R1 experimentation.

Completion criterion: recommendations trace directly to regressions, repeated
interventions, or the lowest blocking capability.
