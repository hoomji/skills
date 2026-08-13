---
name: has-pr-labelling
description: Label the issues an open PR already delivers, so a triage table separates picked-up work from untouched work. Use when the user cannot tell which issues are already in flight, asks for a has-pr label to be created or applied, or when another skill needs the delivers-versus-mentions test.
---

# has-pr Labelling

Triage roles say what an issue _needs_. None of them say whether someone already took it, so an issue whose PR is written and waiting to merge reads exactly like untouched work. `has-pr` is that missing axis.

## Delivers, or merely mentions

A PR **delivers** an issue when merging it does the issue's work. Every other appearance of the number is a **mention**. Label deliveries.

Mentions outnumber deliveries and a bare `#1234` match cannot separate them. Closing keywords (`Closes #N`) are the exception rather than the rule, so most candidates arrive as raw references that have to be read on their line.

| Mention pattern   | How it reads                                                    |
| ----------------- | --------------------------------------------------------------- |
| Coordination      | "coordinate with #X, which deletes the rules this PR names"     |
| Ancestry          | "base is `develop`, which already carries #X"                   |
| Blocker citation  | "CI never executed — blocked by #X"                             |
| Sibling reference | "same billing block as #Y (#X)"                                 |
| Disclaimer        | "#X has been left open — do not treat this PR as delivering it" |

Search for the disclaimer by hand. A PR whose body states it does _not_ deliver an issue — the work unpushed, or deliberately split off — contradicts what its title and diff suggest, and is the mention most likely to be labelled by mistake.

Partial delivery earns the label: a PR implementing one slice of a parent gets `has-pr`, because the triage question is whether anyone has started, not whether they have finished. Mark which are slices when you report.

## Steps

1. **Pin the label, then its rule.** Create it if absent, and reconcile the name against the repo's existing labels first — a repo with `needs review` or `draft` may already carry this meaning under another word.

   ```bash
   gh label create has-pr --color 1D76DB \
     --description "An open PR implements this (fully or as a slice) — closes on merge"
   ```

   Then write the delivers-versus-mentions rule into the repo's triage-label config, as its own axis rather than a sixth triage role. Done when the label exists exactly once and its meaning is recorded somewhere the next pass will read.

2. **Read the authoritative links first.** `closingIssuesReferences` is GitHub's own delivery edge and needs no interpretation:

   ```bash
   gh api graphql -f query='
   { repository(owner:"OWNER", name:"REPO") {
       pullRequests(states: OPEN, first: 100) {
         nodes { number isDraft title
           closingIssuesReferences(first: 20) { nodes { number state } } } } } }'
   ```

   These are deliveries. Expect few.

3. **Gather the candidates.** Dump both sides once, then intersect:

   ```bash
   gh pr list --state open --limit 200 --json number,title,body,headRefName > prs.json
   gh issue list --state open --limit 300 --json number,title,labels > issues.json
   ```

   Scan each PR's title, body, **and branch name** for `#\d+`, keeping only numbers that are open issues. Branches carry the number where the body omits it (`fix/issue-1780`, `worktree-gh-2041-token-type-filter`). Print the full line each reference sits on — the line is the evidence; the number alone is not.

4. **Apply the delivery test to every candidate.** Two shapes generate most of the noise: a cumulative branch PR that mentions dozens of issues, and any PR whose body carries a review or audit block. Done when every candidate is marked delivers or mentions and you can quote the line behind each verdict.

5. **Sweep merged PRs.** Run the step-2 query at `states: MERGED` and keep any whose linked issue is still open. That is finished work sitting on the board — a different problem from the one this label solves. Report these for closing rather than labelling them.

6. **Label, then report the rejects with their lines.** The rejected mentions are the useful half of the report: they are precisely what a bare-match pass would have got wrong.

## Removing it

`has-pr` comes off when the PR closes unmerged. On merge, let the merge close the issue — a body saying `Closes #1234` does this without help.
