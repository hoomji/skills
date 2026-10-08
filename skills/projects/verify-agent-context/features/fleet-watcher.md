# fleet-watcher

The fleet-watcher seat (Codex, `agents/fleet-watcher/`) diagnoses tripped fleet health probes
read-only and mails the mayor a cause with evidence. It wakes on `fleet-watcher-pass` when
`orders/scripts/fleet-watcher-check.sh` writes probe lines to `pending.txt`.

## Sub-features

- `fw-wake` the nudge and the pass formula give the Seat contract's wake order.
- `fw-refs` every path, order and timer the prompt names exists.
- `fw-probes` every line shape the check script emits has a handler, and no handler names a probe the script never emits.
- `fw-memory` the seat's memory copies are in step.
- `fw-pass` a pass that closed after the last context change diagnosed what `pending.txt` held.

## How to get to it (user POV)

- `orders/fleet-watcher-pass.toml` fires on the check script's new signature.
- The seat reads `.gc/runtime/fleet/seats/fleet-watcher/pending.txt`, the nudge and the formula step text.

## Driving it with context.py

Preconditions:

- Doctor ran this pass.

- **Render.** Run `context.py render fleet-watcher $EV`.
- **Wake order.** Compare `$EV/fleet-watcher.wake.md` with `docs/delegated-seats.md` "Seat
  contract" (mail, claim, confirm signature, `pending.txt`, memory). Each difference is recorded.
- **Paths.** Run `context.py refs agents/fleet-watcher/prompt.template.md`. Every line reads `ok`.
  The order names and timer in the prompt are plain text: each order appears in `gc order list`
  and `tmp-reaper.timer` in `systemctl --user list-timers`.
- **Probes.** Run `grep -nE 'echo|print' orders/scripts/fleet-watcher-check.sh`. Shapes are
  `ryzen mem-available …`, `ryzen swap …`, `ryzen /tmp …`, `ryzen / …`,
  `job <id> no receipt <N>h state=<state>` and `session.stranded x<N> in recent events`.
  Each matches one prompt handler and every handler matches a shape.
- **Memory.** Run `context.py seat-memory fleet-watcher`. Output is `fleet-watcher: seat memory in step`.
- **Last pass.** Run `context.py last-pass fleet-watcher > $EV/fleet-watcher.last-pass.json`.
  With `prompt_newer: false`, the `close_reason` names a cause for the probe lines.

## Gotchas

- New reaper orders and timers land often; the prompt's "existing orders" list goes stale
  first. Diff it against `gc order list` each pass.
- Thresholds live in the check script; a prompt that repeats one is a cache to report.
