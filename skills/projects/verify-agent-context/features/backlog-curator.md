# backlog-curator

The backlog-curator seat (Codex, `agents/backlog-curator/`) proposes restocks and stale-bead
closures to the mayor by mail and files nothing. It wakes on `backlog-curator-pass` for a
daily sweep, a thin ready queue or stale in-progress leases.

## Sub-features

- `bc-wake` the nudge and the pass formula give the Seat contract's wake order.
- `bc-refs` every path and script the prompt names exists.
- `bc-probes` every line shape the check script emits has a step in the prompt.
- `bc-readonly` the prompt's commands write only what the Seat contract allows.
- `bc-memory` the seat's memory copies are in step.
- `bc-pass` a pass that closed after the last context change mailed proposals and filed nothing.

## How to get to it (user POV)

- `orders/backlog-curator-pass.toml` fires on `orders/scripts/backlog-curator-check.sh`'s new signature.
- The seat reads `.gc/runtime/fleet/seats/backlog-curator/pending.txt`, the nudge and the formula step text.

## Driving it with context.py

Preconditions:

- Doctor ran this pass.

- **Render.** Run `context.py render backlog-curator $EV`.
- **Wake order.** Compare `$EV/backlog-curator.wake.md` with `docs/delegated-seats.md` "Seat
  contract". Each difference is recorded.
- **Paths.** Run `context.py refs agents/backlog-curator/prompt.template.md`. Every line reads `ok`.
- **Probes.** Run `grep -nE 'echo|print' orders/scripts/backlog-curator-check.sh`. Shapes are
  `daily sweep <date>`, `ready beads: N (< 3) at <YYYY-MM-DDTHH>` and
  `stale in_progress leases: N (> 12h)`. Each has a prompt step.
- **Read-only.** The Seat contract allows mail read/archive, the pass claim, the signature
  copy, the seat's own memory commit and closing the pass bead. Every other command in the
  prompt only reads: no `--fix`, no `gc bd create|update|reclaim|recompute-blocked`, no
  `sling` or `route.sh file`, and no close of any bead but the pass. CLOSE in a proposal is a
  mail verb, not a command.
- **Memory.** Run `context.py seat-memory backlog-curator`. Output is `backlog-curator: seat memory in step`.
- **Last pass.** Run `context.py last-pass backlog-curator > $EV/backlog-curator.last-pass.json`.
  With `prompt_newer: false`, the `close_reason` names proposals mailed and no bead filed or closed.

## Gotchas

- Tools grow write flags (`gc-visualize.py audit --fix` did); re-check the read-only rule when
  a script the prompt runs changes.
- The thin-queue line carries an hour stamp, so it re-fires every throttle window while the
  queue stays thin; repeated identical proposals are expected, not drift.
