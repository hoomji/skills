---
name: owner-catchup
description: Owner catch-up brief — what landed on high-priority work (epics, CI/CD, merging, Gas City) since a cutoff, and the owner's action items, each with an exec summary to rule on.
disable-model-invocation: true
---

# Owner catch-up

Write the owner a **brief**: what *landed* since the cutoff on work that matters, and what only the owner can settle. The owner reads it cold, between other things — every line must stand on its own without opening a link.

Cutoff: the argument if given (`24h`, `since friday`, a date); else the last catch-up's timestamp in `dispatch/ledgers/decisions.tsv` (phase `catchup`); else 48h.

## 1. Harvest landed work

Delivery is the remote head, never a closed bead — a merged PR or a pushed sha is the only evidence that counts. Sweep every source; a source you could not read is named in the brief as a gap.

- **Gateway-LLM PRs** — `gh pr list -R Uniblock-dev/Gateway-LLM --state merged --search "merged:>=<cutoff>" --json number,title,labels,mergedAt,body`. Also `develop`→`main` promotions (deploys).
- **Beads** — `gc bd list --status closed` for rigs `gateway-llm` and `city` since the cutoff; read `close_reason` and NOTES with `gc bd show`. Keep epics, P0/P1, and anything whose close names a PR. Cross-check each claimed delivery against `git ls-remote` or the merged PR.
- **City** — `git -C ~/city log --since=<cutoff>` (skip `grades:` commits), `dispatch/ledgers/decisions.tsv` rows since the cutoff, `gc mail inbox` for mayor digests and escalations.
- **CI/CD and merging** — `dispatch/ledgers/merge-queue-health.jsonl` and `mergify.jsonl`, the latest `develop` and `main` workflow runs (`gh run list -b develop -L 5`), billing walls, gate or ratchet changes.

Filter CodeRabbit before counting anything.

Done when: every source above was read or named as a gap, and every kept item carries its evidence (PR #, sha, or bead id).

## 2. Rank by consequence

Keep an item only if it moves one of: an epic's completion, production behavior (deploys, money paths, customer data), the merge pipeline (CI gates, Mergify, red `develop`), or the fleet's capacity (hosts, providers, quota). Collapse a train of PRs into one line per outcome — "Epic 51: 7/9 stories merged; pricing coverage now live on develop" beats seven PR titles.

Done when: each surviving line names an outcome, not an activity.

## 3. Collect action items

An action item is something only the owner can settle: the four reserved subjects (money, customer data, credentials/repo admin, product scope — see `agents/mayor/prompt.template.md` "Authority and parking"). Sources: open `OWNER-DECISION:` beads, beads assigned to `owner`, PRs awaiting the owner's review, BLOCKED receipts naming a credential.

Before listing one, verify it is still live — its PR not merged, its time box not expired. Owner queues go stale fast; drop dead items and say how many you dropped.

Split them into:
- **Actions** — needs the owner's hands or credentials (rotate a key, approve a deploy). State the exact command or click.
- **Decisions** — needs the owner's judgement. Each gets an **exec summary**:
  - *Question* — one sentence.
  - *Context* — why it came up, what it touches, in 2–3 lines.
  - *Options* — 2–3, each with its cost.
  - *Recommendation* — one option and why.
  - *If no ruling* — what happens by default, and by when.

Done when: every live owner item has a recommendation and the reader could rule on it without opening anything.

## 4. Deliver

Reply in this shape, times in Toronto time:

```
Catch-up since <cutoff, Toronto>

NEEDS YOU (n)
  Actions: …
  Decisions: …   ← exec summaries, highest stake first

LANDED
  Epics · CI/CD & merging · Gas City · Other

AT RISK          ← red develop, stalled lanes, walls; one line each
GAPS             ← sources not read
```

Lead with NEEDS YOU even when empty ("nothing needs you"). Then append `<UTC ts>\tcatchup\tbrief\t<n landed, n owner items>\t-\tdelivered` to `dispatch/ledgers/decisions.tsv` so the next run knows its cutoff.
