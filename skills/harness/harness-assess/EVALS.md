# Harness-assess evaluations

The assessment skill is evaluated at its public seam: a maintainer should be able to
follow every conclusion back to the exact repository state and evidence without the run
mutating that state.

## Initial cases

| Case | Tracer | Expected contrast |
|---|---|---|
| `unified-request` | Add a provider surface and prove it | Mature branch-local command, policy, lifecycle, and hygiene machinery |
| `auto-route` | Deliver a ready-for-agent issue through an isolated stack | Strong domain and architecture content with harness propagation and runtime gaps |

These cases are comparable at the nine-plane vocabulary and qualitative bottleneck
level. Their command coverage and tracer details differ, so the numeric levels are not a
repository leaderboard.

## Dimensions

1. **Scope fidelity** — repository, assessed ref/commit, default-ref relationship,
   dirty state, exclusions, and tracer are explicit and never mixed.
2. **R0 integrity** — no install, service start, cache write, repository edit, or external
   mutation occurs.
3. **Evidence traceability** — every claim cites a repository-relative path at the
   assessed revision, an exact command result, or `unknown`.
4. **Scoring discipline** — nine independent levels use the lowest evidenced capability
   required by the tracer; material sub-capability splits remain visible.
5. **Actionability** — blockers name impact, smallest next capability, and risk class.
6. **Comparison honesty** — comparisons state their equivalence key and do not infer from
   recall or compare evidence gathered under materially different boundaries.
7. **Second-run value** — a rerun distinguishes improvement, regression, ref drift, and
   unchanged gaps instead of repeating the first narrative.

## Passing bar

A run passes when all seven dimensions are satisfied, all nine planes are scored or
explicitly unknown, and a maintainer can dispute the report without rerunning hidden
commands. A paired comparison passes only when it states what is and is not comparable.
