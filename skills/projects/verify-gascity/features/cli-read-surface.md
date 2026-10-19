# CLI read surface

The commands an operator types to see a city: `gc status` (controller, agents, named
sessions, store health), `gc session list`, `gc order list` / `history`, `gc formula list`,
`gc mail inbox` / `count`, `gc bd list|show|ready`, `gc events`. They resolve the city
from `--city` or the cwd, and most read through the supervisor's API when it is up
(`apiClient(cityPath)` in `cmd/gc`), falling back to the files and store directly.

## Sub-features

- `cli-status` `gc status` and `gc status --json` name the controller PID and authority, the suspended flag, each agent's running state and the store health block.
- `cli-sessions` `gc session list` lists session beads with template, state and reason.
- `cli-orders` `gc order list` lists every order with type, trigger and interval; `gc order history [name]` lists runs.
- `cli-mail` `gc mail inbox` and `gc mail count` read the human inbox without marking anything read.
- `cli-bd` `gc bd list|show|ready` pass through to bd in the right scope (bd-backed stores only).
- `cli-events` `gc events --since <d>`, `--type <t>` and `--seq` read the city event log as JSONL.

## How to get to it (user POV)

- `cd` into a city directory (or pass `--city <dir>`) and run the command.
- `gc --help` and `gc <cmd> --help` list the verbs; `docs/reference/cli.md` in the corpus.

## Driving it with gascity.py

Preconditions:

- Isolated instance `$RUN` doctor clean. For the live column, `$H doctor live` clean and
  `export VGC_RUN=$RUN` so live transcripts land beside the isolated ones.

- **Status.** `$H gc $RUN --name status -- status` and `... -- status --json`. Text shows
  `Controller: supervisor-managed (PID <supervisor_pid from instance.json>)`, `Suspended:  no`,
  agents `core.control-dispatcher` and `mayor`, and a `Store health:` block. The JSON
  `agents[].running` agrees with the text. Live: `$H live --name status -- status` names
  `city  /home/coolhenrylinux/city` and the live supervisor PID
  (`systemctl --user show gascity-supervisor -p MainPID`).
- **Sessions.** `$H gc $RUN -- session list` shows a row for `mayor` (template `mayor`);
  compare its STATE with `$H api $RUN '/v0/city/{city}/sessions'` (see Gotchas). Live:
  `$H live -- session list`.
- **Orders.** `$H gc $RUN -- order list` lists the 16 core orders (`beads-health`,
  `gate-sweep`, `reaper`, ...). `$H gc $RUN -- order history beads-health --limit 5` shows
  runs once the controller has fired it (events `order.fired`/`order.completed`). Live:
  `$H live -- order list` and `$H live -- order history <name> --limit 5`.
- **Formulas.** `$H gc $RUN -- formula list` prints the core `mol-*` formulas; live prints
  the city's own formulas (`bmad-*`, `<seat>-pass`, ...).
- **Mail.** `$H gc $RUN -- mail inbox` prints `No unread messages for human`. After a
  `gc mail send human -s probe -m body` on the instance, `mail count` rises by one and
  `mail inbox` lists it; `mail count` again is unchanged (inbox does not mark read). Live:
  `$H live -- mail count` only.
- **bd.** Isolated: `$H gc $RUN -- bd list` exits 1 with `gc bd: only supported for
  bd-backed beads providers (resolved "file" ...)`: record `unreachable in isolation`.
  Live: `$H live -- bd list --limit 5` and `$H live -- bd show <id>`.
- **Events.** `$H gc $RUN -- events --seq` prints the head cursor; `-- events --since 10m
  --type controller.started` prints one line per controller start. Live:
  `$H live -- events --since 5m --type session.woke`.

## Gotchas

- With `GC_SESSION=fake`, `gc session list` from the CLI reports `asleep` for sessions the
  supervisor holds `active` (its fake provider is per-process), and `gc status` can mark one
  agent `running` and another `stopped` in the same run. The API is the truth on the
  isolated instance; on the live city (tmux provider) the CLI and API agree.
- `gc mail read` and `gc mail check --inject` change state; `gc mail peek` does not but is
  off the live allowlist anyway. `gc session peek` reads a tmux pane, which on the live city
  is the `city` socket: refused.
- `gc order check` is a dry evaluation but runs order trigger scripts; it is refused live.
- `gc events` and `gc dashboard` find the live supervisor through
  `$XDG_RUNTIME_DIR/gc/supervisor.sock`. A shell without `XDG_RUNTIME_DIR` (agent shells,
  cron) gets `could not auto-discover the supervisor API ... start the supervisor with
  "gc supervisor start"` while `gc supervisor status` says running (via the service
  manager). Never follow that advice on the live city; `$H live` sets
  `XDG_RUNTIME_DIR=/run/user/<uid>` when it is missing.
- `gc bd ...` against the live city spawns a bd subprocess per call (proxied Dolt): keep
  live bd reads few and bounded (`--limit`).
- With the supervisor up, `gc status` renders the supervisor's cached status view
  (`cmd/gc/cmd_citystatus.go` `cmdCityStatus`). The first call after `gc suspend`/`resume`
  shows the previous state however long you wait (8 s in run 20261019T155212Z); the next
  call is current. Run status twice after any mutation and quote the second.
