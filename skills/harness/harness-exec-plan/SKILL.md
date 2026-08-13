---
name: harness-exec-plan
description: Create, resume, maintain, complete, or inspect repository-local ExecPlans for complex features and significant refactors. Use when work belongs under docs/exec-plans, must survive beyond chat context, spans multiple milestones or agent runs, needs progress and decision logs, or an active plan must be reconciled with implementation and acceptance evidence.
---

# Harness ExecPlan

Manage the living execution-plan lifecycle. Read the repository guidance and the ExecPlan
index and template in full before acting. If the repository maps plans elsewhere, use that
contract instead of assuming `docs/exec-plans/`.

## 1. Resolve the lifecycle state

Identify whether the task creates, resumes, updates, inspects, completes, or supersedes a
plan. Read the linked product specification, issue, design docs, ADRs, current plan, relevant code, and
working-tree state. Reconcile the plan with reality before relying on its unchecked items.

Completion criterion: one plan, baseline, lifecycle action, current milestone, dirty-state
boundary, and maximum authorized risk class are explicit.

## 2. Make the plan restartable

For a new plan, start from the repository template. For an existing plan, preserve its
decision history while correcting stale assumptions. Keep purpose, context, milestones,
exact commands, acceptance, recovery, interfaces, progress, discoveries, decisions, and
retrospective self-contained. Define repository terms at first use and name precise paths.

Use the first milestone as a thin end-to-end tracer where possible. Give every milestone a
binary completion criterion, narrow verification, rollback path, and escalation boundary.

Completion criterion: a fresh agent can execute the next milestone and determine success
without chat history or unstated human knowledge.

## 3. Maintain evidence while work moves

At every stopping point, update progress to distinguish completed, partial, and remaining
work. Record discoveries when they change the approach and decisions when alternatives are
resolved. Replace planned commands with the commands actually run and distinguish executed,
skipped, and failed checks. Keep the plan aligned with the implementation; never rewrite
history to make the original plan appear correct.

Completion criterion: plan state, repository state, and reported evidence agree at the
current stopping point.

## 4. Complete or hand off

Complete a plan only when its promised behavior and acceptance evidence exist. Write the
retrospective, name residual risks and skipped checks, update the active index, and move the
file to the repository's completed-plan location. Otherwise leave it active with one
concrete next action and any blocking human judgment.

Run harness validation and the narrowest relevant repository checks after document changes.
Report the plan path, lifecycle transition, evidence, rollback, and remaining gates.

Completion criterion: the plan is discoverable in exactly one lifecycle index and its
recorded status is supported by repository evidence.
