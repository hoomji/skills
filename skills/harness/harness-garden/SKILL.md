---
name: harness-garden
disable-model-invocation: true
description: User-invoked only. Read-only repository harness gardening for stale, conflicting, broken, duplicated, or orphaned agent-facing artifacts. Use when the user wants to audit AGENTS.md pointers, commands, docs, plans, manifest claims, exceptions, hooks, skills, learning-ledger items, or architecture drift; use fix mode only when explicitly requested.
---

# Harness Garden

## Invocation

Run only when the user explicitly invokes this skill by name (for example,
`$harness-garden` in Codex or `/harness-garden` in Claude Code). A matching task or a reference from another skill is not an
invocation. References to other harness skills below are recommendations; run
those skills only when the user explicitly invokes them as well. Continue the
authorized task directly when a recommended skill has not been invoked.

Read [`../harness/references/contracts.md`](../harness/references/contracts.md). Default to
R0 report mode.

## 1. Bound the garden

Resolve repository state, artifact roots, freshness policy, generated-file boundaries,
and whether the user requested report or fix mode. Protect dirty and user-owned changes.

Completion criterion: scanned surfaces and excluded trees are explicit.

## 2. Scan for drift

Check:

- broken or misleading `AGENTS.md` and `CLAUDE.md` pointers;
- advertised commands that no longer exist or disagree with CI;
- conflicting or duplicated sources of truth;
- stale ownership, review dates, exceptions, and manifest evidence;
- active plans with no progress, completed plans left active, and orphaned debt;
- knowledge stores whose index and directory disagree: unlisted files, indexed files that
  no longer exist, artifacts in two stores, and plans in two lifecycle states;
- design documents whose verification evidence no longer holds, and references past their
  review date or pinned to a version the repository no longer uses;
- generated artifacts whose producing command is gone, or whose content no longer matches
  what regeneration would produce;
- repeated workarounds or learning-ledger entries without disposition;
- skills whose triggers, references, or scripts no longer match the repository;
- broken `CONTEXT-MAP.md` links, terms owned by multiple contexts, stale avoided
  synonyms, or code and guidance that use contradictory meanings;
- ADRs with broken predecessor/successor links, conflicting accepted decisions, or
  implementation and guidance that silently drifted from the recorded choice;
- declared architecture or policy that enforcement no longer covers.

Treat age as a prompt to verify, not proof of staleness.

Completion criterion: every finding cites the conflicting facts and every scanned category
has a result.

## 3. Rank and report

Rank by misleading-agent impact, workflow frequency, safety, and repair size. Separate
confirmed drift, suspected drift, and unknowns. Recommend small independent repairs.

Completion criterion: maintainers can resolve each finding without rediscovering its
evidence.

## 4. Fix only on request

In explicit fix mode, prepare small reviewable changes, run relevant validations, update
manifest or ledger evidence, and return the shared evidence bundle. Scheduled gardening
remains read-only until manual runs demonstrate low false-positive rates.
