# Harness-bootstrap evaluations

The bootstrap skill is evaluated at two public seams: the human-reviewed preview before
any write, and the repository-local validator after the approved files are prepared.

## Required behavior

1. A stale or different-ref assessment triggers a read-only delta before planning.
2. Preview lists every file operation, reconciliation, exclusion, evidence source,
   validator command, and narrow unstaged change group.
3. Existing guidance and architecture are preserved or explicitly reconciled; templates
   never overwrite them blindly.
4. Setup and verification commands are deterministic. An absent runtime may leave start
   unknown only through an evidenced `startable_runtime: missing` capability; the
   bootstrap remains incomplete with unknown setup/check/test commands.
5. The validator detects broken paths, supported task-runner commands, split guidance,
   unsupported capability status/evidence, incomplete policies, and ledger drift with
   remediation-focused output.
6. A second run is a no-op when the minimum harness is already correct.
7. The skill stops at R1 and leaves all changes unstaged.

## Repository matrix

| Case | Purpose | Status |
|---|---|---|
| `auto-route` assessed ref versus harness-bearing ref | Ref-drift gate, existing conventions, Make targets | Passed 2026-08-11 |
| `unified-request` harness branch | No-op/reconciliation, package scripts, dirty worktrees | Passed 2026-08-11; transcript reconstructed from tree |
| Greenfield application | Missing guidance and architecture | Pending |
| Legacy repository | Incomplete setup and flaky validation | Pending |
| Backend with meaningful runtime telemetry | Non-UI tracer evidence | Pending |
| Frontend application | Browser-visible tracer evidence | Pending |

For every trial, record preview accuracy, changed paths, validator output, dirty-tree
preservation, safe-stop behavior, second-run result, and residual unknowns.
