---
name: slack-ingest
description: Run the Slack wiki ingest by hand, for every ingest channel or only the channels named, with its Linear filing and the #linear-new-items post.
disable-model-invocation: true
argument-hint: "[#channel ...] [since <date>]"
---

# Slack ingest, by hand

Run the Slack phase of the daily wiki ingest now, with Henry present. The routine itself is two files, and they stay the authority on every rule:

- `~/.claude/scheduled-tasks/_phases/daily-slack-wiki-ingest.md`: the steps, the cursors, the blast radius.
- `~/.claude/scheduled-tasks/_shared/linear-feed.md`: filing HOP issues and the daily feed post.

Read both in full, and the two contracts they point at (`_shared/unattended.md`, `_shared/wiki-vault.md`), then follow the phase file's steps 1 to 7 with the changes below. Work from `/home/coolhenrylinux/projects/obsidian/Hopscotch`.

This skill states only what a by-hand run changes.

## Scope: the argument

- **No channel named:** every `mode: ingest` row, exactly as the scheduled run.
- **Channels named** (`#name` or a `C…` id, one or several): a **scoped** run.
  - Match each name to its row in `wiki/.slack-registry.json`. Read only those rows.
  - Skip step 2's discovery sweep and the liveness check.
  - Every other row stays byte-for-byte as it was: its cursor, its mode, its note.
  - Step 6b handles only the action items that came from the named channels, plus the feed's "Reading the answers" step. Leave other `queued` ledger entries for the scheduled run.
- **`since <date>`:** read the named rows from that date instead of from `last_ts`. Messages older than the row's cursor were already ingested once, so integrate only what the wiki lacks, and leave the cursor wherever is later: its old value or the newest message read.

A named channel the registry does not let you read is Henry's call, and he is here, so ask him once and act on the answer:

| The row is | Ask |
|---|---|
| missing, and it is a channel | Add it as `ingest`, and read back how far: 7 days, or his date? |
| missing, and it is a DM or group DM | Add it as `ingest`, or read nothing? A DM enters a git-tracked vault. |
| `pending` | Set it to `ingest` and read it, or leave it? |
| `skip` | Read it this once (mode stays `skip`, cursor advances), or set it to `ingest`? |

## A second run on the same day

The scheduled run may already have written today's files. Check `scripts/.runs/<today>-slack*.md` first.

- **If the newest one is under 20 minutes old, or the registry's mtime is,** a run may be live. Two writers on one cursor double-ingest. Tell Henry and wait for his go.
- **Snapshot, source page and report take the next free suffix together:** `raw/slack/<today>-slack-daily-2.md`, `wiki/sources/slack/slack-daily-<today>-2.md` (its `source_file` names that snapshot), `scripts/.runs/<today>-slack-2.md`. With no earlier run today, use the unsuffixed names.
- **Ledger keys** take the new source page's basename, so they cannot collide with the morning's.

## The feed post

`linear-feed.md` allows one post per routine per day, so the team hears once. A by-hand run keeps that promise through Henry:

- **`posted` has no `slack/<today>` key:** post as the file says and record the key.
- **It has one, and this run created an issue or left a "Needs a decision":** show Henry the post's text and ask whether to send it. On yes, post it and record it under `slack/<today>-2` (then `-3`), a key the "Reading the answers" step still finds. On no, put the text in the report under `## Feed (not posted)`.
- **It has one, and this run created nothing:** post nothing.

## Bookends and git

Run `bash scripts/wiki_preflight.sh` before the first log append and `bash scripts/wiki_postflight.sh` after the last wiki write. Commit nothing: the daily wiki fix commits the day's tree.

## Done

A run is done when all of these hold. Check each before reporting.

1. Every conversation in scope has a durable outcome: its messages are in the snapshot, or its skip and the reason are in the run report.
2. Each of those rows' `last_ts` is at the newest message read, and no row outside the scope changed (`git diff wiki/.slack-registry.json` shows only the rows in scope, plus `last_discovery` on an unscoped run).
3. Every qualifying action item from this run has a ledger entry with a status, and each created issue's line on the source page carries its `→ [HOP-n](url)` link.
4. The feed is settled one of the three ways above.
5. The run report file exists.

Then tell Henry, in the chat: the channels read and the message count for each, pages created and updated, each HOP issue created or linked with its link and whether its Slack thread synced, the feed outcome, and anything left `queued` or `skipped` with the reason.
