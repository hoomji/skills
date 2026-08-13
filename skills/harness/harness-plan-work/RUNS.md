# Harness-plan-work runs

## 2026-08-11 — initial contract suite

The execution-plan asset passed its static contract test. Frontmatter and folder naming
passed an equivalent YAML check; the bundled `quick_validate.py` could not run because
PyYAML is absent from the available Python runtimes. Repository trials in `EVALS.md`
remain open, so Milestone 3 is ready for trials, not complete.

Reproduce the contract check with
`python3 -m unittest discover -s skills/harness/harness-plan-work/tests -v`.
Result: **2/2 passing**.

## 2026-08-11 — `auto-route` missing-runtime forward test

A fresh agent planned a task-local, read-only heartbeat e2e log query against
`henry/ai-workflow@7d035348`. The plan fixed the dirty baseline and R0 boundary, cited
eight repository sources, separated broad observability from the narrow query capability,
mapped eight acceptance criteria to static and runtime evidence, and produced three
milestones with rollback and two explicit human gates. It edited no files.

The test exposed no output-contract gap. A separate evidence review did expose that the
skill could invoke issue-publishing planning helpers despite its R1 ceiling; the skill now
requires local/in-chat use and forbids publishing from the planning workflow.
