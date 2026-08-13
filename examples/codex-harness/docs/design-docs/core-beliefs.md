# Core harness beliefs

- State: Verified
- Owner: Example maintainers
- Last verified: 2026-08-13
- Verification evidence: `AGENTS.md`, `docs/harness/manifest.yaml`, `scripts/harness-validate.py`
- Review trigger: a change to repository guidance, artifact ownership, or harness validation

## Beliefs

### The repository is the durable system of record

Important product intent, design knowledge, decisions, plans, and operating instructions
must survive the conversation that produced them.

### Entry points are maps

`AGENTS.md` and `ARCHITECTURE.md` remain concise. They route agents to focused,
authoritative documents rather than duplicating their contents.

### Artifact types keep separate ownership

Product specs define required behavior. Design docs explain system and feature designs.
ADRs record discrete decisions. ExecPlans coordinate implementation. Evidence proves
claims. One artifact may link another but does not absorb its history.

### Claims follow evidence

A design is `Proposed` until repository behavior or other reproducible evidence supports
it. Verification dates and evidence are visible in the design-doc index.

### Enforcement earns its place

Stable, objective, recurring rules should move into tests, linters, schemas, or CI with
actionable remediation. Subjective or one-off preferences should not become global policy.

### Autonomy is workflow-specific

Permissions expand only when the exact workflow has sufficient validation, isolation,
recovery, and escalation evidence.
