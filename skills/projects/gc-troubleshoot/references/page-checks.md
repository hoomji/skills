# Page checks: upstream doc → probe here

One section per page the troubleshooting index links. Each row: what the page checks, the
**translation** (the probe that answers it in this city), and the pass condition. Dated
notes are the last observed values; compare against them, and re-date them when they move.

City facts every row leans on:
- Every store's Dolt is bd-owned (`dolt_mode: proxied-server` in `<store>/.beads/metadata.json`):
  a `bd db-proxy-child` plus its `dolt sql-server` per store. `gc dolt compact/restart/health`
  print "owned by bd" and do nothing; `mol-dog-compactor`, `mol-dog-doctor` and
  `dolt-remotes-patrol` are in `city.toml` `[orders] skip`, correctly so.
- Stores: the city (`~/city/.beads/dolt`, databases gl/hq/ud/udi) plus one per rig, listed by
  `~/city/.beads/routes.jsonl` (paths relative to `~/city`). `gc rig list` comes back empty
  under an exec order's HOME, so routes.jsonl is the list.
- Store restart = SIGTERM that store's `dolt sql-server`; the next `gc bd --rig <rig>` respawns
  it. Never `bd dolt start`, `bd flatten` or `bd compact` on a proxied store.

## Per-store sweep (doctor blind spot)

`gc doctor`'s `dolt-noms-size`, `dolt-log-size`, `dolt-compact-state`, `dolt-version` and
`dolt-config` all print `skipped (file backend, external dolt endpoint, or GC_DOLT=skip)`
here, so size every store by hand:

```bash
cd ~/city
{ echo .; jq -r .path .beads/routes.jsonl; } | xargs -I{} readlink -f {} | sort -u | while read -r r; do
  d=$r/.beads/dolt; [ -d "$d" ] || continue
  echo "== $d  log_level=$(awk '/^log_level:/{print $2}' "$d/config.yaml")"
  du -sh --apparent-size "$d"/proxy.log "$d"/server.log "$d"/*/.dolt 2>/dev/null
done
```

Pass: every `proxy.log`/`server.log` under ~55 MB, `log_level: warning`, and each `.dolt`
size explained by its data. `packs/ops/assets/scripts/dolt-store-logs.sh` (run by the
`disk-hygiene` order every 3 h) caps the logs and sets the level; a log far past the cap
means the order is not running. Check `.gc/runtime/disk-hygiene.log`.

2026-11-15: six rig stores held 13 GB of logs at `log_level: info` over 2–72 MB of data
(gascity-packs: 4.7 GB since 11-02). The 11-13 cap covered only the city's store. Fixed in
city `8c7c373c4`; 12.2 GB reclaimed.

## Diagnose a Failed gc start (`docs/troubleshooting/gc-start-walkthrough.mdx`)

| Doc check | Probe here | Pass |
|---|---|---|
| bd op_init timeout | `gc bd version` | ≥ 1.3.0 (1.3.4 on 11-15) |
| Pack schema mismatch (binary drift) | supervisor `/proc/<pid>/exe` vs `readlink -f $(command -v gc)` | same path. gc is installed only via `dispatch/gc-promote`, so drift means a half-finished promote |
| Duplicate agent name | doctor `v2-agent-format`, `config-semantics` | ✓ |
| Unknown field (`agent.pool`) | doctor `config-semantics` | ✓ |
| Rig path required | doctor `v2-rig-path-site-binding` | ✓ |
| Template not found / duplicate identity | doctor `config-semantics`, `config-refs` | ✓; a `config-refs` ⚠ naming a missing `prompt_template` is a real reference error |

Docs/binary gap (11-15): the page says `city.toml` is the only source of rig paths; the
binary keeps them in `.gc/site.toml` and doctor passes. The binary wins.

## Recover from Dolt Bloat (`docs/troubleshooting/dolt-bloat-recovery.md`)

| Doc check | Probe here | Pass |
|---|---|---|
| `dolt-noms-size` warning | Per-store sweep above (doctor skips it) | `.dolt` sizes match data |
| Dolt ≥ 2.6.0 | `dolt version` | ≥ 2.6.0. Bump only with gc and bd, through gc-promote |
| GC always `--archive-level=0` | the installed bd's `internal/storage/versioncontrolops/gc.go` in `~/projects/beads` at the `gc bd version` sha | `CALL DOLT_GC('--full', '--archive-level', '0')` |
| Archive dictionary count > 256 | `find <db>/.dolt/noms -name '*.darc' \| wc -l`; `dolt admin storage` only on a stopped store | few `.darc`; 0–2 per db on 11-15 |
| Compactor `below_threshold` skip, `--gc-only` reclaim | N-A: the compactor is skipped. Reclaim is `bd gc --skip-decay --full` run from the store's directory (header of `packs/ops/assets/scripts/dolt-maintenance-window.sh`); flattening is order `dolt-history-squash` | both orders absent from `gc events --type order.failed` |
| `read_timeout_millis` ceiling | `grep read_timeout_millis <store>/.beads/dolt/config.yaml` | commented out, so dolt's 28800000 applies. `city.toml` `[dolt] read_timeout_millis` does not reach bd's servers |
| `orders.max_timeout` | `grep -n max_timeout ~/city/city.toml` | unset |
| Long-lived external `dolt sql` sessions | `pgrep -af 'dolt sql'` | none besides the per-store sql-servers |

## Clean Up bd Auto-Backups (`docs/troubleshooting/bd-backup-cleanup.md`)

| Doc check | Probe here | Pass |
|---|---|---|
| `bd-backup-size` | doctor line (it does cover rigs) | < 5 GB aggregate; 0.11 GB on 11-15 |
| Missing-chunk warning on every bd call | `gc bd list --limit 1 2>&1 \| grep 'auto-backup failed'` | no output |

Off-box backup is `gl-dolt-push`, not `mol-dog-backup`'s `.dolt-backup/`: judge it by
`gc events --type order.failed`, never by order history.

## Operate Managed-City Dolt Endpoints (`docs/runbooks/managed-city-endpoints.md`)

| Doc check | Probe here | Pass |
|---|---|---|
| Drift (rig-local Dolt, port mismatch, stale info) | doctor `dolt-topology`, `dolt-drift` | ✓ |
| Storage-mode drift (`[]` with exit 0) | doctor `bd-split-store` per rig; `ls <store>/.beads/embeddeddolt` | ✓ and no `embeddeddolt` dir |
| Sling accepted, agents idle (`rigStores=0`) | `grep -E 'rigStores=0\|assignedWorkBeads=0' ~/.gc/supervisor.log \| tail` | absent |

An empty answer is not drift by itself: `henrys-work-vault` has held 0 beads since it was
added (no `hwv-` event ever).

## Maintain Dolt Storage (`docs/runbooks/dolt-compact.md`)

| Doc check | Probe here | Pass |
|---|---|---|
| `dolt-compact-state` markers | `ls ~/city/.gc/runtime/packs/dolt/compact-{quarantine,pending-gc,pending-push}` | empty (leftovers from before bd owned the store are inert, but clear them) |
| `order.skipped` for `mol-dog-compactor` | N-A: skipped in `[orders] skip` | the skip entry is present |
