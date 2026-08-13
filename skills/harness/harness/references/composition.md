# Engineering-skill composition

Wrap an installed Matt Pocock engineering skill when it already owns the method. Keep
harness-specific inputs and evidence around it instead of rewriting its procedure.

| Need | Preferred capability | Claude Code plugin name |
|---|---|---|
| Stress-test a fuzzy goal | `grilling` or `grill-with-docs` | `mattpocock-skills:grilling` or `mattpocock-skills:grill-with-docs` |
| Establish domain language | `domain-modeling` | `mattpocock-skills:domain-modeling` |
| Turn discussion into a spec | `to-spec` | `mattpocock-skills:to-spec` |
| Split work into tracer tickets | `to-tickets` | `mattpocock-skills:to-tickets` |
| Explore a large unknown area | `wayfinder` | `mattpocock-skills:wayfinder` |
| Diagnose a bug | `diagnosing-bugs` | `mattpocock-skills:diagnosing-bugs` |
| Implement test-first | `tdd` | `mattpocock-skills:tdd` |
| Implement from a spec | `implement` | `mattpocock-skills:implement` |
| Review standards and spec fit | `code-review` | `mattpocock-skills:code-review` |
| Resolve merge conflicts | `resolving-merge-conflicts` | `mattpocock-skills:resolving-merge-conflicts` |

At runtime, use the installed name exposed by the active agent. Codex installations may
expose the unprefixed skill; Claude Code’s plugin exposes the namespaced form. If the
preferred skill is unavailable, perform the narrow workflow directly and state the
fallback in the evidence bundle.

The harness skill retains responsibility for repository grounding, prerequisite gates,
risk boundaries, artifact placement, and evidence reporting.
