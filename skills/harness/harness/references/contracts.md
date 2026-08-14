# Harness contracts

Read this reference whenever a harness skill assesses, creates, or updates shared
artifacts.

## Planes

| Plane | Evidence sought |
|---|---|
| Intent | Specs, acceptance criteria, plans, decisions |
| Knowledge | Agent map, architecture, domain language, indexed design docs, ADRs, operations docs |
| Execution | Deterministic setup, start, build, test, seed, and release commands |
| Feedback | Tests, UI inspection, logs, metrics, traces, performance evidence |
| Policy | Linters, schemas, structural tests, hooks, CI gates, remediation messages |
| Isolation | Worktrees, namespaced ports/data/services, task-local telemetry |
| Lifecycle | Intake, plan, implementation, review, recovery, PR, and merge paths |
| Hygiene | Freshness checks, debt ledger, quality scan, recurring cleanup |
| Governance | Permissions, risk classes, approval gates, audit and escalation |

Score every plane independently:

- `0 opaque`: a person or inaccessible system is required.
- `1 documented`: instructions exist, but execution is manual or ambiguous.
- `2 executable`: deterministic commands or tools perform the capability.
- `3 verifiable`: reproducible evidence distinguishes success from failure.
- `4 enforced`: important boundaries fail mechanically with remediation.
- `5 adaptive`: bounded maintenance detects drift and improves the harness.
- `unknown`: available evidence cannot support a level.

Use the lowest fully evidenced level. Never infer a higher level from file names alone.

## Harness manifest

Use `docs/harness/manifest.yaml`. YAML is the initial interchange format because humans
can review it and common tooling can validate it. Record facts, not aspirations.

```yaml
version: 1
owners:
  harness: "team-or-person"
entrypoints:
  guidance: "AGENTS.md"
  architecture: "ARCHITECTURE.md"
  design: "docs/design-docs/index.md"
  tracer: "docs/harness/tracer-workflow.md"
commands:
  setup: "exact command or unknown"
  start: "exact command or unknown"
  check: "exact command or unknown"
  test: "exact command or unknown"
  validate: "python3 scripts/harness-validate.py ."
capabilities:
  reproducible_setup:
    status: "documented"
    evidence:
      - "README.md"
policies: []
freshness:
  review_after_days: 90
```

Capability statuses are `missing`, `documented`, `executable`, `verified`, or
`automated`. Every `verified` or `automated` claim names reproducible evidence. Every
policy names its enforcement, owner, and remediation path. During assessment, an unknown
command stays `unknown`; a completed minimum bootstrap must resolve setup, check, test,
and validate to deterministic entrypoints. Start may remain `unknown` only when
`capabilities.startable_runtime` is `missing` and cites repository evidence.

## Domain context

Follow the repository's established domain-document convention. When none exists, use one
root `CONTEXT.md` and create it lazily after the first term is resolved. Treat an existing
`CONTEXT-MAP.md` as the authority for multi-context layout; keep domain relationships in
the map and each owned term in exactly one context glossary.

`CONTEXT.md` is a living glossary of current, project-specific language. It is not a spec,
implementation guide, decision log, or scratch pad. Prefer one canonical term, a one- or
two-sentence definition of what it is, and meaningful rejected synonyms under `_Avoid_`.
Edit obsolete meanings in place; use repository history and ADRs for historical rationale.
Route consequential boundary choices to `harness-record-decision`.

## Decision records

Follow the repository's established architecture-decision convention. When none exists,
use `docs/adr/NNNN-short-slug.md` and create it lazily. Record a decision as an ADR only
when it is hard to reverse, surprising without context, and the result of a real
trade-off. A product spec owns required behavior; an ExecPlan decision log owns
task-local execution choices; an ADR owns durable architectural rationale.

Preserve accepted history. Represent a changed decision with a superseding ADR and
bidirectional predecessor/successor links instead of rewriting the old record. Treat
`proposed`, `accepted`, `deprecated`, and `superseded by ADR-NNNN` as the fallback status
vocabulary when the repository does not define one. Documentation is not enforcement:
route checkable architectural boundaries to `harness-encode-invariant`.

## Assessment finding

```yaml
id: "feedback.runtime-logs"
plane: "feedback"
level: 1
confidence: "high"
scope: "credential-free tracer execution on assessed-ref@commit"
required_for_tracer: true
evidence:
  - "docs/operations/observability.md:12"
present_capability: "Runtime logging is documented but has no task-local query path."
gap: "Agents cannot query task-local logs."
impact: "Runtime defects require human reproduction."
next_capability: "Add a read-only log query command for the tracer service."
risk: "R1"
```

Every factual claim links to a path, command result, or explicit `unknown`. Separate
absence from undiscovered evidence.

## Evidence bundle

Every completed mutating workflow reports:

- starting state and requested scope;
- changed artifacts;
- each acceptance criterion and its result;
- commands run and meaningful outcomes;
- runtime evidence where applicable;
- review findings and resolutions;
- residual risks and skipped checks with reasons;
- required human judgment or follow-up.

## Learning ledger

Use `docs/harness/learning-ledger.md`. Each entry records observed friction, frequency,
impact, missing plane, chosen durable layer, resulting change or decision not to encode,
owner, closure evidence, and review date.

Route knowledge to the most enforceable useful layer:

| Need | Layer |
|---|---|
| One task | Prompt or acceptance criteria |
| Durable navigation and commands | `AGENTS.md` |
| Detailed stable knowledge | Focused versioned document |
| System or feature design, rationale, and verification state | Indexed design document |
| Discrete architectural decision and status history | ADR |
| Repeatable method | Skill |
| Deterministic operation | Script or task-runner command |
| Checkable invariant | Test, lint, schema, hook, or CI |
| Live external state | Connector, MCP server, or scoped tool |
| Stable recurrence | Scheduled task invoking a tested skill |

## Risk classes

| Class | Boundary |
|---|---|
| R0 inspect | Read-only files, local queries, and history inspection |
| R1 reversible local | Workspace edits, tests, and isolated worktrees |
| R2 shared reversible | Branch push, draft PR, non-production issue mutation |
| R3 consequential | Merge, staging deploy, or shared test-data mutation |
| R4 high consequence | Production, destructive migrations, secrets, policy changes |

Initial scheduled workflows remain R0. Permit R1 only after the exact skill succeeds
manually and runs in an isolated worktree. R2–R4 require workflow-specific authority;
R4 requires a human gate at action time and normally remains outside skill scope.

Escalate conflicting intent, unsupported safety claims, destructive or irreversible
actions, inaccessible required evidence, source-of-truth conflicts, protected-invariant
exceptions, and changes without a credible recovery path.
