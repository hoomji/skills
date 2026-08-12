# Harness-bootstrap runs

## 2026-08-11 — paired repository trials

The first real bootstraps were applied as unstaged R1 change sets to the two assessment
repositories:

- [`unified-request`](../../docs/assessments/unified-request-initial-harness-bootstrap.md)
  at `henry-sandcastle@dcee73d10`;
- [`auto-route`](../../docs/assessments/auto-route-initial-harness-bootstrap.md) at
  `henry/ai-workflow@7d03534`.

Both produced a root map, architecture pointer, deterministic setup/check/test/validate
commands, tracer workflow, manifest, learning ledger, and dependency-free validator.
Both validators reproduce `PASS` with zero warnings. A read-only second pass found no
missing minimum artifact and proposed no additional bootstrap edit.

The contrast exercised adaptation rather than template copying: `unified-request` added
Yarn entrypoints and a root architecture map around an existing provider skill;
`auto-route` reused its Makefile and `ai/ARCHITECTURE.md` around its ready-for-agent issue
loop. Existing dirty state and repository-specific guidance survived both runs.

One evidence limitation remains explicit: the original `unified-request` transcript was
not retained, so its report was reconstructed from the live unstaged tree and reproduced
validator output. No unavailable command result is claimed.

Milestone 2 is complete on these paired trials. The broader five-case matrix remains
hardening work rather than a prerequisite for beginning the daily lifecycle milestone.

## 2026-08-11 — validator implementation suite

The zero-dependency validator was exercised through its command-line seam against
temporary repositories. Result: **13/13 passing**.

Covered behavior:

- a valid minimum contract passes without mutating the target tree;
- broken paths and missing Make targets fail with remediation;
- required verification commands cannot remain unknown;
- an unknown start command requires evidence that no startable runtime exists;
- opaque installed-tool commands must be exposed through a statically checkable stable
  entrypoint;
- guidance links cannot escape the repository through `..`;
- verified capabilities need evidence and statuses must use the shared vocabulary;
- enforced policies need remediation;
- `CLAUDE.md` routes to `AGENTS.md`;
- commands in the manifest are advertised verbatim in the shared map.

The assessment inventory has a separate passing regression test for local default-ref
divergence. These behavior tests preceded the paired trials above and remain the
deterministic regression suite for the validator.
