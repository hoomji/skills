# Supervisor and reconciler

One `gc supervisor` per `GC_HOME` hosts every registered city: it starts a controller per
city, which reconciles desired agents and named sessions against the runtime, fires orders
on their triggers, and records each step as an event. The user sees it through
`gc supervisor status`, `gc cities`, `gc status` ("Controller: supervisor-managed (PID n)"),
`gc events` and the supervisor log; `gc suspend`/`gc resume` and config edits are the
inputs it converges on.

## Sub-features

- `sup-start` a bare `gc supervisor run` under its own `GC_HOME` binds the configured port and prints `Supervisor API listening on` and `Dashboard:` lines.
- `sup-register` `gc register <city>` adds the city to `$GC_HOME/cities.toml`; the supervisor starts its controller (`controller.started`) and `gc cities` lists it.
- `rec-sessions` the controller creates a session bead per named session and drives it `start-pending` → `creating` → `active`/`awake` (`bead.updated`, `worker.operation`, `session.woke`).
- `rec-orders` cooldown and event orders fire and complete or fail (`order.fired`, `order.completed`, `order.failed`) on their interval.
- `rec-suspend` `gc suspend` / `gc resume` reach the supervisor through the API, write `.gc/runtime/suspension-state.json`, emit `city.suspended`/`city.resumed`, and `gc status` follows.
- `sup-live` the live supervisor's unit, uptime, build and running city are readable without touching it.

## How to get to it (user POV)

- `gc supervisor start|run|status`, `gc register`, `gc cities`, `gc status`, `gc events`,
  `gc suspend`, `gc resume`; `gc supervisor logs` tails `$GC_HOME/supervisor.log`.
- Docs: `docs/reference/events.md`, `docs/getting-started/how-gas-city-works` (corpus).

## Driving it with gascity.py

Preconditions:

- `$H launch` succeeded: `EV/transcripts/*-register.txt` shows
  `Registered city 'vgc-<run>'` and `City started.`

- **Start.** `grep -n 'listening\|Dashboard' /tmp/vgc-$RUN/supervisor.out` shows both lines
  with the instance port. `$H gc $RUN -- supervisor status` prints
  `Supervisor is running (PID <supervisor_pid>)`.
- **Register.** `$H gc $RUN -- cities` lists `vgc-<run>  /tmp/vgc-<run>/city`;
  `cat /tmp/vgc-$RUN/gc-home/cities.toml` names the same path. `~/.gc/cities.toml` is
  unchanged (it lists only `~/city`).
- **Sessions.** `$H gc $RUN --name ev-session -- events --since 10m --type session.woke`
  prints one line with `"subject":"mayor"`; `$H api $RUN '/v0/city/{city}/sessions'` shows
  `mayor` `state: active, running: true`.
- **Orders.** `$H gc $RUN -- events --since 10m --type order.completed` lists
  `beads-health`, `cross-rig-deps`, `convoy-autoclose-backstop` ...; `--type order.failed`
  lists `gate-sweep` (see Gotchas). Wait about 70 s and run it again: a new
  `beads-health` completion appears (60 s apart in run 20261019T155212Z although its
  cooldown is 30 s), which is the loop ticking.
- **Suspend.** `$H gc $RUN --name suspend -- suspend`, then `$H gc $RUN -- status`
  twice: the second reads `Suspended:  yes` (the first can be stale, see Gotchas),
  `cat /tmp/vgc-$RUN/city/.gc/runtime/suspension-state.json` has `"suspended": true`,
  `$H api $RUN '/v0/city/{city}'` has `"suspended": true`, and
  `$H gc $RUN -- events --since 1m --type city.suspended` prints the event with
  `"actor":"human"`. Then `$H gc $RUN -- resume` and the same three sources read false /
  `city.resumed`.
- **Live (read only).** `$H doctor live`; `$H api live /health` (`uptime_sec`, `build_id`,
  `cities_running`, `startup.phase: running`); `$H live -- supervisor status`;
  `$H live -- events --since 5m --type order.completed`;
  `tail -n 50 ~/.gc/supervisor.log`; `journalctl --user -u gascity-supervisor --since -1h`.

## Gotchas

- The supervisor refuses a `HOME` that differs from the passwd entry unless
  `GC_SUPERVISOR_ISOLATED_HOME=1`; the harness sets it. Without the service-manager shims,
  `gc init`/`start` would hand the supervisor to `systemctl --user` and install a unit.
- The core `gate-sweep` order fails on every run in a file-backed city: its script calls
  `gc bd`, which refuses non-bd providers. Expected noise in isolation, not a regression of
  the change under test.
- A port at or above 32768 makes the supervisor warn `binding to ephemeral port ... set
  port = 8372 in ~/.gc/supervisor.toml` — the path in that message is hardcoded even under
  another `GC_HOME`. The harness picks 18300-18999 to avoid it.
- `gc supervisor reload`, `stop`, `start`, `install` are instance-only verbs. The harness's
  cleanup never runs `gc supervisor stop`; it signals the recorded pgid.
- `gc suspend`/`resume` write the suspension file and emit the event at once, but the first
  `gc status` afterwards renders the supervisor's cached status view from before the change
  (seen at 3 s and 8 s); the second call is current. The file, the API and the event are
  the immediate proof; status is the lagging one.
