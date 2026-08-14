---
name: harness-model-domain
description: Create, inspect, revise, or reconcile repository domain glossaries in CONTEXT.md and multi-context maps. Use when project terminology is vague, overloaded, inconsistent with code, missing from the canonical glossary, duplicated across contexts, or needs to be updated without mixing in specifications, implementation details, or architecture decisions.
---

# Harness Model Domain

Maintain the repository's canonical domain language. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md),
[`../harness/references/composition.md`](../harness/references/composition.md),
repository guidance, relevant `CONTEXT.md` or `CONTEXT-MAP.md` files, code, specs, and
ADRs before changing the glossary.

## 1. Prove that the glossary owns the change

Use `CONTEXT.md` only for domain-specific language: concepts whose precise meaning helps
people and agents reason about this product. Exclude general programming terms,
implementation details, requirements, plans, decisions, and scratch notes. Route
consequential rationale to `harness-record-decision`; keep behavior and acceptance
criteria in product specs.

Choose one action: inspect, create, revise, reconcile, split, or merge. A glossary is the
current canonical vocabulary, not a historical log. Edit definitions and preferred terms
in place when the domain model changes; use repository history and linked ADRs for
historical rationale.

Completion criterion: the term, owning context, ambiguity or contradiction, authoritative
domain source, and intended glossary action are explicit.

## 2. Resolve the context boundary

Follow the repository's established domain-document convention. If
`CONTEXT-MAP.md` exists, read it and select the relevant context-specific `CONTEXT.md`;
ask when ownership remains ambiguous. Keep relationships between bounded contexts in the
map and terms owned by one context in that context's glossary.

When no convention exists, default to one root `CONTEXT.md`. Create it lazily only after
the first term is resolved; do not scaffold an empty glossary. Name the root context from
an authoritative repository or product identity; do not promote the first glossary term
into the context name. Ask or leave the heading unresolved when no context name is known.
Introduce a multi-context map only when the repository has genuinely independent domain
contexts and the ownership boundary is evidenced, not merely because it has several
packages.

Completion criterion: one authoritative glossary path owns each term and cross-context
relationships have one discoverable map.

## 3. Resolve language against reality

Use the installed Matt Pocock `domain-modeling` capability when available. Challenge
vague or overloaded words, test relationships with concrete edge cases, and compare
claims with code and existing documentation. Surface contradictions rather than choosing
silently.

Write a term only after it is resolved. Prefer one canonical name, define what the concept
is in one or two sentences, and list meaningful rejected synonyms under `_Avoid_`.
Include only project-specific concepts. Group terms only when a stable domain grouping
improves navigation. Use [the context template](assets/context.md.template), and
[the context-map template](assets/context-map.md.template) only for an evidenced
multi-context repository, when no repository template exists.

Completion criterion: every changed entry is precise, scoped, supported by repository or
user authority, and free of implementation detail.

## 4. Reconcile consumers and verify

Update resolved terms inline rather than batching them until the end of a design session.
Check nearby specs, plans, ADRs, tests, interfaces, and code for contradictory meanings or
synonyms. Report those consumers; do not rename code or expand implementation scope unless
the user authorized it. A term change that also changes a consequential boundary may
require both this skill and `harness-record-decision`.

Check map links, duplicate ownership, avoided synonyms, stale references, and the diff.
Run harness validation and the narrowest relevant documentation tests. Return the shared
evidence bundle, including unresolved language and consumers intentionally left unchanged.

Completion criterion: the glossary is discoverable, each term has one canonical meaning
and owner, available validation passes, and remaining contradictions are explicit.
