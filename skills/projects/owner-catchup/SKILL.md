---
name: owner-catchup
description: Owner catch-up brief — processes Gas City mail first and surfaces what matters in it, then what landed on high-priority work (epics and the work ledger's story stages, CI/CD, merging, Gas City) since a cutoff, and the owner's action items, each with an exec summary to rule on.
disable-model-invocation: true
---

# Owner catch-up

Write the owner a **brief**: what *landed* since the cutoff on work that matters, and what only the owner can settle. The owner reads it cold, between other things — every line must stand on its own without opening a link.

Cutoff: the argument if given (`24h`, `since friday`, a date); else the last catch-up's timestamp in `dispatch/ledgers/decisions.tsv` (phase `catchup`); else 48h.

## 1. Process Gas City mail first

Mail is where escalations, blocked lanes and mayor digests arrive, and an unread inbox hides them under hourly repetition. Clear it before anything else so the rest of the brief builds on what the mail said. The full method is [`gc-mail-backlog`](../gc-mail-backlog/SKILL.md); this is the catch-up pass.

1. **Shape it.** `gc mail count`, then a histogram by sender and subject:
   `gc mail inbox --json | jq -r '(.messages // .)?[] | "\(.from)\t\(.subject)"' | sort | uniq -c | sort -rn`
2. **Read the signal.** `gc mail peek <id>` for every one-off subject, plus one example from each repeated group. Signal = escalations (`ESCALATION`, `[HIGH]`), BLOCKED receipts, credential or billing walls, mayor digests, stranded or unpushed work, and anything that names the owner or a reserved subject.
3. **Check it is still live.** A reminder about a gate, bead or PR is live only if `gc bd show <id>` / `gh pr view` says it is still open. Gate reminders often outlive their gate.
4. **Route each signal message.** Owner-only items go to step 4. Landed or at-risk facts go to LANDED or AT RISK, with the message id as evidence. Anything else the mayor can act on gets a bead, or is named in AT RISK.
5. **Resolve it.** Once a message's signal is recorded, `gc mail mark-read <id>`. Then archive the stale and repeated groups by filter: `gc mail archive --to <recipient> --subject-prefix '<prefix>' --dry-run`, then the same without `--dry-run`. Archive caps at 100 per run, so loop until `gc mail count` stops falling. Never bulk-archive a group whose example you have not read.

Done when: unread is zero, or every remaining unread is named in the brief with the reason it was kept. Every signal message is routed, and you know how many were resolved, how many were stale and how many were surfaced.

## 2. Harvest landed work

Delivery is the remote head, never a closed bead — a merged PR or a pushed sha is the only evidence that counts. Sweep every source; a source you could not read is named in the brief as a gap.

- **Gateway-LLM PRs** — `gh pr list -R Uniblock-dev/Gateway-LLM --state merged --search "merged:>=<cutoff>" --json number,title,labels,mergedAt,body`. Also `develop`→`main` promotions (deploys).
- **Beads** — `gc bd list --status closed` for rigs `gateway-llm` and `city` since the cutoff; read `close_reason` and NOTES with `gc bd show`. Keep epics, P0/P1, and anything whose close names a PR. Cross-check each claimed delivery against `git ls-remote` or the merged PR.
- **City** — `git -C ~/city log --since=<cutoff>` (skip `grades:` commits), `dispatch/ledgers/decisions.tsv` rows since the cutoff, and the mail harvest from step 1.
- **CI/CD and merging** — `dispatch/ledgers/merge-queue-health.jsonl` and `mergify.jsonl`, the latest `develop` and `main` workflow runs (`gh run list -b develop -L 5`), billing walls, gate or ratchet changes.
- **Work ledger** — the per-story stage of every BMad story in Gateway-LLM and Hoppy-city, the same data the `/work-ledger` pane shows. Run it fresh into your scratchpad (about 20 s, read-only): `~/city/dispatch/work-ledger.py --out <scratch>/ledger.json > /dev/null`. Diff it against the snapshot the last catch-up saved, `~/.cache/work-ledger/catchup.json`:
  ```
  S='[.rigs[] | .rig as $r | .initiatives[] | .slug as $i | .epics[] | .stories[] | {key: "\($r) \($i) \(.ref)", value: .stage}] | from_entries'
  jq -n -r --slurpfile a ~/.cache/work-ledger/catchup.json --slurpfile b <scratch>/ledger.json \
    "(\$a[0]|$S) as \$o | (\$b[0]|$S) | to_entries[] | select((\$o[.key] // \"new\") != .value) | \"\(.key)\t\(\$o[.key] // \"new\") -> \(.value)\""
  ```
  Stories that moved to `landed` or `in_pr` are epic progress; cite the epic PR (`.epics[].prs`), since `landed` is the ledger's reading, not evidence on its own. With no snapshot yet, report each initiative's `counts` as a baseline and say so. Each rig's `errors` entries are gaps: name them in GAPS, and a `tickets.py status <initiative>` error means that initiative's tree went unread, so its counts come from beads alone. The `attention` rows feed step 4 (`who: "you"`) and AT RISK (`who: "mayor"`).

Filter CodeRabbit before counting anything.

Done when: every source above was read or named as a gap, and every kept item carries its evidence (PR #, sha, or bead id).

## 3. Rank by consequence

Keep an item only if it moves one of: an epic's completion, production behavior (deploys, money paths, customer data), the merge pipeline (CI gates, Mergify, red `develop`), or the fleet's capacity (hosts, providers, quota). Collapse a train of PRs into one line per outcome — "Epic 51: 7/9 stories merged; pricing coverage now live on develop" beats seven PR titles. Take the n/m from the work ledger's epic `counts` (landed out of the epic's stories), not from counting PRs.

Done when: each surviving line names an outcome, not an activity.

## 4. Collect action items

An action item is something only the owner can settle: the four reserved subjects (money, customer data, credentials/repo admin, product scope — see `agents/mayor/prompt.template.md` "Authority and parking"). Sources: the mail harvest's owner items, open `OWNER-DECISION:` beads, beads assigned to `owner`, PRs awaiting the owner's review, BLOCKED receipts naming a credential, and the work ledger's `attention` rows with `who: "you"` (stories at `your_call`: a hitl or hold-owner label, or a human gate; `text` says which). Group ledger rows by epic, so five hitl stories in one epic are one line, not five. A hitl story that is a release or account step the owner already scheduled is not a new decision: check rulings before asking.

Before listing one, verify it is still live — its PR not merged, its time box not expired — and that the owner has not already answered it. For a PR, read its comments for the owner's `/approve <sha>` or `/review approve <sha>`; fleet PRs are authored as the owner's account, so a comment is how they approve. Compare that sha with the current head, and write each PR line as "approved at <sha> ✓", "approved at an older head, re-approve at <head>", or "not yet approved". For a decision, read `gc bd comments` on the gate and on the bead it blocks, and grep `dispatch/ledgers/rulings.tsv`. If a ruling is already recorded, resolve the gate and don't ask again. Owner queues go stale fast; drop dead items and say how many you dropped.

Split them into:
- **Actions** — needs the owner's hands or credentials (rotate a key, approve a deploy). State the exact command or click.
- **Decisions** — needs the owner's judgement. Each gets an **exec summary**:
  - *Question* — one sentence.
  - *Context* — why it came up, what it touches, in 2–3 lines.
  - *Options* — 2–3, each with its cost.
  - *Recommendation* — one option and why.
  - *If no ruling* — what happens by default, and by when.

Done when: every live owner item has a recommendation and the reader could rule on it without opening anything.

## 5. Deliver

Reply in this shape, times in Toronto time:

```
Catch-up since <cutoff, Toronto>

MAIL            ← n read · n stale archived · n surfaced (the surfaced ones, one line each, most important first)

NEEDS YOU (n)
  Actions: …
  Decisions: …   ← exec summaries, highest stake first

LANDED
  Epics · CI/CD & merging · Gas City · Other

AT RISK          ← red develop, stalled lanes, walls, work-ledger mayor rows (relaunch, unarmed gate, draft epic PR, stalled); one line each
GAPS             ← sources not read, work-ledger rig errors
```

Lead with the MAIL line and then NEEDS YOU, even when empty ("nothing needs you"). Then append `<UTC ts>\tcatchup\tbrief\t<n mail processed/surfaced, n landed, n owner items>\t-\tdelivered` to `dispatch/ledgers/decisions.tsv` so the next run knows its cutoff, and save this run's ledger as the next run's baseline: `cp <scratch>/ledger.json ~/.cache/work-ledger/catchup.json`. Save it only after the brief is delivered, so a run that stops partway does not move the baseline.
