# References index

External-knowledge captures maintained by `harness-reference`. Each entry names its source,
owner, and repository consumers — see the linked file for provenance detail.

| Reference | Source | Last reviewed | Consumers |
|---|---|---|---|
| [architecture-md-matklad.md](architecture-md-matklad.md) | matklad, "ARCHITECTURE.md" (2021-02-06) | 2026-08-14 | `harness-bootstrap`, `harness/references/contracts.md` |
| [openai-codex-exec-plans.md](openai-codex-exec-plans.md) | OpenAI Codex Cookbook, "Exec Plans for Coding Agents" | 2026-08-14 | `harness-exec-plan` |
| [openai-harness-engineering.md](openai-harness-engineering.md) | OpenAI, "Harness engineering" (2026-02-11) | 2026-08-13 | `skills/harness/`, [harness engineering product spec](../product-specs/harness-engineering-system.md) |
| [openai-agents-sdk.md](openai-agents-sdk.md) | OpenAI Agents SDK guide | 2026-08-13 | `skills/harness/`, [harness engineering product spec](../product-specs/harness-engineering-system.md) |

## Review cadence

- `openai-harness-engineering.md`: review when the harness workflows materially change, or
  annually.
- `openai-agents-sdk.md`: review when the Agents SDK guide or the harness integration model
  changes, or annually.
- The remaining captures are version-pinned to a dated article and need review only when a
  consumer's claims depend on a newer revision.
