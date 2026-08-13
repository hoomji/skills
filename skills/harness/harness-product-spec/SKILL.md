---
name: harness-product-spec
description: Create, revise, inspect, or retire repository-local product specifications that define user problems, outcomes, behavioral boundaries, and acceptance criteria separately from implementation. Use when product intent belongs under docs/product-spec, a product-facing change lacks an authoritative specification, or an existing specification must be reconciled with issues, ADRs, code, and delivery evidence.
---

# Harness Product Spec

Operate on the repository's product-intent surface. Read the repository guidance and the
product-spec index and template in full before changing an artifact. If the repository
uses another path, follow its map instead of assuming `docs/product-spec/`.

## 1. Ground the intent

Read the originating request or issue, canonical domain language, relevant product specs,
design docs, ADRs, and observable current behavior. Separate the user's problem and required behavior
from proposed implementation. Surface contradictory authorities and product decisions that
only a human can make.

Completion criterion: the user, problem, outcome, non-goals, constraints, and authoritative
sources are explicit; every unresolved product judgment has an owner or escalation.

## 2. Choose the artifact action

Select exactly one primary action:

- create a specification from the repository template;
- revise the current specification without erasing delivered history;
- inspect and report gaps without mutation;
- mark a specification delivered or superseded with evidence and successor links.

Preserve historical engineering specifications unless the repository explicitly defines a
migration. Keep implementation sequence in an ExecPlan and architectural choices in ADRs.

Completion criterion: one authoritative product-spec path and lifecycle state are resolved,
with overlapping artifacts linked or dispositioned.

## 3. Write the behavioral contract

Use the repository template. Write observable outcomes and acceptance criteria in canonical
domain language. Cover boundaries, failure behavior, compatibility, rollout constraints,
and non-goals only where the product needs them. Link sources instead of copying their
content; record the product decision here only when this file owns it.

Completion criterion: every required behavior maps to at least one observable acceptance
criterion, and no acceptance criterion prescribes incidental implementation.

## 4. Validate and hand off

Update the product-spec index, check local links, run the repository's harness validation,
and inspect the diff for unrelated edits. Report changed artifacts, resolved and open
decisions, validation results, and the next lifecycle action. If implementation is next,
route complex work to `harness-exec-plan`.

Completion criterion: the specification is discoverable from the repository map, its state
and owner are current, and all available structural checks pass or have named blockers.
