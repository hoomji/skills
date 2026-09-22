---
name: gc-store-reclaim
description: Diagnose a slow or erroring Gas City bead store and reclaim it by clearing husk molecules. Use when gc bd writes fail with "invalid connection" or i/o timeout, when gc bd list or gc status is slow (>1s) or reports Live rows 0, when the .beads/dolt directory has grown, or when open-bead counts look inflated by workflow step beads (gc.root_bead_id).
---

# Reclaiming a Gas City bead store

A `gc` store degrades from **churn**, not from size. Every `gc bd` call is a fresh short-lived
connection, hooks fire `bd list --status=open` on every prompt in every lane, and that one
query is the **hot list** — the cost multiplied by lane count and prompt count.

The hot list is inflated by **husks**: `mol-scoped-work` molecule roots whose source work is
finished, each holding ~28 step beads open forever — measured 2026-09-11. Husks also cross-wire live lanes, which
claim a husk's orphaned controller instead of their own work.

Measure before touching anything. The three failure shapes look identical from a failed write.

## 1. Separate the three shapes

| Shape | Signal Command | Indication | Next Step |
|---|---|---|---|
| **Server bounce** | `ps -eo etime,args \| grep '[d]olt sql-server'` | Uptime shorter than the errors | Intact store; retry once succeeds. If recurring, investigate host crashes or OOM kills via [`gc-host-health`](../gc-host-health/SKILL.md). |
| **Churn** | `ss -tn state time-wait '( dport = :14091 or sport = :14091 )' \| wc -l` | TIME_WAIT high (dozens/hundreds), established ~0 | Steps 2–6: clear husk molecules inflating the hot list. |
| **Size** | `du -sh /home/coolhenrylinux/city/.beads/dolt` | Disk footprint elevated (>2 GB) | Step 7, and [`gc-dolt-disk-reclaim`](../gc-dolt-disk-reclaim/SKILL.md) if disk remains high after husks close. |

Run exact host and store probes:

```bash
# Check Dolt server process uptime:
ps -eo etime,args | grep '[d]olt sql-server'

# Check socket churn on Dolt server port (default 14091):
port=$(gc dolt status 2>/dev/null | grep -oE '[0-9]+$' || awk '/^[[:space:]]*port:/{print $2; exit}' /home/coolhenrylinux/city/.gc/runtime/packs/dolt/dolt-config.yaml 2>/dev/null || echo 14091)
ss -tn state time-wait "( dport = :${port:-14091} or sport = :${port:-14091} )" | wc -l

# Check database storage footprint on disk:
du -sh /home/coolhenrylinux/city/.beads/dolt

# Inspect recent Dolt server log for churn signatures:
tail -n 100 /home/coolhenrylinux/city/.gc/runtime/packs/dolt/dolt.log
```

A short uptime explains "invalid connection" on its own: the write failed because the server
restarted. Retry once and it succeeds — that is a bounce, and the store is intact. One trap:
on a stopped city the first `gc status` or `gc bd` boots the managed dolt itself, so an
uptime of about a minute after your own probe is you, not a bounce — read `etime` before
running anything else.

Read the server log tail for the churn signature: climbing connection IDs, `i/o timeout`,
`broken pipe`. Rising IDs over minutes measure the arrival rate.

> [!NOTE]
> The `ps` and `ss` commands above are host-level diagnostics. If Dolt is bouncing repeatedly or socket churn is high, host resource starvation (runaway child processes, CPU pressure, or stale swap latency) may be starving the server — cross-reference [`gc-host-health`](../gc-host-health/SKILL.md) for fuller host diagnosis.

Complete when each of the three shapes has a measured value recorded, the log tail is checked for connection arrival rate, and the primary bottleneck (bounce, churn, or size) is identified.

## 2. Measure the hot list

```
/usr/bin/time -f "%e s" gc bd --rig <rig> list --status open --json > /tmp/bdl.json
jq length /tmp/bdl.json ; wc -c /tmp/bdl.json
```

Record count, bytes, seconds. This is the number the repair moves, and re-measuring it at the
end is how you prove the repair worked.

## 3. Attribute the open beads

Step beads carry `gc.root_bead_id`; real work does not.

