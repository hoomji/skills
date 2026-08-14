# Codex harness engineering example

This directory is a self-contained reference repository showing the complete flow described by OpenAI's harness-engineering model and the product contract in [`../../docs/product-specs/harness-engineering-system.md`](../../docs/product-specs/harness-engineering-system.md).

It is intentionally small enough to understand in one sitting but complete enough to demonstrate every harness plane with concrete artifacts and executable evidence. Copy the structure selectively into a real repository; do not copy capability claims until the target repository can prove them.

## What this example demonstrates

| Plane | Example implementation |
| --- | --- |
| Intent | `docs/product-specs/`, acceptance criteria, ADRs, and ExecPlans |
| Knowledge | `AGENTS.md`, `CONTEXT.md`, `ARCHITECTURE.md`, indexed design docs, ADRs, operations docs, and references |
| Execution | Stable standard-library Python commands under `scripts/` |
| Feedback | Unit tests, structured runtime output, evidence bundles, and CI |
| Policy | Repository-owned checks with actionable diagnostics |
| Isolation | A worktree-derived task namespace and no shared mutable services |
| Lifecycle | Intake through plan, delivery, review, recovery, PR, and merge |
| Hygiene | Learning ledger, gardening report, debt register, and quality score |
| Governance | Risk classes, approval gates, permissions, and escalation rules |

## Repository map

```text
examples/codex-harness/
├── AGENTS.md
├── CLAUDE.md
├── CONTEXT.md
├── ARCHITECTURE.md
├── .codex/config.toml
├── .github/workflows/harness.yml
├── .agents/skills/status-summary/
├── src/
├── tests/
├── scripts/
└── docs/
    ├── product-specs/
    ├── design-docs/
    ├── adr/
    ├── exec-plans/
    ├── operations/
    ├── references/
    └── harness/
```

## Complete harness flow

1. **Assess:** read-only discovery records current capability and risks in [`docs/harness/assessment.md`](docs/harness/assessment.md).
2. **Choose a tracer:** [`docs/harness/tracer-workflow.md`](docs/harness/tracer-workflow.md) names one representative change and its evidence.
3. **Bootstrap:** establish the root map, architecture entrypoint, deterministic commands, manifest, validator, and learning ledger.
4. **Specify intent:** own required behavior in [`docs/product-specs/status-summary.md`](docs/product-specs/status-summary.md).
5. **Maintain design knowledge:** explain the system design, rationale, constraints, and verification status in [`docs/design-docs/status-summary.md`](docs/design-docs/status-summary.md).
6. **Record decisions:** keep discrete architectural choices in [`docs/adr/0001-pure-summary-core.md`](docs/adr/0001-pure-summary-core.md), separate from design documentation.
7. **Plan complex work:** maintain progress, decisions, verification, and recovery in [`docs/exec-plans/active/status-summary.md`](docs/exec-plans/active/status-summary.md).
8. **Deliver:** implement the smallest change, run focused checks, then run the full repository gate.
9. **Observe:** use structured output and [`docs/operations/observability.md`](docs/operations/observability.md).
10. **Review evidence:** fill [`docs/harness/evidence-template.md`](docs/harness/evidence-template.md) and review against intent and standards.
11. **Capture learning:** record repeated friction in [`docs/harness/learning-ledger.md`](docs/harness/learning-ledger.md).
12. **Garden and report:** run read-only hygiene and quality checks, updating trends only from evidence.
13. **Increase autonomy carefully:** apply the gates in [`docs/harness/governance.md`](docs/harness/governance.md).

## Run the example

From this directory:

```powershell
python scripts/setup.py
python scripts/start.py
python scripts/check.py
python scripts/test.py
python scripts/harness-validate.py .
python scripts/garden.py
python scripts/quality_report.py
```

All scripts use the Python standard library. `start.py` performs a finite self-check rather than starting a persistent server, so the example is safe to run in CI or an isolated worktree.

## Adoption guidance

1. Assess the target repository first.
2. Select a real tracer workflow.
3. Reuse existing commands and authoritative documents.
4. Copy only artifacts that close a demonstrated gap.
5. Lower manifest claims when evidence is weaker.
6. Keep production access, secrets, and irreversible actions behind explicit human gates.

## Source boundary

This is a repository-authored interpretation and example. OpenAI's article is background evidence, not a claim that this exact layout is OpenAI's internal repository. See [`docs/references/index.md`](docs/references/index.md) for provenance.
