---
name: closing-completed-prds
description: Close the PRDs and SPECs whose implementation has actually landed, and label the ones still in flight. Use when the user is triaging specs or parent tickets, asks which PRDs are done or can be closed, or cannot tell a delivered PRD from an abandoned one.
---

# Closing Completed PRDs

A PRD or SPEC is a parent ticket. It is finished when the work implementing it has landed, and the tracker will not tell you that — establishing it is the whole job.

## A decision is not a delivery

Recorded intent looks like completion and is not. An ADR committed for the PRD, a slice issue closed, a body edited to read "done" — none of these put code in the tree. Name the PRD's concrete deliverable before judging it: a module, script, endpoint, CLI flag, CI job. Then confirm that artefact exists.

The trap in its sharpest form is a PRD whose ADR is committed and whose implementation was never written. The decision landed; the delivery did not.

## Where landed is measured

Against the branch the work actually merges into — the **integration branch** — which is often not the default branch. Where an agent loop lands work on a long-lived branch that reaches `develop`/`main` through one cumulative PR, issues are closed at the integration branch, and that PR carries already-closed work onward. An open PR is therefore no reason to keep such an issue open.

Read the repo's close convention from the issue-tracker config and confirm the branch before judging anything. Measure against the default branch instead and finished work reports as untouched.

Then confirm the commits are reachable from the **pushed** branch rather than your local one:

```bash
git fetch origin <integration-branch>
git rev-list --left-right --count HEAD...origin/<integration-branch>
git merge-base --is-ancestor <commit> origin/<integration-branch>
```

A local branch can hold merges that never reached the remote — a push rejected for credential scope (a workflow file under a PAT with no `workflow` write) leaves exactly this state, and the carrying PR reflects the remote. Closing on a local-only commit closes an issue that nothing delivers.

## Rebuilding the slice tree

A PRD closes when every slice implementing it is closed. Slices normally do not name their parent, so rebuild the tree from three sources in descending reliability:

1. **Sub-issue links** — `subIssues` on the GraphQL issue. Authoritative where used, and often used by almost nothing. Check it; don't depend on it.
2. **Commit subjects** — `git log --grep` on the PRD number catches `RALPH: … (#1234)` and `feat(x): … (PRD #1234)`. The strongest signal in practice, because it ties a slice to code.
3. **Title topic match** — sibling issues named for the same feature, e.g. `verify mode: …` beneath a PRD about verify mode. Use it to discover candidates, then confirm each through source 2.

A closed issue that looks like a slice may instead be the PRD's own predecessor, closed as superseded when the PRD replaced it. Establish which way the supersession runs before counting it as delivered work.

## Steps

1. **Enumerate the parents.** Title match on `PRD`/`SPEC`/`RFC`, plus any issue carrying an acceptance-criteria section. Done when every parent is listed with its current labels.

2. **Rebuild each slice tree** from the three sources above.

3. **Run the completion test.** Three conditions, all required, per parent: every slice closed; the named deliverable present on the integration branch; its commits reachable from the pushed branch. Done when each parent is marked complete or incomplete **with the failing condition named**.

4. **Close the complete ones with evidence.** Comment the implementing commits, the ADR recording the decision, and which PR carries the work onward — then close.

   ```bash
   gh issue close <n> --comment "..."
   ```

   A bare close leaves no way to tell a delivered PRD from an abandoned one.

   Where the repo's close convention is undocumented, confirm it with the maintainer before closing a batch, then write it into the issue-tracker config so the next pass inherits the answer instead of re-asking. Closing at the integration branch is a house rule, not a default — infer it from how the slices themselves were closed.

5. **Label what is still in flight.** A parent an open PR delivers gets `has-pr` — use `has-pr-labelling` for the label and the delivers-versus-mentions test.

6. **Report the incomplete ones with the evidence that failed.** "No `PathRegistry` on `develop`", "ADR only, no target", "children still open" — these negative findings are what stop the next pass re-deriving them from scratch.
