---
name: rescoping-prs
description: Cut a PR that has grown past its issue back to the commits that deliver it, and give the rest their own PRs. Use when a PR's diff carries more than its linked issue, when a cumulative agent or Sandcastle branch has to become reviewable PRs, or when the user asks to split, narrow, or re-scope a PR.
---

# Re-scoping PRs

An agent loop produces one branch and one PR. Every issue it worked funnels into the same cumulative branch — Sandcastle's implementers merge into `henry-sandcastle`, and #1817 owns the only PR out of it — so a review that should have been eight small reads arrives as one forty-commit diff spanning eight unrelated issues.

The branch was never really one change. Each issue arrived on its own branch and was flattened into the pile by a merge. Re-scoping is un-flattening: recovering the scoped units the merge erased, so each issue gets the review it was sized for.

## Claim and diff

A PR's **claim** is what it says it delivers — its title, body, and `closingIssuesReferences`. Its **diff** is what it actually carries. Re-scoping is the work of making those two agree, and there are two ways to close the gap:

- **Widen the claim.** Leave the diff alone and list every issue it delivers. One review, N issues, one merge.
- **Narrow the diff.** Cut the PR to its claimed issue and give each stranger its own PR.

Widening is cheaper and is the right answer for a small pile of finished work heading for one merge. Narrow when the pile has a **hostage**: one issue that is red, contested, or waiting on a human, holding every green issue behind it. That is the cost a cumulative PR imposes and the only reason worth paying the split for.

## Three kinds of commit

Every commit between the base and the head is one of:

- **on-scope** — delivers an issue the PR claims
- **sibling** — delivers a different issue, one the PR never claimed
- **residue** — delivers no issue: formatting sweeps, lockfile churn, LFS pointer smudge, merges from the base

Siblings are the split. Residue is dropped or landed separately, and it is worth naming out loud, because a hunk nobody can attribute is the one that silently rides along into a scoped PR.

## Steps

1. **Pin the claim.**

   ```bash
   gh pr view N --json title,body,baseRefName,headRefName,closingIssuesReferences
   ```

   `closingIssuesReferences` is GitHub's own delivery edge and needs no interpretation. A body naming issues it does not close is a claim too — read it, and take the issue's acceptance criteria as the definition of that issue's scope.

   Done when the claimed issue set is written down, each with its ACs.

2. **Attribute every commit.** First-parent history is the record of what was flattened — one entry per branch that was merged in:

   ```bash
   git fetch origin
   git log --first-parent --format='%h %s' origin/<base>..origin/<head>
   git log --no-merges --first-parent --format='%h %s' origin/<base>..origin/<head>
   ```

   The merge subjects carry the issue number (`Merge branch 'sandcastle-issue-2084'`). The second command is what was committed straight onto the cumulative branch rather than merged in — hand-fixes and residue live there.

   Then look for the scoped branches themselves, which usually survive the merge:

   ```bash
   git branch -a --list '*issue-*'
   ```

   A surviving branch is the scoped unit, already tested as a unit. Prefer it over reconstructing one.

   Where the merge subject is silent, attribute from the commit body's `#N`, the branch name, or the files against the issue's ACs. Print the evidence beside each verdict.

   Done when every commit in `base..head` is marked on-scope, sibling with its issue named, or residue with its reason.

3. **Choose narrow or widen, then find the entanglements.** Apply the hostage test from above and say which you chose and why. Widening ends here — update the body to claim every issue, and report.

   Narrowing has one obstacle worth finding before you start cutting: an **entanglement**, where one commit serves two issues, or a later commit repairs an earlier issue's work from inside another issue's branch. Keep entangled issues together in one PR whose claim names both. Splitting a commit by hand throws away the one thing it had going for it — a state something actually ran green on.

   Done when each target PR is an ordered set of commits with its issue list, and every entanglement is either kept together or split with a reason.

4. **Un-flatten.** One branch per target, cut from the base.

   Where the scoped branch survived:

   ```bash
   git switch -c rescope/issue-2084 sandcastle-issue-2084
   git rebase --onto origin/<base> $(git merge-base origin/<base> sandcastle-issue-2084)
   ```

   Where it is gone, replay the merge as a single commit:

   ```bash
   git cherry-pick -m 1 <merge-sha>
   ```

   Then prove the split lost nothing. Every hunk of the original has to land in exactly one scoped branch or on the residue list:

   ```bash
   git diff origin/<base>...origin/<head>   # the original
   git diff origin/<base>...rescope/issue-2084
   ```

   Done when the scoped diffs plus the residue reproduce the original diff, hunk for hunk.

5. **Build each branch alone, then stack what fails.** Run the repo's own gate on every scoped branch — the scripts CI runs, read from `package.json` or the workflow, rather than remembered.

   A branch that passed inside the pile and fails alone has found you a real dependency: it needs a sibling's code. That failure is the evidence, and it beats guessing dependencies from diffs. Chain those branches with `stacking-open-prs`, which carries the needs-versus-collides test and the `gh stack` mechanics.

   Branches that pass alone stay independent PRs off the base. Sharing an origin is not a dependency, and stacking them would hand every one of them the hostage problem the split just removed.

   Done when every scoped branch is green on its own, or is a layer in a stack whose lower layers explain its failure.

6. **Open the PRs, retire the original, report.** Each scoped PR gets `Closes #N`, the issue's ACs, and a line naming the PR it came out of.

   The original then either keeps only the residue or closes with a comment saying where every commit went. Choose deliberately: an agent loop funnels its next run into whatever PR owns `<agent-branch> → <base>`, so closing that PR changes what the loop does next — `triaging-sandcastle-issues` holds the Sandcastle envelope.

   ```
   #1817 (henry-sandcastle → develop), 41 commits
     → #1901  closes #2084   k6 spec fixes           3 commits, green alone
     → #1902  closes #2091   Nodies null-result      5 commits, needs #1901 → stack 12
     → #1903  closes #2093, #2095                    entangled in the billing refactor
     residue  format sweep, 6 cassette pointers, 3 merges from develop — dropped
     #1817    left open with the residue; the next run still funnels into it
   ```

   Done when every commit from step 2 appears in exactly one line of the report.
