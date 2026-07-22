# Running it — reference

The decision rules for step 3, in the order step 3 applies them: model, then effort,
then the escalate-or-not call.

For current model IDs, pricing, effort levels, and behavioral specifics, consult the
`/claude-api` skill — it is the source of truth and stays current. The decision rules
here are stable.

**Model.** Default to the **daily driver** (Opus 4.8): cheaper, faster, and it handles
almost everything. Reach for the **heavyweight** (Fable 5) only when the task is hard,
long-horizon, and well-specified enough to run autonomously, and its higher cost and
minutes-long turns are acceptable. Stay on the daily driver for anything routine,
latency-sensitive, interactive, or cyber/bio-adjacent — the heavyweight refuses those.

**Effort — depth within one agent.** Effort dials how hard a single agent thinks; it
spends thinking tokens and turn count together. Reason *to* a level rather than
asserting one:

- *Start point.* Default `high`; `xhigh` for coding and agentic work; `max` only when
  correctness outweighs cost, never reflexively; `low`/`medium` for routine, subagent,
  or simple tasks. On the heavyweight, `low` already performs very well — often beating
  older models even at their highest effort — so start lower than instinct; if a task
  completes correctly but slowly, turn effort *down*.
- *Sweep when unclear.* The cost/quality curve is not monotonic — higher effort up
  front often *reduces* total turns and cost on agentic work, while for some tasks a
  lower level is just as good and faster. When the right level isn't obvious, name a
  **sweep** of two adjacent candidates to run on the actual task and compare.
- *Define done.* A high-effort run needs a defined 'done' or full task spec up front,
  or the deliberation wanders and you pay for thinking you can't use. If the rewrite
  doesn't pin the win condition, lower the effort or tighten the spec first.
- *Latency is a separate dial.* Effort affects latency only indirectly, through turn
  count; the dedicated latency control is fast mode (output tokens/sec). Don't lower
  effort to chase speed — reach for fast mode instead.

**Escalate to a workflow (ultracode) — breadth across many agents.** After model and
effort, decide whether one agent is enough or the task should escalate from depth (one
agent thinking hard) to **breadth** (many independent agents plus verification a single
context can't give itself). Escalate when the task needs one of:

- *Comprehensiveness* — decompose it and cover the parts in parallel.
- *Confidence* — independent or adversarial verification before committing.
- *Scale* — work bigger than one context window: migrations, audits, broad sweeps.

A workflow is opt-in and costly (dozens of agents, many tokens), so recommend it only
when the scale justifies the spend — never for trivial or quick work. When you do,
tell the user how to trigger it: include the keyword **ultracode**, or ask for a
workflow / multi-agent orchestration. When none of the three needs apply, say plainly
that a single agent at the recommended effort suffices.
