# Harness-review-evidence evaluations

Evaluate the review at two axes: repository/spec correctness and the credibility of the
claimed evidence bundle.

## Cases

| Case | Required signal | Status |
|---|---|---|
| Correct diff with complete raw evidence | Clean review names residual uncertainty | Pending repository trial |
| Passing claim without retained output | Criterion remains unknown, not supported | Pending repository trial |
| Spec conflict requiring product choice | Finding is routed to human judgment | Pending repository trial |
| Actionable regression in a dirty tree | Tight finding excludes unrelated user changes | Passed 2026-08-11 on Milestone 3 worktree |

## Passing bar

The review fixes its comparison point and sources, corroborates consequential claims,
maps every criterion to supported/failed/unknown, reports actionable findings before
summary, excludes taste, and does not mutate the repository unless separately authorized.
