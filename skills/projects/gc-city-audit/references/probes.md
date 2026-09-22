# Probes

One entry per check: the command, the pass condition, and the trap that makes the probe
lie. Run from the city root. Every command here is read-only.

## Autonomy

**Wake ticks.** `gc order history <name>` for every wake the contract names. Pass: a
run within two intervals, **and the order's artifact has moved.** History records that the
exec path returned, never that it did its job, so a tick is necessary and not sufficient.
Probe the **artifact** — the thing the order should have produced — and compare its mtime to
the tick:

| Order | Artifact |
|---|---|
| `mayor-wake-on-close` | `.gc/runtime/mayor-wake.last` |
| `mol-dog-backup` | dated directories under `<city>/.dolt-backup/` |
| `reaper` | the husk/step-bead count it should be draining |

Measured 2026-09-16: the wake reported 682 fired / 682 completed / 0 failed across a day while
its stamp sat 13.5h cold and no wake was delivered, because a filter matched a convoy title the
city had stopped using. The backup order and the reaper were failing the same way in the same
hour. A stamp older than the tick interval, beside a green history, IS the finding.

Trap: read the full `gc order list --json`, never a
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

**Supervisor throttle.** `grep -c supervisor.fs_pressure.skipped_tick .gc/events.jsonl`, then
bucket by hour and read the newest payload for its own `avg60` and `threshold`. Pass: zero
under a normal fan-out. Trap: nothing surfaces this — not `gc status`, not `gc doctor`, not the
PSI triad on its own — so a city can throttle its own reconcile loop for hours with every other
probe green. `threshold` is a built-in default with no `city.toml` key; raising it would make the
supervisor thrash instead of back off, so the fix is always to cut IO at the source.

Read it as the **head of a cascade**, because its consequences surface far from the cause:
skipped reconcile → `session.stranded` → `bead.dead_assignee_reopened`, which clears a bead's
routing metadata so finished work reads as never-started. Count all three from the same log
(`grep -c` each) and report them together; the last one is what sends a mayor to re-dispatch work
that is already done. A `gc status` that answers "runtime status probe timed out; using partial
status" is this same pressure showing its face — treat the timeout as the finding, not as a
reason to stop the audit.

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

**Usage facts.** `gc costs`. Pass: every lane that ran today has rows **and a non-zero
`EST_USD`**. Rows alone are not the bar — a full table of `0.0000` with `UNPRICED` equal to the
invocation count is an unmetered city, not a free one.

Decide priced-versus-unpriced from the sink, not the table: `unpriced` is a field stamped into
each fact in `.gc/usage.jsonl` at **write** time, not computed by `gc costs` at read time. So
count it directly, and pay attention to whether it is ever `false`:

```
python3 -c "import json,collections,sys; c=collections.Counter(json.loads(l).get('unpriced') for l in open('.gc/usage.jsonl')); print(c)"
```

**`unpriced` that is never once `false` across the whole file means pricing has never worked in
this city** — not that today's lanes are new. Two consequences follow. First, the flag being
write-time makes any pricing fix forward-only; historical rows stay unpriced permanently. Second,
adding a city-level `[[pricing]]` block may change nothing: on 1.4.1 `gc config show` renders it
faithfully while `gc reload` *and* `gc reload --soft` both answer "No config changes detected" and
new facts still write `unpriced: true`. `pack-spec.md` and `config.md` document the feature; the
binary on the machine is the oracle, and this disagreement is itself a finding to report.

Also count the rows carrying no `provider`/`model` at all — 20,614 of 24,629 in one city. Those
can never be priced whatever the table says, and that is an instrumentation gap, not a config one.

When the audit is heading toward an effort-versus-quota recommendation, run this probe **first**:
that decision is a spend decision, and a fabricated rate under it is worse than a blank.

**Store and logs.** `gc doctor` rows `dolt-noms-size`, `events-log-size`,
`backlog-depth`, `order-tracking-retention`; `gc status` store health (size, live rows,
ratio). Pass: `backlog-depth` open count is mostly claimable work, not notification
beads; `[beads.policies.order_tracking].delete_after_close` set; events log under
~100 MB or rotated. Trap: 400+ open notification beads read as "423 open" and hide a
zero-claimable queue. There is no `--type notification` filter in `bd list`; count
them from `gc doctor`'s backlog-depth row.

