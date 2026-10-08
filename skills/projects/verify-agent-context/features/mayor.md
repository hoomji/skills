# Mayor

The mayor wakes on `gc prime mayor` (Claude, `agents/mayor/prompt.template.md`) plus its
memory index, and plans, files, routes and adjudicates for the whole city. Its prompt is the
city's widest pointer surface: digest and routing scripts, the merge gate, liveness and
turn-ending rules, and the docs it sends the mayor to.

## Sub-features

- `mayor-render` the prompt renders under `gc prime --strict mayor` within its prompt budget.
- `mayor-refs` every script, doc and path the prompt names exists in the city or the gc docs corpus.
- `mayor-flags` every subcommand and flag the prompt passes to a city script is accepted by that script.
- `mayor-policy` each rule the prompt states agrees with the doc it points at and with the seat prompts that defer to it.
- `mayor-live` the running mayor session primed after the last prompt commit.

## How to get to it (user POV)

- The supervisor starts or resumes the `mayor` session, which runs `gc prime mayor`.
- A handoff, the PreCompact hook (`gc handoff --auto`) or a reset re-primes it; the
  SessionStart hook in `hooks/claude.json` runs `gc prime --hook` on resume.
- The prompt's "Every wake" step tells the mayor to read `.claude-memory/MEMORY.md` on either provider.

## Driving it with context.py

Preconditions:

- Doctor ran this pass; the city answers `gc status`.

- **Render.** Run `context.py render mayor $EV 2> $EV/mayor.budget.txt`. `$EV/mayor.prompt.md`
  exists and `mayor.budget.txt` reads `hard_fail=false`.
- **Paths.** Run `context.py refs agents/mayor/prompt.template.md`. Every line reads `ok`.
  Paths outside backticks (`docs/merge-train.md`, `docs/gitbutler-restack.md` in "Merge gate")
  are checked with `ls`.
- **Flags.** `route.sh` hands every command but `backlog` to `dispatch/fleet.py`, so check its
  flags with `grep -n 'choices=' dispatch/fleet.py`; `mayor-digest.py` with `grep -n 'choices=' dispatch/mayor-digest.py`;
  `land.sh` and `merge-train.sh` by reading their usage header (`sed -n 2,45p`) and `case`
  arms. Each subcommand and flag the prompt uses appears.
- **Policy.** Compare "Merge gate" with `docs/merge-queue.md` (the Mergify rules and pretest
  gate), `docs/merge-train.md`, `docs/gitbutler-restack.md` and `docs/ci-controller.md`, and
  "Filing and routing" with `docs/fleet-lifecycle.md`. Each rule reads the same in prompt and
  doc, and a seat prompt that defers to the mayor's section agrees with it.
- **Live.** Run `context.py primed mayor`. `on_current_context: true`; `reset_pending: true`
  with `false` means the running mayor is on an older prompt until its reset runs.

## Gotchas

- `docs/tutorials/...`, `docs/reference/...` and `docs/guides/...` are gc docs corpus paths
  (`gc-docs`); `refs` resolves both.
- Merge mechanics change fastest (trains, then stacks, merge queue and Mergify); read
  `docs/merge-queue.md` and the scripts' gate switches (`CITY_PRETEST_GATE`) before trusting
  any pretest or landing rule in the prompt.
- Under the Mergify ruleset every open develop PR reads `mergeStateStatus=BLOCKED`; a gate
  rule that treats BLOCKED as failing is drift.
- The mayor's memory carries owner rulings; a rule in both prompt and memory is duplication
  to report, not two confirmations.