```
jq '[.[]|select((.metadata//{})["gc.root_bead_id"]!=null)]|length' /tmp/bdl.json
jq -r '[.[]|select((.metadata//{})["gc.root_bead_id"]!=null)]
       | group_by(.metadata["gc.root_bead_id"]) | sort_by(-length)
       | .[] | "\(length) \(.[0].metadata["gc.root_bead_id"])"' /tmp/bdl.json
```

Steps at half or more of the open count means husks are the problem.

## 4. Classify every root as live or husk

For each root, read `gc.graphv2_root_key` — its second `:`-delimited field is the **input
convoy**, whose title reads `input convoy for <bead>`. That bead is the ground truth:

```
gc bd --rig <rig> show <roots...> --json | jq -r '.[] |
  "\(.id) \(.status) sess=\((.metadata//{})["gc.session_name"]//"-")
   src=\(((.metadata//{})["gc.graphv2_root_key"]//"")|split(":")[1])"'
```

- Source bead **closed** → husk.
- Source bead open, lane alive → live, keep.
- Two roots naming one source → **duplicate dispatch**: keep the `in_progress` root on the
  awake lane, husk the other. Two lanes on one job burns provider quota twice. Root-key
  grouping sees only duplicates that attached a root, so run
  [`gc-duplicate-dispatch`](../gc-duplicate-dispatch/SKILL.md) to catch the rest.

A root whose lane is quota-parked is still live — check the lane's tail for a usage-limit
message before calling it dead.

Complete when every root is classified and each husk names the closed bead that proves it.

## 5. Respect deliberate husks

A root carrying a mayor comment is often preserved on purpose, with a stated release
condition ("confirm against `git ls-remote` before anyone deletes it"). Read the comments on
every root before deleting. Where a condition is stated, test it and record the result:

Test **commit containment**, not whether the branch name exists on origin. A branch name
absent from origin is harmless when its commits are already reachable from some other remote
ref — measured 2026-09-11, the name test reported 85 unshipped branches where only 5 were
real, an inflation of ~6x that makes the output unreadable:

```
git worktree list --porcelain | awk '/^branch /{gsub("refs/heads/","",$2);print $2}' | sort -u |
while read b; do h=$(git rev-parse "$b" 2>/dev/null) || continue
  git branch -r --contains "$h" 2>/dev/null | grep -q . && continue
  n=$(git rev-list --count "origin/develop..$b" 2>/dev/null)
  [ "${n:-0}" -gt 0 ] && echo "UNSHIPPED $b ahead=$n head=${h:0:8}"; done
```

Any output means the pointer is still live — keep the husk and say so. Before reporting a
survivor, subtract the throwaways: `orders/scripts/tmp-worktree-reaper.sh` already classifies
a detached `merge <n>` probe and a `probe-*`/`gate4-*` branch whose non-merge commits are all
on a remote as safe to drop. Reuse that classification rather than writing a second one.

## 6. Close the husks

`gc convoy delete <root>` previews; `--force` acts. Closing (the default) sets
`gc.outcome=skipped`, which lifts the beads out of the hot list and leaves the audit trail.
Reserve `--delete` for a store you intend to shrink, accepting the lost history.

Delete the **root**. Closing steps individually regenerates them.

## 7. Reclaim disk, then re-measure

Dated `.dolt.bak-*` directories beside a live `.dolt` are unreferenced copies. Confirm the
live store answers a query, confirm nothing references the backup, then remove it.

Disk still high after the husks are closed means orphaned `oldgen` chunks, which is a
`gc dolt compact --gc-only` job — [`gc-dolt-disk-reclaim`](../gc-dolt-disk-reclaim/SKILL.md).
Growth under `.gc/runtime` rather than `.beads/dolt` is not the store at all; it is the
reconciler trace or the jsonl-archive repo, handled in
[`gc-city-cleanup`](../gc-city-cleanup/SKILL.md) step 2.

Re-run step 2 and report both numbers. Also check `gc status` — `Live rows: 0` with a
`0.0 MB/row` ratio means the health probe is timing out, so its GC advisory can never fire.
Report that as a blind guard rather than a healthy store.

Complete when the hot list has been re-measured, every root is classified, and each preserved
husk carries its reason.
