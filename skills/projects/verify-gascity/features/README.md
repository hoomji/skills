# gc verification map

This directory is the maintained source for verifying the Gas City `gc` binary built from
the hoomji/gascity fork (`city-next`). Read the index, then use the matching feature file
as the recipe.

## Baseline preconditions

- An isolated instance is up: `$H launch --run $RUN` printed the run id and
  `$H doctor $RUN > $EV/doctor.txt` reads `doctor: clean`.
- Before any live read, `$H doctor live` is clean and recorded; it says which commit the
  live gc runs and whether that is `city-next`.
- gc facts are quoted from `git -C ~/src/gascity show city-next:<path>` or the docs corpus,
  never from the working tree (its branch and dirt are someone else's).

## Driving conventions

- State-changing steps run only on the isolated instance (`$H gc $RUN -- ...`).
- Live steps run only through `$H live -- ...` and `$H api live <path>`; a refusal is the
  harness doing its job, not a gap to route around.
- Treat every command as literal; `{city}` in an API path is filled in by the harness.
- With `GC_SESSION=fake`, session liveness lives in the supervisor process: read it from the
  API. A second CLI process builds its own empty fake provider.

## Proof and skip reporting

- Record the feature ID, the transcript numbers and the observed end state in
  `$EV/notes.md`.
- A sub-feature the isolated instance cannot reach (a `gc bd` verb on the file-backed store,
  a real agent turn under fake sessions) is reported `unreachable in isolation` with the
  refusal transcript, and is read on the live city instead when a read can prove it.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph, then exactly four H2 sections in
this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with gascity.py`,
`Gotchas`. The user is an operator at a terminal or a browser on the supervisor port.

## Features

- [CLI read surface](./cli-read-surface.md) covers status, session list, order list/history, formula list, mail inbox, bd reads and events from the terminal.
- [Supervisor and reconciler](./supervisor-reconciler.md) covers the supervisor process, city registration, the controller's reconcile loop, order dispatch and suspend/resume convergence.
- [Formulas and graph.v2 workflows](./formulas-workflows.md) covers formula list/show, a slung formula's workflow root and its step graph.
- [API and dashboard](./api-dashboard.md) covers the supervisor's typed REST API (GET routes) and the embedded web dashboard on the same port.
