# Agent guidance

## Repository map

- Product language: [`CONTEXT.md`](CONTEXT.md)
- Architecture and boundaries: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Product specifications: [`docs/product-specs/index.md`](docs/product-specs/index.md)
- Design documentation: [`docs/design-docs/index.md`](docs/design-docs/index.md)
- Decisions: [`docs/adr/index.md`](docs/adr/index.md)
- Active and completed work: [`docs/exec-plans/index.md`](docs/exec-plans/index.md)
- Accepted technical debt: [`docs/exec-plans/tech-debt-tracker.md`](docs/exec-plans/tech-debt-tracker.md)
- External references: [`docs/references/index.md`](docs/references/index.md)
- Generated documentation, never hand-edited: [`docs/generated/index.md`](docs/generated/index.md)
- ExecPlan contract: [`PLANS.md`](PLANS.md)
- Development and operations: [`docs/operations/development.md`](docs/operations/development.md)
- Harness capability state: [`docs/harness/manifest.yaml`](docs/harness/manifest.yaml)
- Representative workflow: [`docs/harness/tracer-workflow.md`](docs/harness/tracer-workflow.md)
- Risk and approvals: [`docs/harness/governance.md`](docs/harness/governance.md)
- Repeated-friction ledger: [`docs/harness/learning-ledger.md`](docs/harness/learning-ledger.md)

## Common commands

- Setup: `python scripts/setup.py`
- Start/self-check: `python scripts/start.py`
- Focused check: `python scripts/check.py`
- Full verification: `python scripts/test.py`
- Harness validation: `python scripts/harness-validate.py .`
- Read-only gardening: `python scripts/garden.py`
- Quality report: `python scripts/quality_report.py`

## Working agreement

Read the originating product spec before editing behavior and the relevant indexed design doc before changing system structure. Use the canonical terms in `CONTEXT.md`. Keep dependency direction consistent with `ARCHITECTURE.md`. Record discrete architectural choices in ADRs; do not use design docs as a replacement decision log. For multi-step work, create or update an ExecPlan according to `PLANS.md` as decisions and evidence change.

Work within the requested risk boundary. Make the smallest in-scope change, run the focused check, run full verification when supported, and record evidence for every acceptance criterion. Report skipped checks, ambiguous evidence, residual risk, and any action requiring human approval.

Do not claim a higher harness capability than `docs/harness/manifest.yaml` can prove. When the same correction recurs, add a learning-ledger entry and promote it only to the narrowest durable layer that can enforce it consistently.
