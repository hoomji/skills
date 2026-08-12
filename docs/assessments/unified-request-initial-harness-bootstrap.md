# Initial harness bootstrap — `unified-request`

**Evidence date:** 2026-08-11  
**Target:** `henry-sandcastle` @ `dcee73d10`  
**Boundary:** R1, unstaged local edits only

This report was reconstructed from the live unstaged repository state after the original
run transcript file was created empty. It records only evidence still inspectable in the
tree; prompts, intermediate choices, and commands whose output was not retained remain
unknown.

## Gate and preservation

- The assessment baseline is
  `docs/generated/assessment/2026-08-11-harness-assessment.md`.
- Pre-existing work under `.seed-henry-sandcastle/` remains untracked and untouched.
- Existing repository conventions were retained: Yarn/package scripts, `CONTEXT.md`,
  `docs/adr/`, `.claude/skills/`, and the established CI-local aggregator.
- `CLAUDE.md` was reconciled into a pointer after its shared guidance moved to the new
  root `AGENTS.md` map.

## Prepared change set

| Operation | Path | Purpose |
|---|---|---|
| Add | `AGENTS.md` | Shared repository map, commands, working agreement, and known gaps |
| Add | `ARCHITECTURE.md` | Root architecture entrypoint |
| Add | `docs/harness/manifest.yaml` | Evidenced capability and policy facts |
| Add | `docs/harness/tracer-workflow.md` | Provider-routing tracer with acceptance evidence |
| Add | `docs/harness/learning-ledger.md` | Durable harness-friction contract |
| Add | `scripts/harness-validate.py` | Dependency-free repository validator |
| Edit | `package.json` | Stable `yarn setup` entrypoint |
| Edit | `.gitignore` | Track the root shared map while leaving nested maps ignored |
| Edit | `CLAUDE.md` | Route Claude Code to the shared map |

The root map points to existing domain, ADR, e2e, review, skill, and PR-queue sources
instead of duplicating them. The tracer reuses the existing
`.claude/skills/add-provider-to-unified-endpoint/SKILL.md` method and adds the surrounding
risk, acceptance, and evidence contract.

## Declared commands

| Manifest key | Command | Repository evidence |
|---|---|---|
| `setup` | `yarn setup` | new `package.json` alias for `yarn install --immutable` |
| `start` | `yarn start:dev` | existing package script and `test/e2e/README.md` |
| `check` | `yarn ci:local` | `scripts/ci-local.js` and its unit coverage |
| `test` | `yarn test:unit` | existing deterministic Jest tier |
| `validate` | `python3 scripts/harness-validate.py .` | new repository-local validator |

## Verification retained or reproduced

| Check | Result |
|---|---|
| `python3 scripts/harness-validate.py .` | **PASS**, 0 warnings on 2026-08-11 |
| Required minimum artifacts | Present and repository-relative |
| Guidance routing | `CLAUDE.md` points to root `AGENTS.md` |
| Dirty-tree preservation | Pre-existing `.seed-henry-sandcastle/` remains outside the bootstrap diff |
| Read-only second pass | No missing minimum artifact or additional bootstrap edit identified |

The original run's focused Yarn checks were not retained in this report and are therefore
not claimed. The repository-local validator is reproducible; broader product verification
remains part of the eventual commit review.

## Contrast with `auto-route`

| Dimension | `unified-request` | `auto-route` |
|---|---|---|
| Command surface | Yarn scripts plus `scripts/ci-local.js` | Existing Make targets plus one validator target |
| Architecture entrypoint | New root `ARCHITECTURE.md` | Reused `ai/ARCHITECTURE.md` |
| Tracer | Add a provider surface offline | Deliver a `ready-for-agent` issue |
| Strong policy evidence | Suite boundaries, drift checks, replay, PR queue | Import-linter contracts, lint, credential-free tests |
| Honest missing capability | Runtime query path and runtime namespacing | Runtime observability and binding merge gate |
| Guidance reconciliation | New root `AGENTS.md`; thin `CLAUDE.md` | Expanded existing root `AGENTS.md`; thin `CLAUDE.md` |

The two bootstraps share the same artifact contract without sharing repository-specific
content. Both remain unstaged and stop at R1.

## Residual risk

- The bootstrap exists only on `henry-sandcastle`; propagation to the default branch is
  R2 and was not authorized.
- The local runtime still uses fixed ports and has no task-local log/metric/trace query.
- This reconstruction cannot prove the exact preview dialogue or every command from the
  original run; it deliberately limits claims to current files and reproduced validation.
