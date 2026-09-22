# Fix recipes

Reversible repairs, in the order the ranked report tends to need them. Each ends with
the probe that must now pass. Back a file up once, dated, into `<city>/archive/`.

## Re-arm a wake order

    cp orders/<name>.toml archive/<name>.toml.<YYYY-MM-DD>   # only if editing it
    # strip any stale DISABLED header; keep the [order] block
    gc reload
    gc order list | grep <name>
    gc order check                 # shows it due or on cooldown
    gc order run <name>            # one manual tick proves the exec path

If it is still absent after reload, the controller predates the file: `gc restart` is
the recovery, and it restarts every session — park it unless the city is idle.

## Move a lane to another provider

    [[patches.agent]]              # in city.toml, qualified name rig/pack.role
    name = "<rig>/<pack>.<role>"
    provider = "<provider>"

    gc config show >/dev/null      # loads clean (doctor does not catch a bad enum)
    gc doctor
    gc session close <live-session-of-that-role>   # respawns on the new provider
    ps -eo args | grep <binary>    # launched flags match the intent

Model pins go in `option_defaults` on a provider block (validated), never as a
top-level `model` key (dropped with a warning) and never on the agent block
(unvalidated).

## Recalibrate context knobs

    jq '.env.GC_CONTEXT_WINDOW_TOKENS="<window>" | .env.GC_CONTEXT_ADVISORY_PCT="45"
        | .env.GC_CONTEXT_URGENT_PCT="50"' .gc/settings.json > .gc/settings.json.new
    mv .gc/settings.json.new .gc/settings.json
    gc reload --soft

Probe the window first (`claude -p`), and change the numbers in the contract's handoff
line in the same edit so the two agree.

## Set a retention policy

    [beads.policies.order_tracking]
    delete_after_close = "24h"      # Go duration; "7d" is invalid

then `gc order sweep-tracking` once, and `gc doctor` row `order-tracking-retention`
goes green on the next tick. Notification beads have no policy key on 1.4.1;
`gc order sweep-nudge-mail` closes stale delivered ones — count before and after.

## Retire sediment

    mkdir -p archive && mv <file>.bak* <file>.pre-* archive/
    mv orders/disabled/*.toml archive/     # the controller scans orders/ only

A `[[patches.agent]]` whose role no pack provides, or a provider block with no
consumer, is removed with its comment; `gc config show` then `gc doctor`.

## Refresh a stale claim

Edit the comment, contract line, or memory row the probe contradicted, in place, with
the probe date. A claim restating a live count is replaced with the probe command
that produces it. The memory index lives at
`~/.claude/projects/<slug>/memory/`; one fact per file, then its `MEMORY.md` line.

## Clear tmpfs litter

    find /tmp -maxdepth 1 -mindepth 1 -user "$(id -un)" -mtime +0 \
      ! -name 'claude-*' ! -name opencode ! -name node-compile-cache ! -name '.X*' ! -name '.bun*' \
      -exec rm -rf {} +
    free -h | grep Swap            # drops with the tmpfs, no swapoff needed

Then make it recur: the city's `orders/scripts/tmp-worktree-reaper.sh` carries a litter pass
(`LITTER_DAYS`, skips live cwds and open files) after the worktree loop; a city without one
gets that block. Probe: `df -h /tmp` under 10% and swap ≈ process VmSwap.

## Reclaim a dolt store while lanes are up

    gc dolt compact --dry-run                     # says which db is below the flatten threshold
    F=$(awk '/^full/{...avg10...}' /proc/pressure/io); [ "$F" -lt 15 ] || sleep 20
    gc dolt compact --gc-only --only-db gl        # 24s for 1.8 GB -> 901 MB with 7 lanes live

Refuses a quarantined db; that quarantine is an owner decision. If the order that should do
this (`dolt-maintenance-window`) gates on lane count, replace the gate with a size floor plus
the IO check above, as this city did on 2026-09-16.

## Gate a heavy fix on live pressure

Pruning, packing and compaction are IO-heavy, so on an IO-bound box the repair causes the fault
it is meant to cure. Read the signal, act inside the trough, and loop instead of hand-retrying:

```
F=$(awk '/^full/{for(j=1;j<=NF;j++) if($j ~ /^avg10=/){split($j,a,"="); print int(a[2])}}' /proc/pressure/io)
[ "$F" -lt 15 ] || { sleep 20; }        # re-read and retry; do not proceed hot
```

Pressure here is **bursty**, not trending: one city went `avg10` 67 → 9 in twenty seconds, so a
single failed write proves nothing and a single successful one proves just as little. Gate each
attempt rather than concluding anything from either.

Pick the acceptance metric the fault is measured in, not the one the fix is measured in: a
worktree prune is accepted by `supervisor.fs_pressure.skipped_tick` falling under a real fan-out,
never by gigabytes freed. State the confounders in the report — lane count usually drops at the
same time, and a partial hour is not a trend.

## Prove a guard by firing it

A guard that has never fired is not known to work, and its **failing** branch is the one that
matters and the one that never occurs on demand. Force it with a pass-through shim rather than
waiting:

```
#!/bin/bash
# stub only the call whose answer drives the branch; pass everything else through
if [ "$1" = "wait" ] && [ "$2" = "list" ]; then printf 'WAIT SESSION STATE KIND NOTE\n'; exit 0; fi
exec /real/path/to/gc "$@"
```

Then exercise every branch — the quiet path, the firing path, and the rate limiter — pointing the
guard's own env (`GC=...`, `STAMP=...`) at the shim and a scratch state file. A dry run cannot
prove a rate limiter: dry runs skip the state write, so the second call fires again and looks
broken. Stub the side effect instead and run it for real.

Preserve before you remove, always to `archive/` and never to `/dev/null`: a diff, an untracked-file
copy, or a pushed salvage ref. Preservation is additive and needs none of the gates that removal
needs — which is what lets you preserve a dirty or live tree you must not touch otherwise. For
worktrees specifically the whole procedure lives in the `prune-worktrees` skill; use it rather than
improvising a sweep here.

## Parked (never run in fix mode)

List these under OWNER-DECISION with the exact command:

- `gc session prune`, `gc session close` on a session doing work, `gc restart`
- deleting beads or convoys, truncating `events.jsonl`, dolt flatten (`compact` without `--gc-only`) and clearing a quarantine marker; `--gc-only` is a reversible reclaim and runs in fix mode
- any change to `merge_queue`, repair routes, or lane caps the owner set
- `reset --hard`, force-push, worktree removal on a shared checkout
