# Architecture map

## System boundary

The example owns a pure status-summary domain function plus repository-local commands and documentation that demonstrate an agent-ready engineering lifecycle. It has no network dependency, persistent datastore, secret, or production integration.

## Components

| Component | Responsibility | May depend on |
| --- | --- | --- |
| `src/status_summary.py` | Domain types and deterministic summary calculation | Python standard library only |
| `src/app.py` | CLI adapter and structured output | `src/status_summary.py` |
| `scripts/` | Stable setup, start, validation, testing, hygiene, and reporting entrypoints | `src/`, `tests/`, repository docs |
| `tests/` | Behavioral and structural verification | public `src/` interfaces |
| `docs/` | Intent, decisions, plans, operations, evidence, and governance | repository paths and explicit HTTPS sources |

Dependency direction is `docs/requirements -> src/domain -> src/adapter`, while tests and scripts may observe the public layers. Domain code must not import scripts, tests, or operational tooling.

## Data and control flow

```text
JSON-like check input
        |
        v
parse_check_results()  -> validated CheckResult values
        |
        v
summarize()            -> deterministic StatusSummary
        |
        v
to_dict()              -> structured JSON output and test evidence
```

## Runtime and observability

`python scripts/start.py` performs a finite self-check and emits newline-delimited JSON. Every event carries a task namespace derived from the current Git worktree path. There is no shared mutable runtime state to tear down.

## Protected invariants

- Domain code uses only the Python standard library.
- `src/status_summary.py` does not import adapter or script modules.
- All accepted states are explicit; unexpected states fail at the boundary.
- Capability claims at `verified` or `automated` cite reproducible evidence.
- R2 through R4 actions remain outside automated example commands.

## Decisions

See [`docs/adr/index.md`](docs/adr/index.md). Architectural changes require a new or superseding ADR rather than silent edits to history.

## Design documentation

See [`docs/design-docs/index.md`](docs/design-docs/index.md) for indexed system and feature designs, rationale, constraints, alternatives, and verification status. Design docs explain the design; ADRs remain the separate record of discrete architectural decisions.
