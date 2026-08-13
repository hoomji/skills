# Harness-capture-learning runs

## 2026-08-11 — initial contract suite

The learning-ledger entry asset passed its static contract test. Frontmatter and folder
naming passed an equivalent YAML check; the bundled `quick_validate.py` could not run
because PyYAML is absent from the available Python runtimes. Repository trials in
`EVALS.md` remain open, including the important not-encoded case.

Reproduce the contract check with
`python3 -m unittest discover -s skills/harness/harness-capture-learning/tests -v`.
Result: **2/2 passing**.

## 2026-08-11 — one-off preference forward test

A fresh agent received one unsupported request to rename a local variable. It correctly
classified the episode as irreducible judgment, recorded an honest frequency of one, and
chose `not encoded` instead of inventing guidance or enforcement. The first pass left the
review date unscheduled; the skill was tightened to derive a concrete date from manifest
freshness or a labeled 90-day default. The second pass produced `2026-11-09` and retained
the not-encoded disposition. No files were edited.
