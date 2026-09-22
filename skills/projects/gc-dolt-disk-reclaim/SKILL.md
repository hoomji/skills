---
name: gc-dolt-disk-reclaim
description: Reclaim disk from a Gas City Dolt database whose orphaned oldgen chunks scheduled compaction skips, by running gc dolt compact --gc-only against the live server. Use when .beads/dolt has grown, when the compactor log says below_threshold ... skip, when DOLT_GC fails with "SaveHashes ... context canceled", or when a compact cannot resolve the runtime port.
---

# Reclaiming Dolt disk with `--gc-only`

`gc dolt compact` flattens history only above a commit threshold (default 2000). A database
that fell **below** the threshold while still holding orphaned `oldgen` archives is
**stranded**: scheduled compaction skips it forever and the disk is never freed. The operator
path out is `--gc-only`, which runs `CALL DOLT_GC('--full')` with no flatten.

This skill frees **disk**. Husk molecules inflating the hot list are a different reclaim —
[`gc-store-reclaim`](../gc-store-reclaim/SKILL.md).

Two traps decide whether the run succeeds, and both look like a broken store:

| Trap | What you see | Why |
|---|---|---|
| Server down | `cannot resolve runtime port`, `dolt-state.json (missing)` | `--gc-only` talks to the **live** managed server; `gc stop` takes it down with the city. Setting `GC_DOLT_PORT` does not rescue it — the resolver still reports it unset. Stopping the city also does not guarantee host quiescence: measured 2026-09-13, formula-spawned child processes (e.g., `workerd`) can survive `city stop` (ignoring SIGTERM and requiring SIGKILL) and consume 100% CPU, starving Dolt operations. See [`gc-host-health`](../gc-host-health/SKILL.md) step 2 to identify and kill runaway children. |
| Connection reaped | `DOLT_GC('--full'): ... SaveHashes ... context canceled`, `rc=1` after 15-25s | The managed listener's `read_timeout_millis: 15000` reaps the GC connection mid-run. Quiescing the city does not help; measured 2026-09-11, it failed identically with one live session. |

So the city stays **up** for this work, and the listener timeout is raised for the duration.

## 1. Confirm the server answers

```bash
gc dolt status          # expect: Dolt server: running (managed, 127.0.0.1:<port>)
gc dolt health          # expect: Server: running (PID <pid>, port <port>, latency <n>ms)
```

Expected output shapes:

```
Dolt server: running (managed, 127.0.0.1:14091)
```

```
Server: running (PID 3111850, port 14091, latency 111ms)

Databases:
  gl: 10204 commits, 209 open beads
  hq: 10451 commits, 24 open beads

Backups: none found

Last progress: 0s ago
```

**Two lines in that output lie, and both matter here.**

`Backups: none found` means the backup path it checks is empty, not that you have no backup.
Real backups live in `<city>/.dolt-backup/`; list it and read the directory dates. Measured
2026-09-16: 4.4 GB of backups sat there while health reported none, which hid a `mol-dog-backup`
order that had reported EXECUTED every 6h for three days without writing one.

`Zombie processes: N (PIDs: ...)` can name a **live** server. Check before believing it:

```bash
ps -o pid,ppid,stat,etime,cmd -p <pid>     # STAT Sl + a dolt sql-server cmd = alive, not defunct
ss -lntp | grep <pid>                      # a LISTEN row means it is serving a port
```

Measured 2026-09-16: the "zombie" was a dolt sql-server up 13h holding a second 1.6 GB store on
its own port, reparented to systemd after its launcher died. It was safe to stop only after
`ss -tn | grep <port>` showed **zero** established connections and the rig's
`.beads/dolt-server.port` named a different port.

If the server is down (`gc dolt status` reports not running or `cannot resolve runtime port`), start the city and verify:

```bash
gc start
gc dolt status          # confirm running
gc dolt health          # confirm data-plane answers with commit counts
```

This build has no `gc city` subcommand — the verbs are top level (`gc start`, `gc stop`, `gc status`); confirm against `gc --help` before trusting a pasted command.

Complete when `gc dolt status` reports `running (managed, ...)` and `gc dolt health` returns low latency with database commit counts.

## 2. Clear the database for reclaim

`--gc-only` refuses any database under an integrity-quarantine marker, so read the marker
directories rather than inferring from a past failure:

```bash
ls <city>/.gc/runtime/packs/dolt/compact-quarantine/ <city>/.gc/runtime/packs/dolt/compact-pending-gc/
```

Empty means nothing blocks the run. A marker present is its own investigation — resolve the
stated reason first, and **read which marker it is**, because they are not equally serious:

- `compact-pending-push` does **not** block `--gc-only`. It guards a diverged remote, so the
  flatten-and-push path is correctly refused while a local GC is still fine. Leave it in place.
