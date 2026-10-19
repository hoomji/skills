---
name: verify-gascity
description: Verify the Gas City `gc` binary itself (the hoomji/gascity fork at ~/src/gascity, branch city-next, which the live city runs) by driving a throwaway isolated city with its own supervisor — the CLI read surface (status, session list, order list/history, mail inbox, formula list/show, events), the supervisor/controller reconciler loop, formulas and graph.v2 workflows, and the supervisor's REST API and web dashboard — and reading the live city through a read-only allowlist. Use when proving a gc fix or a city-next build before it is staged, when a gc command behaves unexpectedly, when checking a gc doc claim against the binary, or when /maintain-verification-skill audits this map.
---

# Verify gascity

The app is `gc`, one Go binary that is both the CLI and the machine-wide supervisor (the
reconciler, order dispatcher and the HTTP API + embedded dashboard on one port). Source:
`~/src/gascity` (a working checkout; its current branch is often not `city-next`, and it
may be dirty). The live city at `~/city` runs a staged build of `city-next`
(`readlink -f $(command -v gc)` → `~/src/gc-staged/gc-<sha>.d/gc`) under
`gascity-supervisor.service`, API on `127.0.0.1:8372`, city name `city`.

**The live city is production.** Every proof that changes state runs against an isolated
instance this skill launches. The live city is read only through `gascity.py live` and
`gascity.py api live`, which refuse anything outside a read allowlist. Never run
`gc start/stop/restart/suspend/resume`, `gc order run/check`, `gc sling`, `gc mail send/read`,
`gc bd create/update/close`, `gc session kill/peek`, `gc supervisor *` (except `status`) or
`gc events rotate` against `~/city`; never touch the `city` tmux socket, `~/.gc`, or the
`gascity-supervisor` unit; never bwrap/unshare (panics this kernel).

Harness: `.claude/skills/verify-gascity/scripts/gascity.py` (`--help` lists subcommands). Below,
`H=~/projects/skills-verify-agent-context/skills/projects/verify-gascity/scripts/gascity.py`
(or the installed skill's `.claude/skills/verify-gascity/scripts/gascity.py`). Feature map:
[`features/README.md`](features/README.md). gc facts come from the docs corpus
(`~/src/gascity/docs`, or `~/.cache/gascity-docs/docs`; the gc-docs skill) and from
`git -C ~/src/gascity show city-next:<path>`, never from the dirty working tree.

## Launch

Pick the binary:

- The live staged build (default; same code as `city-next` when doctor live says so):
  `$H launch --run $RUN` uses `command -v gc`.
- A fresh build of a ref, when proving a change not yet staged:
  `BIN=$($H build --ref city-next)` (git-archives the ref into `/tmp/vgc-build-<sha>/src`,
  builds under `resource_guard.py --permit go --timeout 1800`, CGO off; the permit can queue
  for many minutes on a loaded host (25 min and 100 s in the 10-19 runs; peak 2.5 GB) —
  wait, never bypass the guard), then
  `$H launch --bin $BIN --run $RUN`.

`RUN=$(date -u +%Y%m%dT%H%M%SZ)`. Launch builds `/tmp/vgc-$RUN/`: its own `GC_HOME`
(`gc-home/supervisor.toml` with a free port in 18300-18999), `HOME`, `XDG_RUNTIME_DIR`,
`TMUX_TMPDIR`, a seeded gitconfig, shims that make `systemctl`/`launchctl`/`loginctl`/
`systemd-run` exit 1 (so gc bare-starts and never installs a unit), `GC_BEADS=file`,
`GC_DOLT=skip`, `GC_SESSION=fake` (no agent process, no tmux, no provider quota). This is
the recipe of `test/acceptance/helpers/env.go` `NewEnv`. It then runs
`gc init --no-start --skip-provider-readiness --template minimal --providers claude
--default-provider claude --name vgc-$RUN city`, starts `gc supervisor run` with setsid
(pid and pgid recorded in `/tmp/vgc-$RUN/instance.json`), waits for `/health`, and runs
`gc register`. Ready when launch prints the run id and
`GET /v0/city/vgc-<run>/status` answers 200 (launch waits for both).

## Doctor

`$H doctor $RUN` — one line per finding, exit 1 on any, `doctor: clean` otherwise. Checks:
the recorded supervisor pid is alive and owns the port (`ss -ltnp`), `/health` and the city
status API answer 200, the binary's `version --long` still matches the launch, `gc status`
exits 0, and no tmux or dolt process carries this run's `GC_HOME` (fake sessions and
`GC_DOLT=skip` spawn neither). First line names version, pid, port, city and the run's
processes.

`$H doctor live` — `gascity-supervisor.service` active, live `/health` 200, the live gc's
commit equals `city-next` (a mismatch means the staged binary trails or leads the fork:
say which one you verified), and `gc status` on `~/city` exits 0. Run it before any live
read and record it.

