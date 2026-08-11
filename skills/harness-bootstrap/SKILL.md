---
name: harness-bootstrap
description: Prepare an unstaged minimum viable harness for a software repository. Use after a harness assessment when the user wants AGENTS.md, a thin CLAUDE.md pointer, deterministic command guidance, a YAML harness manifest, an architecture entrypoint, a tracer workflow, validation, or a learning ledger added without overwriting existing conventions.
---

# Harness Bootstrap

Prepare an unstaged, reviewable change set. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md) before editing.
Use templates in `assets/` as prompts for adaptation, never as blind replacements.

## 1. Gate the bootstrap

Require an evidence-backed assessment or perform `harness-assess` first. Resolve the
tracer workflow, dirty state, existing guidance, authoritative docs, supported commands,
and risk boundary. Preserve user-owned changes and repository layout.

Completion criterion: proposed files, reconciliations, exclusions, and verification are
listed before mutation; overlap with existing edits is resolved.

## 2. Design the minimum change set

Prefer these artifacts, adapting paths to established conventions:

- `AGENTS.md`: concise map, exact common commands, completion expectations, and pointers;
- `CLAUDE.md`: a small pointer to `AGENTS.md`, plus Claude-only material only when real;
- `docs/harness/manifest.yaml`: evidenced capability facts;
- `docs/harness/learning-ledger.md`: empty durable learning contract;
- one existing or new architecture/domain entrypoint;
- one tracer workflow with acceptance evidence;
- one harness validation command when it can be deterministic.

Reuse existing scripts and task-runner commands. Keep specialized detail behind precise
pointers. Record unknown commands as unknown rather than inventing wrappers.

Completion criterion: every added artifact has one responsibility and one authoritative
source; `AGENTS.md` remains a map rather than an encyclopedia.

## 3. Prepare changes

Edit only the approved files. Reconcile existing `CLAUDE.md` content into generic
guidance or a focused linked document before reducing it to a pointer. Keep agent-neutral
rules in `AGENTS.md`. Leave all changes unstaged: do not run `git add`, commit, push, or
open a PR.

Completion criterion: the working tree contains the intended unstaged change set and no
unrelated file has changed.

## 4. Verify

Check links, manifest paths, advertised commands, and `CLAUDE.md` → `AGENTS.md` routing.
Run only safe checks supported by the current environment. Inspect the diff for copied
placeholders, duplicated rules, secrets, absolute personal paths, and claims lacking
evidence.

Completion criterion: every new pointer resolves, every capability claim cites evidence,
the target tracer is operable from the map, and skipped checks are reported.

## 5. Hand off

Return the evidence bundle from the shared contract. Include a concise diff inventory,
remaining unknowns, next weakest plane, and exact review commands. State explicitly that
the change set is unstaged.
