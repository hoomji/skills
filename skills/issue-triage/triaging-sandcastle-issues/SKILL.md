---
name: triaging-sandcastle-issues
description: Triage GitHub issues for the Sandcastle agent loop in unified-request — label ready-for-agent vs ready-for-human, write new issues an agent can actually finish, or check whether a closed run's acceptance criteria really held.
---

# Triaging Sandcastle Issues

## Overview

Sandcastle agents run inside a Docker container (`.sandcastle/Dockerfile`) with an Anthropic key and a **fine-grained GitHub PAT** — strong at writing code and talking to the GitHub API, boxed in everywhere else. The capability envelope below is the actual boundary; don't guess at it.

**Triage rule:** an issue is `ready-for-agent` only if every acceptance criterion can be satisfied by _commits on a sandcastle branch plus GitHub API calls_. Anything requiring a merge, a CI verdict, a push to another PR's branch, a workflow file, an LFS blob, or a live provider is `ready-for-human`.

## The label that actually gates

`.sandcastle/plan-prompt.md` selects issues with:

```
gh issue list --state open --label Sandcastle --limit 100
```

**`Sandcastle` is the only filter. `ready-for-agent` is decorative to the loop.** To stop the planner selecting an issue, remove the `Sandcastle` label — relabelling alone changes nothing.

## Capability envelope

| Capability                                                                           | Status | Mechanism                                                                                                                                                                      |
| ------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Write code, run `yarn test:unit` / `lint:check` / `format:check` / `typecheck:build` | ✅     | in-container                                                                                                                                                                   |
| `gh issue comment` / `close` / `edit`                                                | ✅     | PAT                                                                                                                                                                            |
| `gh pr comment`, `gh pr edit --body/--title`                                         | ✅     | PAT                                                                                                                                                                            |
| Commit + merge into `henry-sandcastle`                                               | ✅     | merger phase only                                                                                                                                                              |
| `git push` from an **implementer**                                                   | ❌     | no credentials — `git fetch has no credentials in this sandbox`; implementers run `--no-fetch` against local refs                                                              |
| Push anything under `.github/workflows/`                                             | ❌     | PAT has no `workflow` write; the whole push is rejected                                                                                                                        |
| Read CI results / re-run a job                                                       | ❌     | the PAT has no Actions permission — the API returns **403** regardless of whether CI itself is healthy                                                                         |
| Merge to `develop`, or `gh pr merge`                                                 | ❌     | needs review + CI; sandbox merges only into `henry-sandcastle`                                                                                                                 |
| Open a **new** PR                                                                    | ❌     | #1817 already owns `henry-sandcastle → develop`; `gh pr create` refuses a duplicate, so all work funnels into that one cumulative PR                                           |
| `git-lfs`                                                                            | ❌     | not installed; committed cassettes smudge to dirty pointers every run and are left unstaged, and the `.husky/pre-push` LFS hook exits 2 (the merger pushes with `--no-verify`) |
| `k6`                                                                                 | ❌     | not installed; k6 specs get edited, never executed                                                                                                                             |
| Live e2e (gateway :3007, Postgres, Redis, provider keys)                             | ❌     | no stack in the container                                                                                                                                                      |
| `@swc/core-linux-arm64-gnu`                                                          | ⚠️     | absent from the copied host `node_modules`; every agent must install it before jest runs at all                                                                                |
| Memory                                                                               | ⚠️     | ~3.9 GB — `--runInBand` OOM-kills the unit suite around 272 suites; `--maxWorkers=2` completes                                                                                 |

## Acceptance-criteria phrases that mean `ready-for-human`

Scan the AC list for these. One hit is enough.

- "merged", "lands on `develop`", "reaches `develop`", "closes once … on develop"
- "green", "CI passes", "re-run on the current Node pin", "real CI verdict"
- "rebased onto", "PR #N is reduced to", "pushed to #N" — anything mutating another PR's branch
- "workflow", "scheduled job", "CI-stored credential", "repository secret"
- "recorded cassette", "stored via Git LFS"
- "live e2e", "against staging", "k6", "Grafana Cloud"

## Writing issues the agent can finish

Split the halves. The code is agent work; the queue mechanics are not.

- ❌ _"Land the Nodies fix and merge #1293."_ — half impossible, so it closes half-done.
- ✅ _"Add a Nodies null-result test that fails against `develop`'s behaviour"_ + a separate human issue _"Rebase and merge #1293."_

An AC that needs a CI verdict is a human AC even when CI is perfectly healthy — the sandbox cannot read Actions at all. Say so in `Blocked by` rather than leaving the agent to discover it and substitute a local run.

## Reading a run that went wrong

Two signatures decide whether a closed issue needs relabelling, not just reopening:

- A **rubber stamp** — closed `COMPLETED` while the implementer's own comment says an AC is still open. The merger closes with `gh issue close --comment "Completed by Sandcastle"` **regardless of unmet ACs**, so trust the comment over the state.
- A **blind spot** — a test the agent edited but flagged as "could not run". Take it literally: #2084 edited two k6 specs it could not execute, and both were red in CI on the next push. Anything needing `k6`, `git-lfs`, or a live stack is unverified by construction, not merely unlucky.

Either one means: reopen the issue, or relabel it `ready-for-human` with the gap named in a comment. For everything else about a finished run — recovering an **orphan**'s uncommitted work, diagnosing a stall, getting the branch green — `salvage-sandcastle-run` runs the full pass.

Logs: `.sandcastle/logs/sandcastle-issue-<n>-{implementer,reviewer}.log`, plus `henry-sandcastle-{planner,merger}.log`. The merger log is the record of every GitHub write the loop performed.
