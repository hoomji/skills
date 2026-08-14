---
name: harness-exec-plan
description: Create, resume, maintain, complete, or inspect self-contained repository ExecPlans. Use when multi-milestone work must survive beyond chat context, a novice agent must be able to restart it, or plan state must be reconciled with implementation and acceptance evidence.
---

# Harness ExecPlan

Manage the living execution-plan lifecycle. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md), repository
guidance, and the repository's ExecPlan index in full before acting. If the repository maps
plans elsewhere, use that contract instead of assuming `docs/exec-plans/`.

## 1. Resolve the lifecycle state

Identify whether the task creates, resumes, updates, inspects, completes, or supersedes a
plan. Read the linked product specification, issue, ADRs, current plan, relevant code, and
working-tree state. Reconcile the plan with reality before relying on its unchecked items.

Completion criterion: one plan, baseline, lifecycle action, current milestone, dirty-state
boundary, and maximum authorized risk class are explicit.

## 2. Make the plan restartable

For a new plan, start from [`assets/exec-plan.md.template`](assets/exec-plan.md.template).
For an existing plan, preserve its decision history while correcting stale assumptions. A
plan is self-contained only when a novice can follow it using the working tree and the plan
file alone: define non-ordinary terms where they first appear, name repository-relative
paths and exact commands, and embed necessary reasoning rather than pointing to external
documentation.

ExecPlan files contain only the plan and therefore omit an outer code fence. When an
ExecPlan is embedded inside another Markdown document, wrap the entire plan in one `md`
fence and show commands, transcripts, and excerpts as indented blocks; do not nest fences.
Keep prose first outside the mandatory Progress checklist. Use the template's required
living-document sections: purpose, progress, discoveries, decision log, outcomes,
orientation, plan of work, concrete steps, validation, recovery, artifacts, interfaces,
and revision note.

Use the first milestone as a thin end-to-end tracer where possible. Give every milestone a
binary completion criterion, narrow verification, rollback path, and escalation boundary.
Describe each milestone as a readable goal-work-result-proof narrative, and use additive,
independently verifiable prototypes where they reduce uncertain or high-risk work.

Completion criterion: a fresh agent can execute the next milestone and determine success
without chat history or unstated human knowledge.

## 3. Maintain evidence while work moves

At every stopping point, update progress to distinguish completed, partial, and remaining
work. Record discoveries when they change the approach and decisions when alternatives are
resolved. Replace planned commands with the commands actually run and distinguish executed,
skipped, and failed checks. Update every affected section after revising the plan, then add
a dated revision note explaining why it changed. Keep the plan aligned with the
implementation; never rewrite history to make the original plan appear correct.

Completion criterion: plan state, repository state, and reported evidence agree at the
current stopping point.

Use canonical domain language throughout the plan. Route a newly resolved term or changed
meaning through `harness-model-domain`; the plan is not the glossary. The Decision Log
records task-local reasoning and does not replace durable architecture history. Route a
newly resolved, consequential architectural trade-off through `harness-record-decision`,
then link the ADR from the plan. Do not continue an implementation path that contradicts
an accepted ADR until the decision is reopened.

## 4. Complete or hand off

Complete a plan only when its promised behavior and acceptance evidence exist. Write the
retrospective, name residual risks and skipped checks, update the active index, and move the
file to the repository's completed-plan location. Otherwise leave it active with one
concrete next action and any blocking human judgment.

Run harness validation and the narrowest relevant repository checks after document changes.
Report the plan path, lifecycle transition, evidence, rollback, and remaining gates.

Completion criterion: the plan is discoverable in exactly one lifecycle index and its
recorded status is supported by repository evidence.