---
name: stacking-open-prs
description: Chain a repo's open PRs into GitHub stacks wherever one genuinely depends on another, and rewrite the PR bodies to match. Use when the user asks to stack or restack PRs, when open PRs are branching off each other's unmerged work, or when another skill needs the needs-versus-collides test.
---

# Stacking open PRs

A **stack** is a chain of open PRs. The bottom targets the trunk, each layer above targets the branch below it, and they merge bottom-up. Every branch rule — required checks, CODEOWNER approval — is enforced on every layer, including mid-stack ones that never touch the trunk. GitHub draws the chain as a stack map in each PR's merge box.

The fleet you are reading is usually already stacked in fact — someone cut a branch off an unmerged branch and opened a PR against `main` anyway. GitHub doesn't know, so the reviewer of the upper PR reads a diff that silently carries the lower one's work, and neither PR says which lands first. Stacking makes the dependency the repo already has visible and enforced.

## Needs, or merely collides

PR B **needs** PR A when B's diff is wrong without A's — it calls a function A introduces, or B's branch was cut from A's.

PR B **collides** with A when they edit the same lines and nothing more. Whoever merges second rebases. That is a conflict, not a dependency.

Stack needs. Leave collisions alone.

## What a stack costs

Bottom-up merging turns every PR beneath a PR into a blocker. A green, approved PR stacked above a stalled one cannot land until the stalled one does. Pay that when the need is real — the upper PR could not have merged first anyway — and you have paid nothing. Pay it for a collision and you have invented a blocker. This is why "these two are related" is not a reason to stack.

## What can't be stacked

- **A fork branch.** Every branch in a stack lives in the same repo.
- **Different trunks.** One stack, one base — `gh pr view N --json baseRefName`.
- **A cycle.** A needs B and B needs A. Fold them into one PR, or split the shared piece into a third PR both sit on.
- **One PR carrying several issues.** There are no layers to chain yet — `rescoping-prs` cuts it into them first.

## Steps

1. **Read the fleet.**

   ```bash
   git fetch origin
   gh pr list --state open --limit 200 \
     --json number,title,body,headRefName,baseRefName,isDraft,author,isCrossRepository
   ```

   Drop the cross-repository ones and note which PRs are already in a stack. Done when every remaining open PR is on the list with its branch and base.

2. **Find the needs.** Ancestry first — it needs no interpretation. One `rev-list` per open branch gives every commit that branch carries beyond the trunk:

   ```bash
   git rev-list origin/main..origin/<branch>
   ```

   B needs A when A's tip (`git rev-parse origin/<A-branch>`) appears in B's list. Those two are already stacked in git and only GitHub is unaware — the safest stack to create, because no branch has to move.

   Where ancestry is silent, read for the need:

   - the body says it — `depends on #41`, `stacked on`, `blocked by`, `builds on`
   - the upper diff uses a symbol the lower diff introduces (`gh pr diff N`) — the strongest code-level evidence
   - the branch name says it — `feat/api-on-auth`, `fix/1780-followup`

   Overlapping files alone is a collision, not an edge. Print the sha, quote, or symbol behind every edge you record.

   Done when every open PR is on the list with its needs named, and every named need carries its evidence.

3. **Chain each stack.** A GitHub stack is a chain, not a tree. Lay each connected piece of the needs graph out bottom-first:

   - **Straight chain** → that is the stack.
   - **Fan-in** — C needs both A and B, and A and B are independent. Any topological order works (A → B → C); you have invented an order between A and B, so say so when you report.
   - **Fan-out** — B and C each need A, independently. Only one can sit above A. Stack the longer chain; the sibling stays unstacked and gets a body line naming what it needs.

   PRs with no edges stay exactly as they are.

   Done when each proposed stack is an ordered list bottom-to-top and every open PR is either in one or explicitly left out with a reason.

4. **Get the go-ahead, then link.** Stacking retargets other people's PRs, so show the proposed stacks with their evidence and the PRs you are leaving alone, and wait for a yes.

   ```bash
   gh extension install github/gh-stack   # once
   gh stack link 41 42 43                 # PR numbers, bottom to top
   ```

   Pass PR numbers. Numbers link and retarget; branch names push.

   Then check the bases took — `gh pr view 42 --json baseRefName` should name the branch below it — and retarget any straggler with `gh pr edit 42 --base <branch>`.

   A layer whose branch does not contain the layer below shows **needs rebase** in the stack map. The fix, `gh stack rebase`, force-pushes someone else's branch and drops their review state, so hand that layer back to its author rather than running it.

   Done when every stack exists on GitHub and each layer's base is the branch beneath it.

5. **Rewrite the bodies.** The stack map already renders the shape. Write what it cannot carry — why this layer sits where it does — inside a marked block, so the next run replaces it instead of appending a second copy:

   ```markdown
   <!-- stack -->
   **Stacked on #41.** Base is `feat/auth`, so the diff below is only the API routes — `requireSession` arrives in #41. Merges after it.
   <!-- /stack -->
   ```

   Add the full table to every layer when the stack has no map to lean on — linking failed, or the branches are in a fork — and when the chain is three or more layers deep, where "stacked on #41" leaves the reader unable to see the top. Bottom row first, so reading down is merge order:

   | Order | PR                  | Why here                        |
   | ----- | ------------------- | ------------------------------- |
   | 1     | #41 Auth middleware | merges first                    |
   | 2     | #42 API routes      | calls `requireSession` from #41 |
   | 3     | #43 Settings UI     | consumes the routes in #42      |

   Edit with `gh pr edit N --body-file -`. Done when every layer's body names what it sits on and the marked block appears exactly once per PR.

6. **Report.** One line per open PR, stacks first:

   ```
   #41 → stack 7, bottom
   #42 → stack 7, layer 2 — contains #41's tip a1b2c3d
   #43 → stack 7, layer 3 — body: "builds on the routes in #42"
   #44 → left out, needs rebase onto #42 before it can join — @author's call
   #45 → left alone, only collides with #42 in package.json
   ```

   Done when every open PR from step 1 has a line.

## Unstacking

A need that turns out to be false comes back apart with `gh stack unstack <stack-number>`, which retargets the layers at the trunk. GitHub leaves behind any PR already queued or on auto-merge. Clear the marked block from each body in the same pass.

Merging is not this skill's job: the stack lands bottom-up through `gh stack merge`, and that call belongs to the authors.
