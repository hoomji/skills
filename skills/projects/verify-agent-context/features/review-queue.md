# review-queue

The review-queue seat (`agents/review-queue/`; provider in its `agent.toml`) works the admin
Supply > Review queue: it resolves ref-stack items through `dispatch/review_queue.py` with cited
evidence, files gap beads itself through `dispatch/route.sh` (its one exception to "one filer"),
and mails the mayor `REVIEW DIGEST:`. It wakes on `review-queue-pass` when
`orders/scripts/review-queue-check.sh` sees a box rise or an item age.

## Sub-features

- `rq-wake` the nudge and the pass formula give the Seat contract's wake order.
- `rq-refs` every path, script and memory name the prompt names exists.
- `rq-doors` every helper call in the prompt's door table is a `review_queue.py` subcommand with those arguments.
- `rq-stack` step 1's ref-stack relaunch matches who owns the stack now (the `wall-e2e` order during the wall, the trampoline memory otherwise) and needs no `--resource` reservation from the seat shell.
- `rq-authority` the prompt's authority rules (ref writes only, dev and prod read-only, money undecided) agree with the owner rulings in the mayor's memory.
- `rq-memory` the seat's memory copies are in step.
- `rq-pass` a pass that closed after the last context change resolved, digested and filed as the loop asks.

## How to get to it (user POV)

- `orders/review-queue-pass.toml` runs `orders/scripts/review-queue-check.sh`; a new signature
  routes a pass bead to the seat.
- The woken session reads the `nudge` in `agents/review-queue/agent.toml`, the step text of
  `formulas/review-queue-pass.toml` and `.gc/runtime/fleet/seats/review-queue/pending.txt`.

## Driving it with context.py

Preconditions:

- Doctor ran this pass. `gc order list | grep review-queue-pass` shows the order.

- **Render.** Run `context.py render review-queue $EV`.
- **Wake order.** Compare `$EV/review-queue.wake.md` with `docs/delegated-seats.md` "Seat
  contract" (mail, claim, confirm signature, `pending.txt`, memory, close with `--actor`). Each
  difference is recorded.
- **Paths.** Run `context.py refs agents/review-queue/prompt.template.md`. Every line reads `ok`.
  Each memory the prompt names by slug exists in `agents/review-queue/memory/`.
- **Doors.** Run `grep -n 'add_parser\|choices' dispatch/review_queue.py`. Every subcommand,
  positional and flag in the door table and the loop appears.
- **Stack.** `ls .gc/runtime/wall-e2e/state.json` decides the owner: present means step 1 defers
  to the `wall-e2e` order. The heavy-command rule names `--permit <class>`, and each class it
  could use is a key in `.gc/runtime/fleet/resource-policy.json` `commands`.
- **Authority.** Compare the "Authority" bullets with the mayor memories
  `baseline-sweep-owner-rulings`, `sell-models-aggressively` and
  `owner-rulings-2026-10-18-fee-refunds-scope`. A rule the owner superseded is drift.
- **Memory.** Run `context.py seat-memory review-queue`. Output is `review-queue: seat memory in step`.
- **Last pass.** Run `context.py last-pass review-queue > $EV/review-queue.last-pass.json` and
  `tail -5 .gc/runtime/fleet/seats/review-queue/resolutions.jsonl`. With `prompt_newer: false`,
  the close reason names resolutions or gaps that appear in the resolutions log.

## Gotchas

- The seat shell runs inside a `fleet-resource-*.scope`: `resource_guard.py --resource` refuses
  there as a nested reservation, and a `systemd-run --user` unit started from it stays nested.
- `open_model` and `open_evidence` are read-only panel actions; the helper has no subcommand
  for them, by design.
- `review_queue.py --help` is safe; the helper holds the dev staff header in memory, so never
  print a request it builds.
