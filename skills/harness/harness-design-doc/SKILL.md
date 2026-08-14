---
name: harness-design-doc
description: Create, revise, inspect, verify, or retire indexed repository design documentation under docs/design-docs or the repository's established equivalent. Use when a system or feature design needs durable rationale, constraints, interfaces, alternatives, or verification status without collapsing that material into product specs, ARCHITECTURE.md, ADRs, or execution plans.
---

# Harness Design Doc

Operate on the repository's design-knowledge surface. Read the repository guidance,
design-doc index, relevant product specs, `ARCHITECTURE.md`, ADRs, ExecPlans, code, and
verification evidence before changing an artifact. Follow an established equivalent path
when the repository does not use `docs/design-docs/`.

## 1. Resolve document ownership

Choose one primary action: create, revise, inspect, verify, or retire a design document.
Keep responsibilities separate:

- product specs own required user-visible behavior and outcomes;
- `ARCHITECTURE.md` owns the concise current-system map and boundaries;
- design docs explain a system or feature design, rationale, constraints, interfaces,
  alternatives, and operational implications;
- ADRs record discrete architectural decisions and their status over time;
- ExecPlans own implementation sequence, progress, recovery, and delivery evidence.

Link overlapping artifacts instead of copying them. A design doc may synthesize several
ADRs, but must not replace or silently rewrite their decision history.

Completion criterion: the artifact owner, scope, lifecycle action, related authorities,
and any conflicting source are explicit.

## 2. Write the design contract

Describe the problem context, goals and non-goals, system boundaries, proposed or current
design, interfaces and data flow, alternatives considered, constraints, failure modes,
operational consequences, security and reliability implications where relevant, and
links to governing specs and ADRs. Distinguish observed repository behavior from proposed
design.

Every design doc must expose lifecycle state, owner, last-verified date or `Unverified`,
verification evidence, and a review trigger. Use `Proposed`, `Verified`, `Superseded`,
or `Retired` unless the repository defines another vocabulary.

Completion criterion: a maintainer can understand the design and its evidence without
reconstructing chat history or treating an unverified proposal as current behavior.

## 3. Maintain the index

Add or update the design-doc index row with title, state, owner, last verified, evidence,
and related ADRs/specs. Keep foundational beliefs in a separately indexed design document
when they constrain multiple designs. Mark superseded or retired documents explicitly and
link their successors; do not delete historical design context merely because it changed.

Completion criterion: the document is discoverable from the root guidance and design-doc
index, and its index metadata agrees with the document.

## 4. Validate and hand off

Check local links, compare claims with code and tests, run repository harness validation,
and inspect the diff for duplicated authority or accidental ADR replacement. Report
changed artifacts, verification status, supporting and missing evidence, linked decisions,
residual uncertainty, and the next lifecycle action. Route implementation work to an
ExecPlan when it is complex.

Completion criterion: every design claim is labeled as proposed, observed, inferred, or
verified; available structural checks pass or have named blockers.
