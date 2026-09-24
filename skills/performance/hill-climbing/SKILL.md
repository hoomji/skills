---
name: hill-climbing
description: Run the measure, ship, judge, ratchet loop that makes one user journey faster. Use when asked to make something faster or smoother, to cut latency, jank or CPU on a named path, to find the next slow spot in a journey, or to resume a performance thread. When no written baseline exists yet, start with perf-baseline.
---

# Hill climbing

One **journey** (a thing a user does: launch, load a conversation, send a message, serve a completion), one number that says how slow it is today, and a loop that only ever moves that number one way. Every step ends on a check you can read off a file or a dashboard, so the loop can run thread after thread without a human re-deriving where it is.

Two measures, two words, used throughout:

- **Lab**: a deterministic measure of the journey, run on a laptop or in CI, identical for identical input. Instruction counts, function call counts, commits per interaction, layout passes. Never wall clock.
- **Field**: what users experience, read from production telemetry at a named percentile.

The lab is fast to run and cannot lie about noise; the field is the only thing that matters. The lab earns its place by predicting the field, and a lab measure that cannot is **unshipped**.

The positive default this loop runs on: propose the PR, not the ticket. A wait on a merge or a deploy is a request for the owner to shortcut it, said out loud. The target is a floor, so hitting it opens the question "what's next in this journey?" rather than closing the thread.

## Steps

### 1. Identify

Name the journey, the slow moment inside it, and the human owner of the thread. The moment comes from a recording, a screenshot, a field percentile that moved, or a nightly lab run that went red.

Done when one line reads `journey / moment / owner / field signal (percentile)`. If no baseline row exists for that journey, run `perf-baseline` first and come back.

### 2. Measure

Trace the moment to the code that runs, then build the lab measure for it. Pick the measure from [`MEASURES.md`](MEASURES.md) by runtime. The measure takes a fixed input and returns a count, and two runs return the same count.

Then prove it: change something the measure says is hot, and show the field signal (or a warm, repeated wall-clock run when the field cannot be read yet) move the same way. Record the pair, lab delta and field delta, beside the measure.

Done when the measure runs from one command, its count is checked in, its field signal is named, and one correlation pair is written down. A measure with no pair after a real attempt is unshipped and its name added to the unshipped list, so it is not rebuilt.

### 3. Decide

Propose to the owner, in one message: the hot spot, the estimated win in the field signal's units, the blast radius (files, flags, surfaces), and the size of the change. A user-perceptible trade (fill a table cell by cell or wait for the row; skeleton now or at 500ms) comes with a before/after recording.

The owner **gavels**: go, or not worth it. A small win behind a large diff stops here, and that is the step working.

Done when the go is written in the thread, or the proposal is closed with the ruling recorded.

### 4. Ship

Tests before the optimisation, so a behaviour change reads as red before it reads as fast. Split the change into PRs sized for review; each PR carries its lab delta in the description. Anything user-visible ships behind a flag typed at birth as **kill switch** (default off in the loss branch) or **ramp** (percentage that climbs), with an owner and a retire-when written on it.

Done when every PR is merged and deployed with the flag in its starting state.

### 5. Judge

Read the field signal named in step 2 at the thread's percentile, warm, after the deploy. Compare against the baseline row.

- It moved the predicted way: run `perf-ratchet` to lower the lab ceiling to the new count, and update the baseline row.
- It did not, or a guardrail fired: flip the kill switch or hold the ramp, and return to step 2 with what the field taught you.

Done when the baseline row and the ceiling both carry the new number, or the flag is off and the thread notes why.

### 6. Continue or close

Ask what is now slowest in the same journey and go to step 1 with it. Close the thread when the last two wins were under the owner's noise floor, or the owner rules diminishing returns. Closing retires every flag the thread opened whose retire-when has arrived, and leaves the ceiling and the baseline row as the thread's record.

Done when the thread's flags are retired or each has a retire-when still pending, and the journey's baseline row is current.

## Direction, held by the owner

One journey or one measure per thread. When two threads touch the same code, the owner merges them or sequences them; the loop does not decide that. Threads that a nightly lab run opens (a ceiling went red) start at step 2 with the red measure already in hand.
