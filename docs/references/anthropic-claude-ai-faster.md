# How We Made claude.ai 3x Faster in Two Weeks (Anthropic, 2026-09-23)

**Source:** https://claude.dev/blog/how-we-made-claude-ai-faster/ (Raymond Wang, Sam Attard, Issac G.)
**Captured:** 2026-09-24. **Owner:** hoomji. **Consumers:** `skills/performance/`, the [flow audit](../assessments/2026-09-24-hill-climbing-flow-audit.md).

A capture of the method, not the results. The numbers are kept only where they calibrate a rule.

## The setting

A two-week sprint in August 2026, one Slack channel, one standing brief to an agent ("facilitate all things related to the performance of the claude.ai website and desktop app"), 150+ concurrent threads each owned by a named human, 3,000+ changes, zero customer-facing incidents. Geometric mean across thirteen measurements: 3.1x faster at p75.

## The brief

Four **journeys** chosen up front: launch the app, start a conversation, load a conversation, send a message. Thirteen measurements across web and desktop. About twenty hand-picked initiatives, each with a millisecond estimate; the estimates summed to sprint targets. Twelve of thirteen targets were hit by day three, after which the human asked for a refresh: "what have we not explored, what can we hill climb on?"

## Anything can be hill climbed

Wall-clock timing is noisy, so the sprint built **lab** measurements that are deterministic for a fixed input:

- Node hot paths: instruction counts under Valgrind with `node --predictable`, compared against checked-in baselines. No statistics.
- Browser (no instruction counting in Chromium): V8 call counts from precise coverage, React commits per interaction, layout and style-recalc counts, DOM mutations.

Every lab measure had to prove it predicts wall clock: "please prove that hill climbing against each of these can result in measurable wall clock perf wins. we'll unship the benches for any candidates that cannot prove that." Two calibration points: message-tree assembly, instructions -48% gave wall clock -78%; status-line scanner, instructions -31% gave wall clock -44%.

The central claim: measuring something makes it tractable. Measurement is step one, not a thing you add and wait on.

## The loop, per thread

1. **Identify.** An engineer posts a slow moment (screenshot or recording).
2. **Benchmark.** The agent traces the flow and builds a reproducible lab test.
3. **Implement.** Several PRs sized for risk and review; user-visible changes behind feature flags.
4. **Deploy.** Behind the flag; the agent watches the deploy and field data.
5. **Validate.** A win ratchets the benchmark ceiling down. A loss disables the flag and returns to step 2.
6. **Continue.** Next slow spot in the same journey.

Threads stayed open for long optimisation passes (50 to 100 PRs each). The agent opened new threads from what it found during investigations and nightly jobs.

## Guardrails

- Automated review plus at least one human approval on every PR.
- Unit tests before optimisations.
- User-visible changes behind short-lived flags, each classified **kill switch** or **ramp**. Nearly 200 flags; over half retired by sprint end.
- The brittle change (a static HTML composer painted before React) got its own guardrails: generated from the real component in jsdom with a never-diverge test, alignment compared at 14 viewports within 1px, a keystroke-through-handoff test, and field telemetry on every handoff with a thread opened on any nonzero shift.

## Steering

- **Ambition.** The agent's default is to ticket findings, hedge and pad estimates. "if you put it up right now I will get it merged and deployed. we have the power to do anything. please be braver." and "the targets are not the stopping point."
- **Taste.** Each thread has a named human owner who rules on user-perceptible trade-offs from before/after recordings, and can gavel a change out: "2ms per send is not worth the complexity of maintaining this build plugin" on a 900-line PR.
- **Direction.** Threads stay narrow, one benchmark or journey each. Humans sequence surfaces, merge overlapping threads and close diminishing-return ones.

## The 8ms budget

A side quest: a 120Hz frame budget (8.33ms) turned into a frame-by-frame audit of streaming. Memoisation removed O(message length) work per chunk, tokenisation moved to workers, tables revealed cell by cell. Main-thread blocking 750ms to 200ms; the rig became a nightly regression job.

## What is next, per the authors

p95, other journeys, very long conversations. Ratchets hold the gains.
