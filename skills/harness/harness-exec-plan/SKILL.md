---
name: harness-exec-plan
description: Create, resume, maintain, complete, or inspect self-contained repository ExecPlans and their implementation slices. Use when multi-milestone work must survive beyond chat context, a milestone exceeds one agent context and must be cut into fresh-context slices, a novice agent must be able to restart it, or plan state must be reconciled with implementation and acceptance evidence.
---

# Harness ExecPlan

Manage the living execution-plan lifecycle. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md), repository
guidance, and the repository's ExecPlan index in full before acting. Resolve the store from
`knowledge_store.exec_plans` in the harness manifest; if the repository maps plans
elsewhere, use that contract instead of assuming `docs/exec-plans/` with its `index.md`,
`active/`, `completed/`, and `tech-debt-tracker.md`.

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

## 3. Cut oversized milestones into slices

A slice is one implementation unit sized to a single fresh agent context. Cut slices only
when a milestone exceeds that budget: a milestone whose file, the files it names, and its
verification output fit one context needs no slices, and adding them is ceremony. When the
milestone does not fit, split it and start each slice from
[`assets/slice.md.template`](assets/slice.md.template).

Self-containment is scoped to the slice, not to the plan. The executing agent reads the
slice file and the working tree only; it does not read the parent plan, the sibling slices,
or chat history. Restate the orientation, paths, terms, baseline, and dirty-state boundary
the slice needs even where that repeats the plan. A slice that requires the plan to be
understood is not yet a slice.

Give every slice exactly one parent milestone, an ordered position and stated dependencies,
a binary completion criterion, an exact verification command with expected output, a
rollback path, a risk ceiling, and an explicit out-of-scope list naming the later slices
that own the adjacent work. Prefer additive changes that keep the repository verifiable
between slices. A milestone is complete when every slice under it is done and the
milestone's own verification passes; slice criteria do not replace it.

Store slices where the repository maps them; otherwise use
`docs/exec-plans/<plan-slug>/slices/M<k>-S<n>-<slug>.md` and create the directory lazily.
Keep a slice index in the milestone listing each slice id, title, path, and status, so the
plan stays the single place that shows remaining work. Slice files carry no outer code
fence and use indented blocks for commands and transcripts, matching the ExecPlan envelope.

Hand a slice to `harness-deliver-work` as the executable contract. When it completes, fold
its Execution Record into the plan's `Progress`, `Surprises & Discoveries`, and
`Decision Log`, then update the slice status in both the slice header and the index.

Completion criterion: each slice can be executed and proven by an agent that has read
nothing but that slice file and the working tree.

## 4. Maintain evidence while work moves

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

## 5. Complete or hand off

Complete a plan only when its promised behavior and acceptance evidence exist. Write the
retrospective, name residual risks and skipped checks, update the active index, and move the
file and its slice directory together to the repository's completed-plan location. Otherwise
leave it active with one concrete next action, the next `ready` slice if any, and any
blocking human judgment.

Run harness validation and the narrowest relevant repository checks after document changes.
Report the plan path, lifecycle transition, evidence, rollback, and remaining gates.

Completion criterion: the plan is discoverable in exactly one lifecycle index and its
recorded status is supported by repository evidence.