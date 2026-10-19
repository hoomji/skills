# quota-routing

Quota readings, backend fallback and Pareto lane placement. `dispatch/codex-fallback.py` (the
Ryzen `codex-fallback.timer`, every 10 min) reads every subscription, picks each host's backend
(`.gc/runtime/fleet/pool-backend`), writes `quota-windows.json`, probes muse-code into
`muse-code-usage.json`, appends `quota-history.jsonl` through `dispatch/quota-runway.py`, re-pins
role providers and moves the mayor's Claude login in `[providers.claude-mayor]`. `dispatch/fleet.py`
then places each lane from those readings (`t1_pool`, `placement_pool`, `gateway_review_provider`).
`orders/scripts/fleet-supply-probe.py providers` turns walls and stale readings into fleet-watcher
lines. Policy lives in `docs/quota-fallback.md`, `docs/model-routing-contract.md` and
`docs/mayor-provider.md`.

## Sub-features

- `qr-readings` each reading (`quota-windows.json`, `muse-code-usage.json`, the last
  `quota-history.jsonl` line, `hopscotch-credit.json` prod, the agy cache) is present and younger
  than the max age the code that consumes it uses.
- `qr-constants` thresholds mirrored across `fleet.py`, `codex-fallback.py`, `quota-runway.py` and
  `fleet-supply-probe.py` agree (swap headroom, burst, agy spent, muse and controller staleness,
  dsh floor, credit age, Codex login map, muse probe cadence vs runway's muse max age).
- `qr-providers` every pool the code maps to (`POOL_BACKENDS`, `EXPERIMENTAL_POOLS`, seat, implementer,
  review, light and `-ub` twin tables) has a `[providers.<name>]` block in `city.toml`.
- `qr-mayor` `agents/mayor/agent.toml` names `claude-mayor`; its default model resolves to
  `--model claude-opus-5-5`, effort `low`; its `CLAUDE_CONFIG_DIR` is the login `mayor_login` picks
  from the latest readings (`MAYOR_LOGINS` order, under `MAYOR_THRESHOLD`).
- `qr-backend` this host's `pool-backend` is known to `POOL_BACKENDS` and consistent with its readings
  (no Sol backend over the Codex threshold; `dsh` only above the dsh floor).
- `qr-t1` the write order `t1_pool` actually walks, per quota switch, equals the contract table.
- `qr-review` the gateway-review order `gateway_review_provider` walks equals the contract table.
- `qr-docs` numbers and tables in the two policy docs match the code (thresholds, backend table
  writes/reads/seats, `T1_HARD_EFFORTS`, Sonnet backends, `MUSE_HOSTS`, rules `t1_pool` applies).
- `qr-placement` from the current readings, the pool a fresh write, hard write, retry, read,
  browser walk and gateway review get, and why.
- `qr-supply` the supply probe's `providers` arm reports the walls the readings show.

## How to get to it (user POV)

- The mayor or a seat asks "where will the next lane land and why": quota is read from the files
  above, never from a provider call. `systemctl --user list-timers | grep codex` shows the controller.
- `python3 dispatch/quota-runway.py` (no argument) prints the runway table read-only;
  `quota-runway.py record` appends to history, so never run it in a drive.
- The fleet-watcher seat sees `fleet-supply-probe.py` lines in its `pending.txt`.
- Owner-facing routing policy: `docs/model-routing-contract.md` "Distinct routing paths" (revision
  line names the version) and the backend table in `docs/quota-fallback.md`.

## Driving it with quota_routing.py

Preconditions: baseline from the README; `H=<skill>/scripts/quota_routing.py`;
`mkdir -p $EV/quota-routing`. Every subcommand is read-only; `--city` defaults to `$GC_CITY` or `~/city`.

- **Doctor.** `$H doctor > $EV/quota-routing/doctor.txt; echo $?`. Exit 0 prints
  `quota-routing: clean`; exit 1 prints one finding per line, prefixed `reading missing|stale|failing`,
  `constant drift`, `provider missing`, `mayor drift`, `backend drift`, `doc drift`, `code drift`,
  `order drift`, `harness stale` or `controller`. Covers `qr-readings` through `qr-docs`.
- **Readings.** `$H readings > $EV/quota-routing/readings.txt`. Each file line reads
  `age <a> max <m> (<constant>) fresh|STALE|MISSING <detail>`, then every pool in the latest history
  line with its used % and time to reset, then `pool-backend`. Proves `qr-readings`.
- **Placement.** `$H placement > $EV/quota-routing/placement.txt`. Prints backend, `codex_swap_percent`,
  `claude_spent`, `sonnet_first`, `muse_before_sonnet`, `gemini_first`, `muse_available` (binary,
  auth, `muse_quota` detail), `agy_available`, then one line per job: `pool`, `effort` (`t1_effort`)
  and whether `t1_pool` or `pool_for` decided. It calls the imported fleet functions on live files,
  so it is exactly what `launch_node` would choose now. Proves `qr-placement`; cross-check with the
  readings (for example, backend `dsh` with Claude's 7d at 100% must not place on `claude-review`).
- **Orders.** `$H orders > $EV/quota-routing/orders.txt`. Enumerates the T1 order for fresh/hard x
  `sonnet_first` x `muse_before_sonnet` and the review order for `gemini_first` by patching those
  predicates on the in-memory module and removing each winner; prints `code` beside `contract`.
  Proves `qr-t1` and `qr-review`.
- **Supply.** `$H supply > $EV/quota-routing/supply.txt`. Runs `fleet-supply-probe.py providers`
  only. Each `quota wall <pool> N%` line must match a pool at 95%+ in `readings`. Proves `qr-supply`.
- Record `exits.txt` with each subcommand's exit code.

## Gotchas

- Never execute or import `dispatch/codex-fallback.py`: it has no `--help`, and any argument,
  `--dry-run` included, is treated as a live pass (it can ssh-write other hosts, spend a muse model
  turn on the probe, edit `city.toml` and mail). The harness reads its constants from the AST.
- `fleet-supply-probe.py` with no argument or `aa` calls wrangler and writes
  `.gc/runtime/fleet/seats/fleet-watcher/aa-pointer.json`; only `providers` is read-only.
- `mayor-provider.py status` takes `.gc/mayor-provider.lock` and runs `gc session list`; read
  `agents/mayor/agent.toml` instead. Any other argument rewrites the mayor's provider.
- Importing `fleet.py` is side-effect free (module level reads `integration-branch` and resource
  policy only); the harness sets `dont_write_bytecode` so no `__pycache__` lands in the city.
- `quota-windows.json` carries one Claude login per host (the lane login), and Codex as the binding
  (fuller) window. Mayor login checks use the per-login pools in `quota-history.jsonl`.
- A reading past its `resets_at` is ignored by `_window`, so a 100% that has reset reads as no
  reading (Sol first), not as spent.
- `muse_available()` also needs `~/.local/bin/muse` and `~/.config/muse/auth.json` on the host
  running the harness; run it on Ryzen, or the placement lines describe the wrong host.
- `DOC_T1`/`DOC_REVIEW` in the harness transcribe contract revision `routing-contract-v1.7`; when the
  revision line changes doctor prints `harness stale` until they are re-read.
- Known drift on 2026-10-19 (reported, not fixed): contract v1.7 omits `muse_before_sonnet`
  (in `docs/pareto-routing-research.md` only) and the `claude_spent` fallback in `placement_pool`;
  `codex-fallback.implementer_provider` skips `muse_before_sonnet`; quota-fallback.md's `codex` row
  says seats `codex-ci` and calls Hailey "not in `MUSE_HOSTS`"; `quota-runway.MUSE_MAX_AGE_S` (30 m)
  is under the hourly muse probe, so ~17% of history lines lack `muse:*` pools.