## Drive

Isolated instance (any gc verb is allowed here; it is ours):

- `$H gc $RUN [--name LABEL] -- <gc args>` runs gc in the instance env from the city dir and
  writes a transcript. Or `eval "$($H env $RUN)"` and type plain `gc` (the env is complete:
  it `cd`s into the city and exports `VGC_API`).
- `$H api $RUN [--name LABEL] <path>` GETs `<path>` from the instance supervisor; `{city}`
  in the path becomes the city name. Routes are in
  `git -C ~/src/gascity show city-next:docs/reference/schema/openapi.json` (84 GETs).
- Mutations on the instance go through gc verbs (`gc sling`, `gc suspend`, `gc formula cook`),
  which take the API path when the supervisor is up, exactly as a user's would.

Live city (read only):

- `$H live [--name LABEL] -- <gc args>` runs `gc --city ~/city <args>` only for: `version`,
  `status`, `cities`, `session list`, `order list|show|history`, `formula list|show`,
  `bd list|show|ready|count`, `mail inbox|count`, `events` (no `--follow`/`--watch`),
  `supervisor status`, `dashboard serve`, `metrics status` (`config show` is left out: it dumps resolved provider env). Anything else
  exits 2 with `refused: ...`.
- `$H api live <path>` GETs from `127.0.0.1:8372`; `{city}` becomes `city`. It refuses
  `/runs*` (a lazy cold replay of the whole event log inside the live supervisor),
  `.../stream` and `/orders/check`.
- `$H live` sets `XDG_RUNTIME_DIR=/run/user/<uid>` when the shell lacks it; without it
  `gc events`/`gc dashboard` cannot find the live supervisor's socket.
- The supervisor log is `~/.gc/supervisor.log` (read with `tail`/`grep`, never rotate);
  the unit journal is `journalctl --user -u gascity-supervisor --since -1h`.

Feature files give the per-feature commands.

## Evidence

Everything lands in `~/.local/state/verify-gascity/$RUN/` (`EV`): `instance.json`,
`transcripts/NN-<label>.txt` (timestamp, cwd, exact argv, exit code, stdout, stderr) for
every `gc`/`live` call, `api/NN-<label>.<json|html>` bodies with their
`transcripts/NN-api-<label>.txt` (URL, status, headers), and after cleanup
`supervisor.out`, `supervisor.log`, `city-events.jsonl`, `city.toml`, `cleanup.txt`. Save
doctor output with `$H doctor $RUN > $EV/doctor.txt`. Write `$EV/notes.md`: feature id,
the commands (by transcript number), the observed end state, verdict. Live-only runs use
`VGC_RUN=live-<ts>` so their transcripts collect in one dir.

Proof standards: drive the user's path (the gc verb or the documented API route), not a Go
test or an internal setter. Capture the action and the resulting state from a second
source: a CLI write is proven by the API or the events log, an API read by the CLI or the
file it reflects (`.gc/runtime/*.json`, `.gc/events.jsonl`). A `--dry-run` proves nothing
about the real path. `GC_SESSION=fake` keeps session state inside the supervisor process,
so session liveness is read from the API, never from a second CLI process (see the
reconciler feature). A finding against the live city is reported, never fixed from this
skill.

## Cleanup

`$H cleanup $RUN` copies the logs, events and config into `EV`, signals only the recorded
supervisor pgid and the pids whose environ carries this run's `GC_HOME` (TERM, then KILL),
confirms none survive and the port is free, then removes `/tmp/vgc-$RUN`. It never calls
`gc supervisor stop` (a wrong `GC_HOME` would aim it at the live supervisor) and never
kills by name. Exit 1 means survivors or a held port: it keeps the instance dir and lists
them in `cleanup.txt`. A build dir `/tmp/vgc-build-<sha>` is reusable; remove it with
`rm -rf` when done. `EV` stays: `ls $EV` after cleanup is the last step of every proof.
Run cleanup after a failed launch too.

## Helpers

`.claude/skills/verify-gascity/scripts/doctor.sh` runs `gascity.py doctor live` (read-only); the city's weekly
`verify-skill-doctors` order calls it and mails the mayor `VERIFY-SKILLS:` when it fails.

`.claude/skills/verify-gascity/scripts/gascity.py` (Python 3, stdlib only):

```
$H build [--ref city-next] [--out DIR]          # prints the built gc path
$H launch [--bin PATH] [--run RUN]              # prints RUN
$H doctor (RUN | live)
$H env RUN                                      # eval "$($H env RUN)"
$H gc RUN [--name LABEL] [--timeout S] -- <gc args>
$H live [--name LABEL] [--timeout S] -- <gc args>
$H api (RUN | live) [--name LABEL] [--max-time S] [--print-limit N] <path>
$H cleanup RUN [--keep-instance]
```