- `compact-quarantine` **does** block `--gc-only`, and clearing it is the owner's call: it fires
  on a post-flatten integrity check, which is the one thing a GC should not paper over.

Clearing one is reversible only if you **move** the marker rather than delete it:

```bash
mv <city>/.gc/runtime/packs/dolt/compact-quarantine/<db> <city>/archive/compact-quarantine-<db>.<date>.marker
cp -a <city>/.beads/dolt/<db> <city>/.dolt-backup/pre-gc-<date>/<db>    # insurance; GC is not reversible
```

After the reclaim, prove **integrity**, not just size: the server answers, the commit count has
advanced rather than dropped, and beads a live lane holds still read. Measured 2026-09-16 on a
quarantined hq: 3.3 GB -> 2.7 GB in 323s, commits 58851 -> 60163, all lane beads intact.

Take the before number and dry-run:

```bash
du -sh <city>/.beads/dolt/<db>/.dolt
df -h <city>                                        # GC rewrites chunks; budget 2x
gc dolt compact --gc-only --only-db <db> --dry-run
```

Expected dry-run output shape:
```
compact: db=<db> — dry-run (would reclaim via DOLT_GC --full)
```

Complete when the marker directories are read, free space covers 2x the store, and the
dry-run names the database it would reclaim.

## 3. Raise the listener read timeout

`city.toml` `[dolt] read_timeout_millis` overrides the managed default. Back the file up,
append the block with a dated comment saying it is temporary, then restart the server so it
takes.

Append this exact block to `city.toml`:

```toml
# TEMPORARY: raised read timeout for DOLT_GC disk reclaim (2026-09-13). Revert in step 5.
[dolt]
read_timeout_millis = 1800000
```

Command sequence:

```bash
cp city.toml city.toml.bak
cat << 'EOF' >> city.toml

# TEMPORARY: raised read timeout for DOLT_GC disk reclaim (2026-09-13). Revert in step 5.
[dolt]
read_timeout_millis = 1800000
EOF
gc dolt restart
grep -n 'read_timeout_millis:' <city>/.gc/runtime/packs/dolt/dolt-config.yaml
```

Expected output:
```
21:  read_timeout_millis: 1800000
```

`dolt-config.yaml` is generated on every server start — the grep reading back the raised value
is what proves the override landed.

Complete when `grep -n 'read_timeout_millis:'` on `<city>/.gc/runtime/packs/dolt/dolt-config.yaml` outputs `read_timeout_millis: 1800000`.

## 4. Run the reclaim

```bash
time gc dolt compact --gc-only --only-db <db>
```

Read the line, not the exit code: `gc-only reclaim duration=<n>s — ok` is the success shape,
and `gc-only reclaim DOLT_GC failed rc=1` carries its own error text. A failure at 15-25s is
the reap again — check that step 3's grep really showed the raised value.

Expected success output shape:
```
compact: db=<db> gc-only reclaim duration=45s — ok
```

After the reclaim finishes, verify immediately that the server is still answering queries:

```bash
gc dolt status          # expect: Dolt server: running (managed, 127.0.0.1:<port>)
gc dolt health          # expect: Server: running (PID <pid>, port <port>, latency <n>ms)
```

Reading the output line confirms the reclaim command's exit, but running `gc dolt status` and `gc dolt health` verifies that the Dolt server did not crash or hang during chunk rewriting and is actively responding.

Complete when `gc dolt compact --gc-only` prints `gc-only reclaim duration=<n>s — ok` and post-reclaim `gc dolt health` confirms the server is alive and answering with low latency.

## 5. Restore the timeout

Restore the backup and restart, so the city runs on the managed 15s default again:

```bash
cp city.toml.bak city.toml
gc dolt restart
grep -n 'read_timeout_millis:' <city>/.gc/runtime/packs/dolt/dolt-config.yaml   # back to 15000
```

Expected output:
```
21:  read_timeout_millis: 15000
```

The raised timeout lets dead per-call connections pile up in `Sleep` — this restore is part of
the reclaim, not cleanup for later.

Complete when `city.toml` is restored from `city.toml.bak`, `gc dolt restart` completes, and `grep -n 'read_timeout_millis:'` on `<city>/.gc/runtime/packs/dolt/dolt-config.yaml` confirms `read_timeout_millis: 15000`.

## 6. Prove the store answers

A size drop measures the GC, not the store's health. Pair it with a query:

```bash
du -sh <city>/.beads/dolt/<db>/.dolt      # after
gc bd list --status open                  # answers, with a plausible count
gc dolt health                            # commits and open beads per database
```

Report both numbers, and record the pair with
[`gc-reclaim-register`](../gc-reclaim-register/SKILL.md) when this is part of a wider cleanup.

Complete when the timeout is back at the managed default (15000), the reclaim line read `ok`, the after size is measured, and the store has answered a query (`gc bd list` or `gc dolt health`) since.
