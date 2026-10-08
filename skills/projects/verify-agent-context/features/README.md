# Agent context verification map

This directory is the maintained source for verifying what each Gas City agent loads on wake.
Read the index, then use the matching feature file as the recipe.

## Baseline preconditions

- Run from the city root, `~/city` on Ryzen, with `gc` on PATH.
- `context.py doctor` has run this pass; its findings are recorded in `$EV/doctor.txt`.
- Read prompts and memory from disk as the agent does; quote code and policy from the live
  file or command, never from memory.

## Driving conventions

- Every drive is read-only: no pass order fired, no nudge, no mail, no store write.
- Treat every command as literal.
- A prompt line that names a flag or subcommand is proven by `<script> --help` or the
  script's argparse `choices=` / `case` arm.
- Two sources that state one rule differently are drift even when both paths exist.

## Proof and skip reporting

- Record the feature ID, the command and its output (or the `MISS` line) in `$EV/notes.md`.
- A seat with no closed pass in `gc order history <seat>-pass` is reported unreachable with
  that command's output, not as verified.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph, then exactly four H2 sections in
this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with context.py`,
`Gotchas`. The user is the agent waking.

## Features

- [Mayor](./mayor.md) covers the mayor's rendered prompt, its named scripts and docs, and its gate rules.
- [ci-controller](./ci-controller.md) covers the CI/CD seat's prompt, wake order, memory copies and last pass.
- [fleet-watcher](./fleet-watcher.md) covers the watcher's prompt, the probe lines it handles, memory and last pass.
- [receipt-grader](./receipt-grader.md) covers the grader's prompt, grade ledger, memory and last pass.
- [backlog-curator](./backlog-curator.md) covers the curator's prompt, probe lines, read-only contract, memory and last pass.
- [Mayor memory](./mayor-memory.md) covers the mayor's memory index, links, frontmatter and the seat copies taken from it.
