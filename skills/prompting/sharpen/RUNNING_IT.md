# Running it — reference

The decision rules for step 3, in the order step 3 applies them: model, then effort,
then the escalate-or-not call.

For current model IDs, pricing, effort levels, and behavioral specifics, consult the
`/claude-api` skill — it is the source of truth and stays current. The decision rules
here are stable.

**Model.** Default to the **daily driver** (Opus 5): cheaper, faster, and it handles
almost everything. Reach for the **heavyweight** (Fable 5) when the task is hard,
long-horizon, and well-specified enough to run autonomously, and its higher cost and
minutes-long turns are acceptable. A large unattended batch job — e.g. "migrate all N X
end-to-end with passing tests," work scoped to run over a weekend — is the **signature
heavyweight case**: name the heavyweight as *the* recommendation, not a fallback, a
reserve, or a daily-driver pilot. Stay on the daily driver for anything routine,
latency-sensitive, interactive, or cyber/bio-adjacent — the heavyweight refuses those.

**Effort — depth within one agent.** Effort dials how hard a single agent thinks; it
spends thinking tokens and turn count together. Reason *to* a level rather than
asserting one:

- *Start point.* **`high` is the default, and the floor for real work.** Move off the
  floor deliberately, by the *kind* of task rather than its apparent size:
  - `xhigh` for **demanding** coding and agentic work — long-horizon, multi-file, or
    tool-heavy runs, and the coordination on a large autonomous job.
  - `high` — the floor — for bounded, well-specified **coding**, for **diagnostic,
    analytic, or decision** work, for **writing**, and for any task whose **win condition
    can't be pinned** up front. A short diff is still coding: a change looking small is
    not a reason to drop below the floor.
  - `low`/`medium` for **subagent tasks and non-code routine** — classification, lookups,
    high-volume mechanical passes. These are the primary cost and latency control, but a
    code change never qualifies on size alone; go below the floor on evidence that quality
    holds there, not on the diff looking short.
  - `max` only when the task justifies unconstrained spend, never reflexively.

  Recommend the effort the *task* needs, independent of the effort this session happens to
  be running at — never lower your pick just to match the current session. An effort level
  carried over from an older model is a stale default, not a starting point: both models
  hold quality further down the ladder than their predecessors did. If a task completes
  correctly but slowly, turn effort *down*.
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
