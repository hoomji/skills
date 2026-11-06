# Audit: the hill-climbing loop in "How We Made claude.ai 3x Faster"

**Subject:** the per-thread loop and its steering, as captured in [the reference](../references/anthropic-claude-ai-faster.md).
**Output:** the improved flow that `skills/performance/` packages.
**Date:** 2026-09-24.

## What the flow gets right

- **Measurement first.** A slow moment becomes a deterministic lab number before anyone edits code. Everything downstream (the ratchet, the field check, the thread's scope) hangs off that number.
- **Lab and field are two measures with one job.** The lab is deterministic and cheap; the field is what users feel. The lab earns its place only by predicting the field.
- **The ratchet is the memory.** A win is not "shipped" until the ceiling moves, so the sprint's gains survive the sprint.
- **Narrow threads, named owner.** One journey or one benchmark per thread; a human rules on taste; the agent runs the loop.
- **Flags typed at birth.** Kill switch or ramp, decided before deploy, so the loss branch of the loop is one toggle.

## Findings

Each finding names the step it changes in the improved flow.

1. **No baseline step.** The loop starts at "identify", but the before/after table exists only because someone wrote the numbers down first. Without a written baseline a win is a claim. *Fix: step 0, baseline, with the percentile and the warm/cold state named.*
2. **Benchmark validation is a separate, later ask.** The "prove it predicts wall clock or we unship it" instruction came after the benches existed. A bench with no proven correlation is a target that can be climbed for nothing. *Fix: correlation proof is the benchmark step's completion criterion. A bench that cannot show one wall-clock win it predicted is unshipped there and then, and the unshipped list is kept so nobody rebuilds it.*
3. **The taste gate sits after the code.** The 900-line build plugin was gaveled after it was written. The owner's question ("is 2ms worth this complexity?") was answerable at proposal time from the estimate. *Fix: a decide step between measure and ship. The agent proposes estimated win, blast radius and complexity; the owner gavels; small wins with large diffs stop here.*
4. **The ratchet has no rules.** "Ratcheted ceilings downward" says nothing about tolerance, who may raise a ceiling, or what happens when a stale ceiling reds an unrelated change. A sibling repository (Gateway-LLM's no-unit-words gate) hit that exact failure: a checked-in number went stale under other authors' merges and every open PR inherited the red. *Fix: the ratchet compares against a checked-in ceiling with a stated tolerance; a fall lowers the ceiling in the same change; a rise fails; raising a ceiling is a named human decision recorded beside the number.*
5. **Flag retirement is unowned.** Half the flags were retired by sprint end, so half were not. *Fix: a flag is born with an owner and a retire-when condition (ramp reaches 100% and the field signal holds for N days; kill switch unused for N days). Continue-or-close includes retiring the thread's flags.*
6. **"Monitor field data" names no signal.** Without the named field signal the validate step cannot go red. *Fix: the benchmark step records which field measurement (journey, percentile) the lab number predicts; the judge step reads that one.*
7. **The tail is implicit.** p75 was the sprint's tail and p95 is "what's next". Which tail is being climbed changes which fixes matter (cold start versus steady state). *Fix: the baseline names the percentile; a thread that changes it is a new thread.*
8. **Ambition is a human nudge.** "Be braver" had to be said. *Fix: the skill states the positive default: propose the PR, not the ticket; a wait on a deploy is a request for a human to shortcut it; the target is a floor.*
9. **Bench sprawl.** "Anything can be hill climbed" is true and also how a repository grows fifty benches nobody reads. *Fix: the unshipped list from finding 2, and one bench per journey stage as the default shape.*

## The improved flow

```
0 Baseline   journeys, percentile, warm state, written numbers        (perf-baseline)
1 Identify   one slow moment, one journey, one owner
2 Measure    deterministic lab measure + its field signal + correlation proof, or unship
3 Decide     estimate vs complexity; the owner gavels
4 Ship       tests first, PRs sized for review, a typed flag with a retire-when
5 Judge      field signal moves: ratchet down (perf-ratchet). It does not: kill the flag, back to 2
6 Continue   next slow spot in the journey, or close: retire flags, record the ceiling
```

Steps 0 and 5 are their own skills because they fire on their own trigger words ("baseline", "ratchet") outside a running loop. Steps 1 to 6 are `hill-climbing`.
