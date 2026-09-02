# Probes

One entry per check: the command, the pass condition, and the trap that makes the probe
lie. Run from the city root. Every command here is read-only.

## Autonomy

**Wake ticks.** `gc order history <name>` for every wake the contract names. Pass: a
run within two intervals. Trap: read the full `gc order list --json`, never a
`head` of the table — a truncated table once read as "mayor-wake missing" while
`history` showed it ticking; and a file under `orders/` with a stale "DISABLED"
header is still scanned. `gc order check`
says which are due now.

**Standing authority.** Read the contract. Pass: dispatch, push, PR, merge gate, park
protocol, sweep budget each stated; park protocol unsets `gc.routed_to`,
`gc.session_id`, `gc.session_name` before setting status. Trap: status-only parking
reverts in under a minute because the dispatcher reads metadata.

**Lane caps.** `gc session list --json` grouped by provider/template, versus the cap in
the contract. Pass: live ≤ cap per lane. Trap: `gc status` says "scaled max=unlimited"
for pools regardless of the contract; the contract cap is enforced by nobody.

**Merge policy.** `gc config show | grep -A12 'github.pr_monitor'`. Pass:
`merge_queue = "observe"` unless the owner granted more; no script in the city passes
`--create-repair-beads` without an author gate (`grep -rn create-repair-beads`).
Trap: the monitor has no author field, so a bare backfill repairs foreign PRs.

**Stranded work.** In each rig: `git worktree list --porcelain | grep -c detached` and
`git for-each-ref refs/heads --format='%(refname:short) %(objectname)'` then
`git branch -r --contains <sha>` per tip. Pass: no ripe tip (≥1 commit, stable) that no
remote ref contains. Trap: a refs/heads watcher misses detached HEADs.

## Context

**Window knobs.** `jq .env .gc/settings.json`; then the model each lane resolves to:
`claude -p 'reply with the model id only'` inside the rig for unpinned lanes, and
`ps -o args= -p <pid>` of a live session for pinned ones. Pass: advisory/urgent
percentages sit against the window that model actually has. Trap: the comment above
`[providers.claude]` describes the owner's global settings, which can change without
touching the city.

**Hooks.** `jq .hooks .gc/settings.json`. Pass: PreCompact → `gc handoff --auto`;
SessionStart carries the `GC_STARTUP_PROMPT_DELIVERED` guard on the backstop;
UserPromptSubmit hooks run under `gc hook run --timeout`. Trap: the primary prime
delivers 0 bytes on SessionStart; the guard is what keeps the backstop from
double-delivering — deleting either breaks a different session start.

**Prompt weight.** `wc -c agents/*/prompt.template.md *STATE*.md` and the memory index
(`~/.claude/projects/<slug>/memory/MEMORY.md`). Pass: the state file is under ~10 KB
and holds no line a probe reproduces (session counts, PR states, dates); archives live
in `archive/`, not beside the live file. Trap: a state file that restates fresh counts
is a cache that is stale by the next tick.

**Handoff path.** `grep -n 'session reset\|gc handoff' <contract> agents/*/prompt*`.
Pass: handoff named, reset absent or explicitly forbidden against a live controller.

## Efficiency

**Provider pins.** For each `[providers.*]`: `gc config show` for the resolved
`option_defaults`; then the launched reality — `ps -eo pid,args | grep -E
'claude|codex|agy'` for flags, and the provider's own log (`grep -a 'model override'
~/.gemini/antigravity-cli/cli.log` for agy). Pass: launched model/effort equals the
pinned intent. Trap: gc hardcodes codex flags and ignores the model key; a PATH shim
may be the real pin — `which codex` and read its header.

**Idle sessions.** For each active session, `gc session peek <id> | tail -5 |
sha256sum`, twice, ≥2 minutes apart. Pass: hash changes, or the session is a named
always-on session at its composer by design. Trap: `last_active` is identical across
all sessions and proves nothing; a session can report active while logged out ("Not
logged in") or quota-blocked — read the tail text, not just the hash.

**No-consumer roles.** Diff `gc session list --template <t>` against the config's own
comments ("no consumer as of …"). Pass: a role the config says is unused has no live
sessions. Two `claude-high` sessions under a block that says "no consumer" is drift in
one direction or the other.

**Usage facts.** `gc costs`. Pass: every lane that ran today has rows. Trap: only
codex writes usage facts on gc 1.4.1; claude lanes are unmetered here and must be
read from the owner's plan dashboard.

**Store and logs.** `gc doctor` rows `dolt-noms-size`, `events-log-size`,
`backlog-depth`, `order-tracking-retention`; `gc status` store health (size, live rows,
ratio). Pass: `backlog-depth` open count is mostly claimable work, not notification
beads; `[beads.policies.order_tracking].delete_after_close` set; events log under
~100 MB or rotated. Trap: 400+ open notification beads read as "423 open" and hide a
zero-claimable queue. There is no `--type notification` filter in `bd list`; count
them from `gc doctor`'s backlog-depth row.

**Review budget.** In the rig, the newest CodeRabbit summary comment on any open owned
PR prints the remaining reviews per hour. Pass: fixes are batched per PR (contract says
so). Trap: `gh pr ready` and every fix push each spend one.

## Config hygiene

**Resolved versus written.** `gc config show > /tmp/resolved.toml`, `gc config explain`
for provenance, and the loader's warnings on stderr. Pass: no "unknown field" warning;
every value a comment claims equals the resolved value. Trap: `gc doctor` passes a
config that `gc config show` rejects — run both. Agent-level `option_defaults.model`
loads unvalidated and only fails at spawn.

**Sediment.** `ls *.bak* *.pre-* *.prev-* .gc/settings.json.* 2>/dev/null`;
`ls orders/disabled/`; for each `[[patches.agent]]` name, `gc agent list` contains the
role (there is no `gc agent show`). Pass: no sibling backups (dated copies live in `archive/`), every patch targets a
provided role, every provider block has a consumer or a comment saying why it stays.

**Packs.** `gc import list` / `packs.lock` fetched dates; `gc pack list`. Pass: the
pinned commit is the one on disk under `.gc/cache`, and floating ranges (`^0.4`) are
either intended or replaced with a sha. Trap: the cache holds several checkouts; test
the pinned one, not any copy.

## Liveness

**Reliability.** `gc analyze reliability`. Pass: dropped/skipped lifecycle event counts
are small relative to sessions; note the instrumentation gap it prints.

**Nudges and waits.** `gc nudge status <session>` for the mayor and each pool head;
`gc wait list`. Pass: no dead-letter nudges, no wait older than the session it belongs
to. Trap: a nudge can land in a codex composer unsent; the queue shows delivered while
the session never started.

## Safety

`jq .skipDangerousModePermissionPrompt .gc/settings.json`; `grep -rn 'reset --hard\|
push --force' dispatch/ orders/ agents/`; `gc formula list` and the default formula
per role (`gc config show`, the agent's `formula`/`default_formula` key) — a role whose default formula has no worktree
isolation puts a bare sling in the shared checkout. Pass: destructive git is only in
scripts that operate on throwaway worktrees; secrets appear only as `*_env` names.
