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

**Escalate — breadth across many agents.** After model and effort, decide whether one
agent is enough or the task should escalate from depth (one agent thinking hard) to
**breadth** (many agents plus verification a single context can't give itself). Escalate
only when the task needs one of:

- *Comprehensiveness* — decompose it and cover the parts in parallel.
- *Confidence* — independent or adversarial verification before committing.
- *Scale* — work bigger than one context window: migrations, audits, broad sweeps.

**Default to no agents.** Sequential steps, a dependency chain, same-file edits, and
anything a single session can hold are all one-agent work — the briefing cost of handing
context to a fresh agent is real, and paying it for a job the current session already
understands is a loss. Say plainly that a single agent at the recommended effort
suffices, and stop there. Coordination overhead is the cost that escalation has to
outweigh, so name a shape below only when one of the three needs above actually applies.

When it does, pick the shape by how the parallel workers relate to each other and to the
user:

- **Subagents** — the pieces are independent and only the *results* matter: parallel
  search, research, per-item review or edits, or work whose intermediate reading would
  drown the lead's context. Workers report to the lead and never talk to each other. Point
  the user at the `subagent-prompt` skill to write the dispatch prompt.
- **A team** — the workers must **argue with each other** (competing hypotheses, multi-lens
  review that should cross-examine) or the user wants to message, redirect, or halt one
  individually. Costlier than subagents and experimental; point the user at the
  `team-prompt` skill.
- **A workflow (ultracode)** — the fan-out should be *deterministic and large*: fixed
  stages, loops, adversarial verification passes, dozens of agents over a migration or
  audit. Opt-in and expensive, so recommend it only when the scale justifies the spend.
  Tell the user how to trigger it: include the keyword **ultracode**, or ask for a
  workflow / multi-agent orchestration.

Both prompt-writing skills are user-invoked, so name the skill for the user to type
rather than promising to run it.
