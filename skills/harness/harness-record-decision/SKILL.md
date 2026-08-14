---
name: harness-record-decision
description: Create, inspect, accept, deprecate, or supersede repository architecture decision records (ADRs). Use when a consequential technical or boundary choice is hard to reverse, surprising without context, and resolves a real trade-off; when a plan or implementation conflicts with an existing ADR; or when decision history must be reconciled without rewriting it.
---

# Harness Record Decision

Manage the repository's durable decision history. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md), repository
guidance, relevant domain language, existing ADRs, and the originating issue, spec, or
plan before changing a record.

## 1. Prove that an ADR is warranted

Require all three conditions:

1. **Hard to reverse:** changing course later has meaningful cost.
2. **Surprising without context:** a future maintainer could reasonably undo or question
   the choice without its rationale.
3. **A real trade-off:** credible alternatives existed and specific reasons resolved them.

If any condition is missing, keep the choice in the task's spec, ExecPlan decision log,
code, or review notes instead. Do not create an ADR merely because a decision occurred.

Completion criterion: the decision, alternatives, owner, scope, reversal cost, and source
that authorizes the outcome are explicit; unresolved human judgment remains `proposed`.

## 2. Resolve location and lifecycle action

Follow the repository's established decision-record convention and index. When none
exists, use `docs/adr/NNNN-short-slug.md`, scan for the highest number, increment it, and
create the directory only when the first qualifying decision is recorded. In a
multi-context repository, use the context-specific decision directory only when the
repository map establishes one; keep cross-context decisions at the system level.

Choose one action: inspect, create, accept, deprecate, or supersede. Preserve accepted
history. Correcting a typo or broken link in place is fine; changing the decision or its
rationale requires a new ADR that names the predecessor, and the predecessor must link
back to the successor. Never renumber existing records or silently replace an accepted
choice.

Completion criterion: one authoritative path, lifecycle action, status vocabulary, and
predecessor or successor relationship are resolved without conflicting sources of truth.

## 3. Write the smallest useful record

Use [`assets/adr.md.template`](assets/adr.md.template) only when the repository has no
template. At minimum, state the context, decision, and why in one to three sentences.
Add status metadata, considered options, consequences, evidence, or supersession links
only when they make the record easier to operate or revisit. Use canonical domain terms
and link to specs, plans, references, or issues instead of copying them.

Before writing, search for an existing record that already owns the decision. Surface any
conflict with an accepted ADR. An agent may draft a proposed record under R1 authority,
but may mark it accepted only when the user or an authoritative repository source has
actually resolved the trade-off.

Completion criterion: a future maintainer can tell what was decided, why, what it applies
to, and whether it is current without reconstructing chat history.

## 4. Reconcile consumers and verify

Update an existing architecture map or decision index when its convention requires it.
Reconcile affected product specs and ExecPlans with links, not duplicated rationale. When
implementation would contradict an accepted ADR, stop that path until the contradiction
is explicitly resolved or a superseding record is accepted. Route mechanically checkable
boundaries to `harness-encode-invariant`; an ADR documents intent but does not enforce it.

Check numbering, local links, status and supersession symmetry, repository guidance, and
the diff. Run harness validation and the narrowest relevant documentation tests. Return
the shared evidence bundle, including skipped checks and any decision still awaiting a
human.

Completion criterion: the record is discoverable, consumers agree with its current state,
available validation passes, and historical decisions remain traceable.