**Measure the tree, not the named files.** `du -sh .gc/* | sort -rh | head`, then descend into
whatever leads — including hidden entries (`du -sh <dir>/* <dir>/.[!.]*`), because the largest
consumer is often a `.git` that a bare `ls` never shows. Named-file checks pass while a directory
beside them holds 30× more: one city's `events.jsonl` sat at a healthy 91 MB while
`.gc/runtime/packs/core/jsonl-archive/.git` held **3.5 GB**, with every `gc doctor` size row green.

That repo is worth naming because the shape recurs: an order that commits a full export on a
cooldown (`jsonl-export`, every 15m) writes a fresh copy of a large blob forever, and nothing packs
it. `git count-objects -vH` inside it decides in one command — **2,076 loose objects at 3.37 GiB
against 6,553 packed at 41 MiB** is the signature. Pass: loose `count` in the low hundreds. The fix
is a plain `git gc`, which preserves all reachable history (that city went 3.5 GB → 112 MB with all
1,089 commits intact), making it one of the few large reclaims that is safely reversible.

Store health in `gc status` is a separate matter and can be **structurally blind**: `Live rows: 0`
with `Ratio 0.0 MB/row` against a `1.0 MB/row` threshold means the row count broke, so the guard
can never fire however large the store grows — no amount of data will trip it. Take real figures
from `gc dolt health --json` (`commits` and `open_beads` per database) and read growth in
**commits**, not rows. `gc dolt compact` is the lever, and on 1.4.1 it takes **no `--gc-only`
flag** whatever the docs say.

**Dolt load.** `show global status like 'Connections'` and `'Questions'` through
`echo "…;" | gc dolt sql`, twice 10s apart. Pass: under ~3 new connections/s at idle. A busy
`dolt sql-server` with an empty `show full processlist` is this probe's case: on 1.4.1 every
gc command opens a connection per query (`gc bd show` ≈ 40, `gc nudge drain --inject` 230-430),
and the opencode plugin `<rig>/.opencode/plugins/gascity.js` runs drain + `mail check` from two
hooks on every model step. Measured 2026-09-16: 7 lanes, 18 conn/s, dolt at 270% CPU, `gc doctor`
fork-rate 200-365/s — three faces of one finding. Trap: the plugin is regenerated from the gc
binary on each spawn, so an edit there passes the probe and reverts within minutes; the lever is
lane count and churn, and the upstream bead (`ci-tsitmx`).

**Swap versus tmpfs.** `free -h`, then `awk '/VmSwap/' /proc/*/status` for any process over
50 MB and `df -h /tmp`. Pass: swap used ≈ the sum of process VmSwap. Swap high with RAM free and
no swapped process is tmpfs: `/tmp` pages the kernel pushed out (4.4 GB of litter read as 58% swap
on 2026-09-16). `Shmem` in `/proc/meminfo` counts only the resident part, so it stays small.
Trap: the tmp reaper order only reaps entries carrying a `.git`; count the rest with
`find /tmp -maxdepth 1 -mtime +0 | wc -l`.

**Review budget.** In the rig, the newest CodeRabbit summary comment on any open owned
PR prints the remaining reviews per hour. Pass: fixes are batched per PR (contract says
so). Trap: `gh pr ready` and every fix push each spend one.

## Config hygiene

**Quiet-window gates.** For each order whose script exits on a lane count or "quiet" test
(`grep -ln 'list-sessions\|quiet' orders/scripts/*.sh`), read its history for a line that
says it did the work, not just that it ran. Pass: at least one real run in the last interval ×4.
`dolt-maintenance-window` ticked green every 6h for days and reclaimed nothing because this city
never has ≤1 lane up; the gl store grew to 1.8 GB behind it.

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

**An empty `gc wait list` is the finding, not the clean bill.** Cross it with work in flight —
beads `in_progress` carrying `gc.routed_to` — and an empty inbox. Routed work with no wait armed
and no `HANDOFF:` mail means the last turn ended on neither, so nothing will wake anyone when the
work lands. The `PreCompact` → `gc handoff --auto` backstop does not cover it, because the usual
cause is a **restart**, and a restart is not a compaction.

## Safety

`jq .skipDangerousModePermissionPrompt .gc/settings.json`; `grep -rn 'reset --hard\|
push --force' dispatch/ orders/ agents/`; `gc formula list` and the default formula
per role (`gc config show`, the agent's `formula`/`default_formula` key) — a role whose default formula has no worktree
isolation puts a bare sling in the shared checkout. Pass: destructive git is only in
scripts that operate on throwaway worktrees; secrets appear only as `*_env` names.
