# Execution plans

An execution plan (ExecPlan) is the durable record for work that spans multiple
milestones, agents, or work sessions. It must let a new contributor continue the
work with only the checkout and the plan file; chat history and prior context are
not prerequisites.

## When to use one

Use an ExecPlan for a complex feature, significant refactor, risky migration, or
investigation with material uncertainty. Store active plans in
`docs/exec-plans/active/`, and move completed plans to
`docs/exec-plans/completed/`. Use the repository template when creating a plan.

## Required qualities

Write for a newcomer. Start with the user-visible outcome and how to demonstrate
it. Define repository-specific terms when first used, name repository-relative
paths and precise seams, and state exact commands together with the expected
success signal. Resolve meaningful ambiguity in the plan; do not defer design
choices that the next implementer must make to proceed.

Every plan must include its goal, non-goals, baseline and dirty-state boundary,
sources of truth, acceptance evidence, ordered milestones, risk and approval
boundaries, progress, discoveries, decisions, recovery, and retrospective. Each
milestone has an observable outcome, a binary completion criterion, narrow
verification, rollback guidance, and an escalation point. Prefer the first
milestone to be a thin end-to-end tracer.

## Living-plan rules

Update the plan at every stopping point. Progress distinguishes completed,
partial, and remaining work. Replace proposed validation with the commands
actually run, recording results, skipped checks, and blockers. Record discoveries
that change the approach and decisions that resolve alternatives. Preserve the
history: correct stale assumptions without rewriting why a prior decision was
made.

At completion, compare the delivered behavior and evidence with the original
goal, record residual risks and lessons, update the active index, and move the
plan to the completed location. A plan is complete only when its promised
behavior is demonstrated, not merely when the code has changed.

## Safety

An ExecPlan may describe later R2-R4 actions, but must place an explicit human
gate immediately before each such action. Include a safe retry or rollback path
for operations that can fail partway through, and keep repeated steps idempotent
where practical.
