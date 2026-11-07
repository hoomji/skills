---
name: perf-ratchet
description: Lock in a measured performance win so it cannot regress silently. Use when a lab count fell after a change, when asked to ratchet or lower a ceiling, to add a perf check to CI or a nightly job, or when a perf gate went red on a change that touched nothing near it.
---

# Performance ratchet

A **ratchet** turns one direction of movement into the only direction allowed. A checked-in **ceiling** per journey holds the lab count; a run compares the live count against it; a rise is red and a fall lowers the ceiling in the same change. The repository remembers every win without anyone remembering to look.

## Rules

- **Compare live against checked in.** The ceiling is a number in a file at a named commit, and the check runs the lab on the tree under test. Never compare two stored numbers.
- **A fall lowers the ceiling in the same PR.** The win and its lock land together, so the next change is judged against it.
- **A rise is red.** Tolerance is zero for a deterministic count. Where a measure carries small run-to-run variance despite `--predictable`, state the tolerance in the file beside the count, and keep it under one percent.
- **Raising a ceiling is a decision, not an edit.** The PR that raises one names the commit that forced it and the owner who accepted it, in the file, beside the number.
- **Red on an untouched path is a question, not a fix.** Reproduce on the base commit first (the same-red-on-both rule): red on both means the ceiling went stale under someone else's merge, and the fix is a ceiling PR that names that merge. Red only on the change means the change did it, whatever it looked like it touched.

## Steps

### 1. Read the win

Run the lab on the base and on the change. Write the pair per journey.

Done when each journey shows `base count / change count / delta`.

### 2. Lower the ceiling

Set each fallen journey's ceiling to the new count. Leave a journey that did not move alone. Record the commit and runtime version the counts were measured at.

Done when `<lab> --check` is green on the change and red when any lowered ceiling is raised back by hand.

### 3. Wire the check

The lab's check runs where the repository's other gates run: the CI job that runs on pull requests, and a nightly job when the field signal can only be read from a deployed target. The check exits with the repository's convention for pass, fail, and could-not-run, so an unavailable lab is never a green.

Done when one CI or nightly run has gone green on the ceiling and a deliberate regression (a hand-raised count in a scratch branch, or the lowered ceiling with the old code) has gone red.

### 4. Update the baseline row

The field number for the journey, at its percentile and warm state, read after the deploy, replaces the baseline row along with the new lab count.

Done when the baseline row and the ceiling carry the same lab count and the field number has a date.
