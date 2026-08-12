# Harness-assess runs

## 2026-08-11 — initial paired review

Inputs:

- `unified-request`, assessed at `henry-sandcastle@b44764ea5`; report stored as
  `docs/assessment/2026-08-11-unified-request-harness-assessment.md` in the assessment
  workspace.
- `auto-route`, assessed at `henry/heartbeat-control-durability@2ae706c`; authoritative
  report stored at `docs/generated/assessment/2026-08-11-harness-assessment.md` on
  `henry/ai-workflow`.

Both runs used the same nine-plane contract and R0 boundary. They used different tracer
workflows and safe command samples, so this is a structural comparison, not a ranking.

### Comparison-equivalence key

| Key | `unified-request` | `auto-route` |
|---|---|---|
| Contract | Initial version-1 nine-plane contract | Initial version-1 nine-plane contract |
| Assessed ref | `henry-sandcastle@b44764ea5` | `henry/heartbeat-control-durability@2ae706c` |
| Tracer | Add a provider surface and prove it | Deliver a ready-for-agent issue through an isolated stack |
| Inspection depth | Static inventory and history; safe command probes; three selected Jest guardrail suites | Static inventory and history; installed-tool version probes; no repository gate executed |
| External-read boundary | GitHub issues and labels read-only; Actions/secrets remained unknown | GitHub issues, labels, branch protection, and rulesets read-only |

| Plane | `unified-request` | `auto-route` | Comparative signal |
|---|---:|---:|---|
| Intent | 3 | 2 | Both have structured work; unified-request also verifies its queue graph. |
| Knowledge | 3 | 1 | Auto-route's content is strong, but absent entrypoint/branch propagation blocks cold-start discovery. |
| Execution | 4 | 3 | Both have real gates; unified-request self-guards a CI-equivalent aggregator. |
| Feedback | 3 | 2 | Both prove logic better than runtime; credential-free runtime evidence is the shared gap. |
| Policy | 4 | 3 | Local checks are strong; auto-route lacks a binding merge boundary. |
| Isolation | 2 | 2 | Worktrees exist, but ports, backing state, or telemetry are not fully task-local. |
| Lifecycle | 4 | 1 | Unified-request tracks and checks its queue lifecycle; auto-route's assessed ref cannot reconstruct its working loop. |
| Hygiene | 3 | 0 | Unified-request has a useful drift detector with no active runner; auto-route has stale pointers and no loop. |
| Governance | 2 | 1 | Both lack one shared risk/escalation vocabulary; auto-route's agent authority is largely operator-local. |

### What the initial runs proved

- The plane vocabulary separates meaningfully different repository strengths; neither
  report needed an aggregate readiness score.
- Tracer-based bottleneck ranking produces small, repository-specific next steps rather
  than a generic maturity wishlist.
- R0 can still gather useful evidence when command execution is separated from static
  CI and configuration evidence.

### What the initial runs exposed

- **Ref scope was too easy to discover late.** Both repositories had important harness
  capability away from their default or working branch. Auto-route needed a large delta
  appendix because the assessed and storage refs differed.
- **Comparison was underspecified.** Each standalone report correctly refused a
  recall-based comparison, but the skill had no comparison key or paired-run artifact.
- **Plane floors needed sharper scope.** Unit feedback versus runtime feedback, and local
  enforcement versus merge enforcement, can differ by multiple levels inside one plane.
- **Citation portability mattered.** A report stored outside the assessed repository can
  make relative links resolve against the wrong tree.

### Revisions made from the evidence

- The inventory now reports locally known default-ref divergence and worktree count.
- The skill freezes assessed ref/commit and storage ref before scoring and forbids mixed-ref
  scores.
- Findings record tracer scope and material sub-capability splits.
- Reports carry a comparison-equivalence key and use revision-stable citations.
- The shared finding schema now aligns on numeric level, confidence, scope, present
  capability, and R0–R4 risk.

Milestone 1 is complete on this evidence. The next validation gap is broader repository
coverage from the specification's five-case matrix; that is follow-up hardening, not a
blocker for the minimum bootstrap milestone.
