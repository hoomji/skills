---
name: harness-reference
description: Capture, update, inspect, or retire durable external reference material in a repository knowledge store. Use when agents need version-pinned API notes, protocol or standard excerpts, provider behavior evidence, or another external source under docs/references without depending on browser context, private conversations, or human memory.
---

# Harness Reference

Curate the repository's external-knowledge surface. Read the repository guidance and the
references index in full before changing it. If the repository maps references elsewhere,
follow that contract instead of assuming `docs/references/`.

## 1. Prove local capture is warranted

Inspect the authoritative source and its current consumers. Prefer a direct link when it is
stable, accessible, and sufficient. Keep a local reference only when a pinned version,
minimal excerpt, normalized observation, or durable summary is necessary for reproducible
agent work.

Completion criterion: the source, consumers, capture reason, ownership, and freshness need
are explicit; material with no durable consumer is excluded.

## 2. Bound the material

Classify the action as capture, update, inspect, or retire. Check licensing, confidentiality,
and generated-file boundaries. Select the smallest material that preserves the needed fact:
metadata plus a concise summary by default, with short excerpts only when exact wording is
essential. Keep secrets, customer data, private transcripts, and temporary research outside
the knowledge store.

Completion criterion: every retained section supports a named repository consumer and can
be stored safely.

## 3. Write provenance-first

Follow the repository's reference contract. Record source URL and title, version or
retrieval date, owner, local-copy reason, and repository consumers before the summary.
Separate sourced facts from repository inference. Use canonical domain language and link to
product specifications, ExecPlans, or ADRs that rely on the material rather than duplicating
their decisions.

Completion criterion: a future reader can locate the authority, identify staleness, and
trace every local claim to its source or label it as inference.

## 4. Index and verify

Add or update the references index with review date and consumers. When retiring material,
first remove or redirect every consumer and preserve a successor link where history needs
it. Check local links, run harness validation, and inspect the diff for copied excess or
unrelated edits.

Completion criterion: the reference is discoverable or cleanly retired, all consumers
resolve, and available structural checks pass or have named blockers.
