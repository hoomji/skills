---
name: harness-bootstrap
description: Preview and install a minimum viable harness for a software repository. Use after a harness assessment when the user wants AGENTS.md, a thin CLAUDE.md pointer, deterministic command guidance, a YAML harness manifest, an architecture entrypoint, a tracer workflow, validation, or a learning ledger added without overwriting existing conventions.
---

# Harness Bootstrap

Prepare a previewed, reviewable change set. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md) before editing.
Use templates in `assets/` as prompts for adaptation, never as blind replacements. The sole exception is `assets/PLAN.md.template`: copy it byte-for-byte to the target repository root as `PLAN.md`, because it is the canonical ExecPlan instruction file.

## 1. Gate the bootstrap

Require an evidence-backed assessment or perform `harness-assess` first. Confirm that its
assessed ref still matches the target; when it does not, run a read-only delta before
using its recommendations. Resolve the tracer workflow, dirty state, existing guidance,
authoritative docs, supported commands, and risk boundary. Preserve user-owned changes
and repository layout.

Completion criterion: proposed files, reconciliations, exclusions, and verification are
listed before mutation; overlap with existing edits is resolved.

## 2. Preview the minimum change set

Prefer these artifacts, adapting paths to established conventions:

- `AGENTS.md`: concise map, exact common commands, completion expectations, and pointers;
- `CLAUDE.md`: a small pointer to `AGENTS.md`, plus Claude-only material only when real;
- `docs/harness/manifest.yaml`: evidenced capability facts;
- `docs/harness/learning-ledger.md`: empty durable learning contract;
- `PLAN.md`: the canonical ExecPlan instructions, copied byte-for-byte from
  `assets/PLAN.md.template`;
- the knowledge store below, from `assets/knowledge-store/`;
- one existing or new architecture/domain entrypoint;
- one tracer workflow with acceptance evidence;
- a repository-local copy of `assets/harness-validate.py`, exposed through the repo's
  existing script or task-runner convention.

Reuse existing scripts and task-runner commands. Keep specialized detail behind precise
pointers. Record unknown commands honestly in the preview rather than inventing wrappers,
but stop short of completion until setup and verification have deterministic entrypoints.

### Knowledge store

Every bootstrap installs all five stores, each with an index that owns its entry
contract, so the lifecycle skills have somewhere to write on their first run:

| Path | Owner skill | Bundled template |
|---|---|---|
| `docs/design-docs/index.md` | — | `design-docs-index.md.template` |
| `docs/design-docs/core-beliefs.md` | — | `core-beliefs.md.template` |
| `docs/exec-plans/index.md` | `harness-exec-plan` | `exec-plans-index.md.template` |
| `docs/exec-plans/active/`, `docs/exec-plans/completed/` | `harness-exec-plan` | tracked with `.gitkeep` |
| `docs/exec-plans/tech-debt-tracker.md` | `harness-exec-plan` | `tech-debt-tracker.md.template` |
| `docs/generated/index.md` | producing commands | `generated-index.md.template` |
| `docs/product-specs/index.md` | `harness-product-spec` | `product-specs-index.md.template` |
| `docs/product-specs/template.md` | `harness-product-spec` | `product-spec.md.template` |
| `docs/references/index.md` | `harness-reference` | `references-index.md.template` |

Install stores empty rather than populated: an index that says it has no entries yet is
honest, and a fabricated specification, plan, or reference is not. Migrate existing
material into a store only when the user approves the move, and prefer the repository's
established path when one already exists — record that path in `knowledge_store` instead
of installing a competing directory. Declare every installed index under
`knowledge_store` in the manifest and advertise each one from `AGENTS.md`.

Before mutation, show:

- every add/edit/leave-unchanged operation;
- how existing `AGENTS.md`/`CLAUDE.md` content will be reconciled;
- evidence for each advertised command and capability;
- for each knowledge store, whether it is newly installed or mapped to an existing path,
  and any existing material that stays where it is;
- the exact validator command and expected files;
- excluded findings and why they are outside the bootstrap;
- narrow unstaged change groups, each with one purpose, a suggested commit message, and
  its verification command.

Pause for review when the preview would overwrite guidance, choose between competing
authoritative docs, or add behavior beyond the approved R1 boundary. A preview is not
permission to perform R2–R4 work.

Completion criterion: every added artifact has one responsibility and one authoritative
source; `AGENTS.md` remains a map rather than an encyclopedia.

## 3. Prepare the approved changes

Edit only the previewed files. When `PLAN.md` is absent, copy `assets/PLAN.md.template` to it byte-for-byte. When it already exists, compare it with that template and pause for review rather than overwriting divergent user guidance. Reconcile existing `CLAUDE.md` content into generic
guidance or a focused linked document before reducing it to a pointer. Keep agent-neutral
rules in `AGENTS.md`. Never replace an existing architecture or guidance file with a
template. Never overwrite an existing store index: map `knowledge_store` to it, and report
the entry-contract sections it lacks as findings rather than editing them in. Copy the
validator into a repository-owned path and keep it dependency-free.

Completion criterion: the working tree contains the intended unstaged change set and no
unrelated file has changed.

## 4. Verify and group narrowly

Run the installed harness validator, then the narrow checks named in the preview. Run only
safe checks supported by the current environment. Inspect the diff for copied
placeholders, duplicated rules, secrets, absolute personal paths, and claims lacking
evidence. Confirm the diff still matches the preview and divide it into the previewed
single-purpose change groups. Leave every group unstaged. Do not run `git add`, commit,
push, or open a PR. Provide exact path lists and suggested commit messages so the
maintainer can review and commit each group narrowly.

Completion criterion: every new pointer resolves, every capability claim cites evidence,
every declared knowledge store resolves to an index the map advertises, the target tracer
is operable from the map, and skipped checks are reported.

## 5. Hand off

Return the evidence bundle from the shared contract. Include the accepted preview, a
concise diff inventory, validator result, change-group status, remaining unknowns, next
weakest plane, rollback by group, and exact review commands. Do not push or open a PR
without separate R2 authority.
