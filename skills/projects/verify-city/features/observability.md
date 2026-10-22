# observability

The operator views of the city: the gc-top terminal dashboard (`gc-top.py`, city root), the
PR pipeline dashboard (`gc-pr-top.py`, city root), the bead/graph observer (`gc-visualize.py`,
city root), the gc-mobile phone PWA (`mobile/server.py` on `127.0.0.1:8390`, service
`gc-mobile`, doc `docs/gc-mobile.md`), the provider classifier both dashboards share
(`dispatch/fleet_facts.py`), the drift order that keeps them mapped (`orders/ui-drift.toml` →
`orders/scripts/ui-drift-check.py`), and the scorecards (`dispatch/city-metrics.py`, doc
`docs/city-metrics.md`; `dispatch/mergify-metrics.py`, doc `docs/merge-queue.md`). A view is
right when it shows what the source it names says, using the state words placement uses.

## Sub-features

- `obs-docs` every script and path `docs/gc-mobile.md` names exists (bare names resolve under the city root, `dispatch/`, `mobile/`, `.gc/runtime/{mobile,fleet}/` or the gc-fleet-metrics skill).
- `obs-mobile-up` the server answers `/api/health`, every collector in its `jobs` table appears in `sources`, none carries an `error`, none is older than three intervals.
- `obs-mobile-routes` every GET route `do_GET` registers (`/api/{health,vapid,alerts,now,prs,metrics,flow,costs,mergify,agy}`, the `days=` variants, `/` and each `mobile/static/` file) returns 200.
- `obs-mobile-fresh` the running server started after the last change to each module it loads once (`mobile/*.py`, `gc-top.py`, and through gc-top's `_ROUTING_MOD` cache `dispatch/fleet.py`, `fleet_facts.py`, `codex-fallback.py`).
- `obs-states` gc-top `MUSE_STATE_STYLE` and app.js's `const st` map exactly the words `fleet.muse_state` returns; no display, alert or test names a retired state, and no display describes a pace gate `fleet.muse_quota` no longer has (owner 2026-10-19).
- `obs-parity` the phone's `/api/now` `quota.muse.state` equals `fleet.muse_state` over `.gc/runtime/fleet/muse-code-usage.json` now; its host order equals `fleet.HOSTS`.
- `obs-gaps` the lane gap kinds in gc-top `classify_gaps`, `mobile/alerts.py` `GAP_KINDS` and the doc's alert table are one set.
- `obs-drift` `ui-drift-check.py --dry-run` reports no drift.
- `obs-top` gc-top renders (one-shot and live TUI) with the NODES, PROVIDERS and LANES sections and the muse-code line.
- `obs-facts` fleet_facts classifies every city.toml provider; what it cannot place is listed as unmapped.
- `obs-views` gc-visualize summary and mergify-metrics print their reports.

## How to get to it (user POV)

- Terminal: `python3 gc-top.py` (live, `-n` interval), `--once`, `--json`, `--host <h>`;
  `python3 gc-pr-top.py` (`--once`, `--json`, `--audit`, `--pr N`); `python3 gc-visualize.py
  summary|work|loop|graph|audit`. All from `~/city`.
- Phone: `https://coolhenrylinux-ms-7a40.tail92f6df.ts.net/` via `tailscale serve` to
  `127.0.0.1:8390`; tabs Now, Lanes, Metrics, Flow, Quota, Alerts. Each tab reads `/api/<name>`.
- Scorecards: `dispatch/city-metrics.py report [--days N] [--json]`,
  `dispatch/mergify-metrics.py [--since YYYY-MM-DD]`.
- Drift mail: the `ui-drift` order mails the mayor `UI DRIFT: N new` when the drift set grows.

## Driving it with observability.py

Helper: `~/projects/skills-verify-agent-context/skills/projects/verify-city/scripts/observability.py`
(stdlib, `--city` defaults to `$GC_CITY` or `~/city`, `--ev DIR` saves each drive's files).
Set `H=<that path>` and `mkdir -p $EV/observability`.

Preconditions: `systemctl --user is-active gc-mobile` prints `active` and
`ss -ltnH 'sport = :8390'` shows a `127.0.0.1` listener; else `obs-mobile-*` and `obs-parity`
are `verified-unreachable` with that output.

- **Doctor.** `$H doctor --ev $EV/observability`. One line per finding, prefixed with the
  sub-feature ID; exit 1 on any. Clean reads `observability: clean`. It runs in about 2 s:
  GETs every route, scans the display sources, computes `fleet.muse_state` in a `python3 -I`
  subprocess and runs `ui-drift-check.py --dry-run`.
- **Mobile.** `$H mobile --ev $EV/observability` writes `mobile.txt`: one `GET <path> <status>
  <bytes> <ms>` line per route with a sanitized excerpt (emails, URLs and 32+ char tokens
  redacted), then `parity muse:` (phone state and windows beside `fleet.muse_state` and the raw
  `muse-code-usage.json`), `parity hosts:`, the Now summary, and gc-pr-top / city-metrics output
  as the server last collected it. Proof: every line `200`, both parity lines `agree`.
- **Top.** `$H top --ev $EV/observability` runs `gc-top.py --once` (COLUMNS=180) into
  `gc-top-once.txt`, then starts `gc-top.py -n 5` in `tmux -L verify-city-obs` (180x200),
  waits for `GAS CITY DASHBOARD` and `PROVIDERS`, saves `gc-top-pane.txt` and
  `gc-top-pane.ansi`, and kills that socket (`killed: True`). Compare the `muse-code <state>`
  line in the pane with the phone's state from the Mobile drive: both read fleet.muse_state.
- **Facts.** `$H facts --ev $EV/observability` writes `facts.txt`: per provider family,
  `quota_sub` and `pin_label`, `sub_order`, Claude and Codex logins, the unmapped list, and the
  dry-run drift beside the last order run's `.gc/runtime/ui-drift.json`.
- **Views.** `$H views --ev $EV/observability` (about 30 s) saves
  `gc-visualize-summary.txt` and `mergify-metrics.txt` (7 days).

## Gotchas

- gc-top and gc-pr-top live at the city root, not `dispatch/`.
- gc-top caches `fleet.py` for the life of the process (`routing_module`, `_ROUTING_MOD`). The
  gc-mobile server loads gc-top once at start; its `code_watch` thread exits the server once a
  loaded city `.py` changed and compiles (after 5 min uptime and 10 s settle), and systemd restarts
  it. `obs-mobile-fresh` therefore names only a change older than about 6 min: the watch failed
  or the new code does not compile (journal line `code watch:`). Never restart it as the verifier.
- `GET /api/<name>?refresh=1` wakes a collector run; never pass `refresh`. Every POST route
  (`subscribe`, `unsubscribe`, `test-push`, `alerts/ack`) writes or pushes to the phone.
- Do not run `gc-pr-top.py` directly as a check: when its cache is over 45 s old it rewrites
  `.gc/runtime/fleet/pr-pipeline-cache.json`. Read `/api/prs` instead.
- `city-metrics.py report` is read-only but takes about 2 min (gh and bd). `record` appends to
  `dispatch/ledgers/city-metrics.jsonl`. Read `/api/flow` instead.
- `mergify-metrics.py --reconcile` appends to `dispatch/ledgers/mergify.jsonl` after asking
  GitHub. Without the flag it only reads.
- `gc-visualize.py audit --fix` runs `gc bd recompute-blocked` and `graph -o/--html` writes a
  file. `summary`, `work`, `loop` and `graph` without an output path only read.
- `ui-drift-check.py` with no flag writes `.gc/runtime/ui-drift.json` and the stamp, and can
  mail the mayor. `--changed` only reads. Use `--dry-run`. It checks maps and pins, not state
  words, so `obs-states` covers what it misses.
- gc-top in TUI or `--once` mode appends stderr to `.gc/runtime/fleet/gc-top.err`. On the
  train coordinator its probe briefly flocks `merge-trains/local-slot-*.lock`. The gc-mobile
  server makes the same probe every 10 s, so one drive adds nothing new.
- gc-top's live frame is longer than a normal pane. The drive uses a 200-row window and
  `capture-pane -S -400`, or the header scrolls off.
- The facts drive calls `quota_sub` on every provider, including ones no pin uses (the
  `opencode-*` pools), so its unmapped list can be longer than gc-top's UNMAPPED footer. The
  footer and ui-drift only count pins in use.
