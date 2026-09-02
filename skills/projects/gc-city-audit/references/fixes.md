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

## Parked (never run in fix mode)

List these under OWNER-DECISION with the exact command:

- `gc session prune`, `gc session close` on a session doing work, `gc restart`
- deleting beads or convoys, truncating `events.jsonl`, dolt maintenance
- any change to `merge_queue`, repair routes, or lane caps the owner set
- `reset --hard`, force-push, worktree removal on a shared checkout
