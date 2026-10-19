# orders

The city's cron, cooldown, condition and event orders (`orders/*.toml`, one order per file,
name = basename) and the scripts they run from `orders/scripts/` and `dispatch/`: the seat wake
checks (`seat-check.sh`, `seat-throttle.sh`, `elapsed-check.sh`, `seat-wake-watchdog.sh` via
`fleet-maintenance.sh`), the reapers (worktree, rig-worktree, tmp, disk, store, dolt tmp-pack),
the quality loops (`completion_sweep.py`, `lens_audit.py`, `baseline-sweep.sh`), the run logs
and stamps those scripts keep under `.gc/runtime/`, and the docs that describe an order
(`docs/completion-sweep.md`, `docs/delegated-seats.md`, `docs/worktree-lifecycle-and-storage.md`,
`docs/verify-skill-maintenance.md`). Order semantics are gc's: `~/.cache/gascity-docs/docs/tutorials/07-orders.md`
and `reference/config.md` (`OrdersConfig`, `OrderOverride`, `[workspace] timezone`).

## Sub-features

- `ord-parse` every `orders/*.toml` parses, has an `[order]` table, only known keys, a valid trigger with its field (`interval`/`schedule`/`check`/`on`), exactly one of `formula`/`exec`, no `pool` on exec, no `env` on formula.
- `ord-targets` every exec and check command resolves: a script run directly exists and is executable, a script passed to `python3`/`bash`/`sh` exists, a bare command (`gc`) is on PATH; a named formula exists in `formulas/` or the order's formula layer.
- `ord-loaded` every enabled, unskipped order file appears in `gc order list --json` with `source` pointing at that file (a city file shadows the pack order of the same name).
- `ord-condition` every condition order sets `check_timeout` explicitly (gc's default is 10s).
- `ord-refs` every city path an order file's comments or its script's header names (REVERSIBLE lines, briefs, docs, sibling scripts) exists; `docs/tutorials|reference/...` resolve in the gc docs corpus; every `gc order <sub>` they cite is a real subcommand.
- `ord-cron-tz` a cron order's comment that states a UTC time agrees with the zone its schedule is evaluated in (order `tz`, else `[workspace] timezone`, else the host's zone).
- `ord-cadence` a clock order expected to fire twice a day or more has at least one run in `gc order history --since 24h`; inventory shows observed runs against the declared cadence.
- `ord-runlog` each order's run log or stamp under `.gc/runtime/` (and `order-elapsed/<name>` for elapsed-check orders) is present and recent for its cadence.
- `ord-seats` each delegated seat's wake state (`.gc/runtime/fleet/seats/<seat>/`) is idle or claimed, not an unclaimed fire older than the stale alarm.
- `ord-docs` a doc describing an order states the cadence and outputs the order file and script carry (e.g. `docs/completion-sweep.md` "every two hours" = `interval = "2h"`).

## How to get to it (user POV)

- The orchestrator rescans `orders/` about once a minute; `gc order list` shows what it loaded
  (pack orders too), `gc order show <name>` one definition, `gc order history <name>` the
  tracking beads (`order-run:<name>` label; `exec-failed` marks a failed exec).
- City config: `city.toml` `[orders]` (`max_dispatches_per_tick`, `skip`, `[[orders.overrides]]`).
- Disarm convention: `mv orders/<name>.toml orders/disabled/`. `orders/remote/*.toml` are
  deployed to other hosts (GTX) and are not scanned on Ryzen.

## Driving it with orders_check.py

Preconditions:

- Doctor ran this pass. `H=~/projects/skills-verify-agent-context/skills/projects/verify-city/scripts/orders_check.py`
  (`--city` defaults to `$GC_CITY` or `~/city`). It reads files and calls only
  `gc order list --json|show|history --json|--help` and `gc bd show --json`.

- **Doctor.** `$H doctor > $EV/orders/doctor.txt`. Covers `ord-parse`, `ord-targets`,
  `ord-loaded`, `ord-condition`, `ord-refs`, `ord-cron-tz`, `ord-cadence`. Output is
  `orders: clean`, exit 0; else one `<order>: <finding>` line each (file:line where it has one), exit 1.
  The 24h history read takes ~30s; `--no-history` skips `ord-cadence`.
- **Inventory.** `$H inventory > $EV/orders/inventory.txt` (`--json` for rows). One line per
  loaded order (city or pack): trigger, interval/schedule/check with its timeout, cron zone,
  exec or formula -> pool, `runs24h=<n>/~<expected>`, last run in 24h, then each `.gc/runtime`
  file the script names or that carries the order's name, with its mtime. Proves `ord-runlog`
  and shows `ord-cadence` as numbers.
- **One order.** `$H order <name> > $EV/orders/order-<name>.txt`. File text, `gc order show`,
  each script's header, the last 5 runs with status, duration, labels and close reason from
  the tracking bead, and the tail of each runtime file. Use it on the order a finding names.
- **Seats.** `$H seats > $EV/orders/seats.txt`. Per seat: `idle` (no pending signature),
  `claimed` (pending = last), or `UNCLAIMED` with the claim age, last probe, `pending.txt`
  header and `alarm-sent`. `ord-seats` holds when no seat is UNCLAIMED past an hour
  (seat-check.sh mails `SEAT STALE` at 3600s; seat-wake-watchdog.sh acts at 900s).
- **Docs.** For `ord-docs`, read the order file beside its doc: `docs/completion-sweep.md`
  (cadence, gap classes vs `completion_sweep.py` docstring), `docs/delegated-seats.md`
  (seat-check/seat-throttle/seat-wake-watchdog), `docs/worktree-lifecycle-and-storage.md`
  (reapers), `docs/verify-skill-maintenance.md`. Each stated cadence and output matches.

Never run `gc order check` (it runs every condition check and opens pending windows),
`gc order run`, or any order script, including `DRY_RUN=1` forms: several still fetch, mail
or stamp state (`elapsed-check.sh` and `seat-throttle.sh` stamp on every call;
`completion_sweep.py` and `lens_audit.py due` read the network and store).

## Gotchas

- `gc order history` keeps ~24h (store-retention purges closed wisps), so a weekly or daily
  cron order with no history is normal; `verify-skill-maintenance.sh` keeps its own
  `.gc/runtime/verify-skill-maintenance.log` for this reason. Doctor only flags orders
  expected to fire at least twice a day.
- Cron schedules are evaluated in the host zone (America/Toronto) unless the order sets
  `tz` (only `dolt-server-recycle` does) or `city.toml` sets `[workspace] timezone`. A comment
  saying `13:00Z` on a schedule `0 13 ...` is wrong by four or five hours.
- Clock orders (cooldown, cron, event) share `max_dispatches_per_tick`; observed cadence runs
  well below declared (10m orders ~35/24h, 1h reapers ~10/24h on 10-19). Fleet-critical
  clocks are condition orders on `elapsed-check.sh` for this reason. Low `runs24h` against
  `expected` is this budget, not a dead order; zero is a finding.
- Several scripts gate real work on their own stamp (`MIN_INTERVAL` in disk-hygiene,
  checkout-freshness, dolt-tmp-pack-sweep, jsonl-archive-mirror); a fresh `.log` with an old
  `.last` means the order ran and skipped, which is a success there.
- A ledger a script appends to (`dispatch/ledgers/wall-deploy.tsv`) does not exist until its
  first record; doctor ignores ledger paths named in script headers.
- `/home/coolhenry` is a symlink to `/home/coolhenrylinux`; order paths through it resolve.
- Another session may add an order mid-pass; inventory reads live state, so re-run before
  comparing counts.
