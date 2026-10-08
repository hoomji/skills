# ci-controller

The ci-controller seat (Codex, `agents/ci-controller/`) takes fleet PRs from reviewed to
landed: mergeability upkeep, pretest, the merge queue and restacks. It wakes on its
`ci-controller-pass` order, follows the Seat contract (mail, claim, confirm the signature,
`pending.txt`, memory), runs its loop and mails the mayor.

## Sub-features

- `cic-wake` the nudge and the pass formula give the Seat contract's wake order.
- `cic-refs` every path the prompt names exists.
- `cic-flags` every command the prompt runs accepts the subcommands and flags it passes.
- `cic-probes` every `pending.txt` line shape has a handling step in the prompt.
- `cic-memory` the seat's mayor-sourced memory copies are in step.
- `cic-pass` a pass that closed after the last context change did what the loop asks.

## How to get to it (user POV)

- `orders/scripts/ci-controller-check.sh` writes `.gc/runtime/fleet/seats/ci-controller/pending.txt`;
  a new signature fires the `ci-controller-pass` order, which routes a pass bead to the seat.
- The woken session reads the `nudge` in `agents/ci-controller/agent.toml` and the step text of
  `formulas/ci-controller-pass.toml`.

## Driving it with context.py

Preconditions:

- Doctor ran this pass. `gc order list | grep ci-controller-pass` shows the order.

- **Render.** Run `context.py render ci-controller $EV`. The prompt, memory and wake files exist.
- **Wake order.** Read `$EV/ci-controller.wake.md` beside `docs/delegated-seats.md` "Seat
  contract". The contract's order is mail (read, act, archive), claim (`gc hook --claim --json`,
  never `--drain-ack`), copy `pending-signature` to `last-signature`, read `pending.txt`, then
  MEMORY.md. Nudge and formula follow it, or each difference is recorded.
- **Paths.** Run `context.py refs agents/ci-controller/prompt.template.md`. Every line reads `ok`.
- **Flags.** Read the usage header and `case` arms of each script the prompt runs:
  `merge-train.sh`, `land.sh`, `merge-queue.sh`, `gitbutler-radar.sh`, `zero-lens-eligible.sh`,
  and `grep -n 'add_argument' dispatch/mergify-metrics.py`. Each subcommand and flag appears.
- **Probes.** Run `grep -nE 'echo|print' orders/scripts/ci-controller-check.sh orders/scripts/seat-check.sh`.
  Shapes are the header `# ci-controller pending at <ts>, signature <sig>`,
  `pr <n> <sha8> <mergeStateStatus> <CONCLUSION:n,…>` and `train-file <path> <mtime>`. Each
  shape, and each state in the live `pending.txt` (`BLOCKED`, `UNSTABLE`, `DIRTY`, `CLEAN`),
  has a step in the prompt.
- **Memory.** Run `context.py seat-memory ci-controller`. Output is `ci-controller: seat memory in step`.
- **Last pass.** Run `context.py last-pass ci-controller > $EV/ci-controller.last-pass.json`.
  With `prompt_newer: false`, the `close_reason` names steps the current loop asks for and
  nothing it forbids.

## Gotchas

- The seat prompt defers gate policy to the mayor's "Merge gate" section; re-check that
  deferral whenever either file changes.
- Under the Mergify ruleset `BLOCKED` is the normal state of an open develop PR, not a failure.
- `pending.txt` reflects the last probe, not now; compare its header timestamp.
