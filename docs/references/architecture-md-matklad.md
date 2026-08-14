# ARCHITECTURE.md (matklad)

- **Source**: [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) — matklad, 2021-02-06
- **Retrieved**: 2026-08-14
- **Owner**: harness skills (`skills/harness/`)
- **Local-copy reason**: durable summary — the article backs the `architecture` entrypoint
  convention used by the harness manifest and bootstrap skill, and its recommendations
  (concise, low-maintenance, no-hyperlink codemap) are load-bearing for what those skills
  ask repositories to produce. A link alone risks silent drift from the source if the post
  changes or disappears.
- **Consumers**:
  - [skills/harness/harness-bootstrap/SKILL.md](../../skills/harness/harness-bootstrap/SKILL.md) —
    installs the `architecture` entrypoint (`entrypoints.architecture` in the manifest)
  - [skills/harness/harness/references/contracts.md](../../skills/harness/harness/references/contracts.md) —
    names `ARCHITECTURE.md` as the default architecture entrypoint path

## Sourced facts

- Core claim: for projects roughly 10k–200k LOC, an ARCHITECTURE document pays off. The
  main barrier for a contributor isn't writing the patch, it's finding *where* to make the
  change — locating the right place can take ~10x longer than writing the fix itself.
- The document should externalize the mental map an experienced maintainer already carries,
  so occasional contributors don't have to rebuild it from scratch by reading source.
- Recommended structure:
  1. bird's-eye overview of the problem the project solves
  2. a codemap: coarse-grained modules and how they relate
  3. architectural invariants, including invariants stated as an absence ("there is no X")
  4. layer and system boundaries
  5. cross-cutting concerns
- Authoring guidance:
  - keep it short — every recurring contributor will actually read it, so length is a real
    cost, not a nice-to-have constraint
  - don't duplicate implementation detail; link out to focused docs instead
  - revisit only a few times a year — treat staleness risk as a reason to stay high-level,
    not a reason to skip the doc
  - name important files/modules/types by identifier rather than hyperlinking them, so the
    doc keeps working after files move (readers use symbol search instead)
  - writing the codemap is itself a forcing function: it surfaces whether logically related
    components are actually physically adjacent in the repo, and where they aren't

## Repository inference

- This is why `skills/harness/harness/references/contracts.md` treats `ARCHITECTURE.md` as
  a *lazily created* entrypoint name rather than mandating exhaustive content: the source
  material argues for a short, symbol-searchable codemap over a maintained reference doc.
- The "invariants as absence" and "physical adjacency" ideas aren't yet reflected as
  explicit prompts in `harness-bootstrap`; if that skill's architecture-entrypoint guidance
  is deepened later, this reference is the place to check first.

## Freshness

- Static blog post; unlikely to change. Re-check only if `harness-bootstrap`'s
  architecture-entrypoint guidance is revised and needs to re-justify itself against the
  source, or opportunistically during the next harness-garden pass over `docs/references/`.
