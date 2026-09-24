---
name: perf-baseline
description: Write down how fast a repository's user journeys are today, in a form a ratchet can hold. Use when asked to establish or refresh a performance baseline, when a repo has no written latency numbers, or when hill-climbing finds no baseline row for a journey.
---

# Performance baseline

A **baseline** is a written row per journey: the field number at a named percentile and warm state, and the lab count that predicts it, at a named commit. Until it exists a "win" is a claim and a regression is invisible. This skill produces the file, the lab that fills it, and the doc that tells the next agent how to read it.

Two measures, defined in [`hill-climbing`](../hill-climbing/SKILL.md): **lab** (deterministic count) and **field** (production percentile).

## Steps

### 1. Name the journeys

List what a user does with this system, as verbs, and pick the ones that carry the product. Four is the usual number. For each, name the entry point in code and the percentile the team will climb (p75 by default; p95 when the tail is the complaint).

Done when each journey has `name / entry point / percentile / warm or cold`.

### 2. Read the field, if it exists

For each journey, read the current field number from production telemetry or the repository's existing timing harness. Write "not measured" where nothing exists rather than a guess; a blank is a finding.

Done when every journey row has a field number or "not measured", with the source named.

### 3. Build the lab

Pick the measure from [`MEASURES.md`](../hill-climbing/MEASURES.md) by runtime. Drive each journey's entry point in-process with a fixed request and a stubbed dependency (a canned provider reply, a fixture stream), warm it, then count a fixed number of iterations.

The lab lives where the repository already keeps measurement tooling, runs from one command, prints the row per journey, and exits non-zero on a lab that could not run (distinguish "could not measure" from "measured and slow"). Wall clock rides along as a printed correlate and is never the number.

Done when two consecutive runs print identical counts for every journey.

### 4. Check the numbers in

Write the counts to the baseline file in the shape `MEASURES.md` gives, with the commit and runtime version they were measured at. Add the compare mode that fails when a count rises above the file (that is the ratchet's first rung; `perf-ratchet` wires it into CI and lowers it on wins).

Done when `<lab> --check` passes on the measured commit and fails when a count in the file is lowered by hand.

### 5. Write it down where agents look

One doc beside the repository's other tool docs: what each journey is, how the lab drives it, what the counts do and do not mean, the field source per journey, and the rule for moving a number. Add the lab's command to whatever index the repository's agents read first (the harness manifest, `AGENTS.md`, a tools index).

Done when a reader who has only the doc can run the lab, read one row, and say what would make it red.

## The baseline is a floor

Numbers in the file only fall through `perf-ratchet`. A number that has to rise is a named decision recorded beside it, with the commit that forced it, so a reader can tell a regression somebody accepted from one nobody noticed.
