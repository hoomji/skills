---
name: discovery-sweep
description: The discovery-sweep method — keep an agent work queue stocked by gating on queue depth, sweeping lanes for candidates with named provenance, splitting agent-finishable from human, filing armed up to a budget, and carrying state in a ledger. Use when a discovery routine fires, when standing one up for a repo, or when another skill needs the sweep method.
---

# Discovery Sweep

A **discovery sweep** is a recurring routine that hunts a repo for unfiled work and
files what an agent can finish, so an agent loop selecting from a tracker never
starves. It is judged by its hundredth firing: still cheap, still bounded, still
saying something.

Two failures destroy its value, and every step below defends against one of them.

- **Slop** — an item that restates the backlog, chases a **dead end**, or lands
  outside the **envelope**. It costs a whole agent run to discover it was never
  real.
- **Silence** — a firing that finds nothing and says nothing is indistinguishable
  from a routine that died. Step 8 emits a line every time.

The sweep is **read-only** on the repo: its only durable writes are the tracker
items it files and the **ledger** it keeps. A dirty working tree is normal, not an
error — leave it exactly as found.

## Bindings

A host routine supplies the repo-specific facts; this skill owns the method. The
bindings a firing reads:

| Binding | Names |
|---|---|
| **Repo & tracker** | Path, remote, the CLI that is authenticated |
| **Arm marker** | The label or field the agent loop actually selects on |
| **Queue query** | The one command that returns the live agent queue depth |
| **Target & cap** | The queue depth to hold, and the most one firing may file |
| **Lanes** | Which lanes below apply, and where the evidence for each lives |
| **Envelope** | What that repo's sandbox can and cannot do |
| **Dead ends** | Where the repo records data sources known not to exist |
| **Ledger home** | A tracker item with a marker comment, or a state file on disk |

A firing whose host leaves a binding unnamed stops and names the missing one
rather than inventing a value. To author a host routine, read
[`HOSTING.md`](HOSTING.md).

## Blocking edges and the frontier

An item declares its **blocking edges** — the items that must close before it can
start. An item with none is on the **frontier**.

**Arm only the frontier.** The agent loop selects on the arm marker alone, so an
armed item whose blocker is still open dispatches an agent onto work it cannot
start: a full run spent discovering that, then a half-finished branch the loop
closes as complete anyway. Blocked agent items are filed with their edges declared
and **left unarmed**, and step 2 arms them once their blockers close.

File a chain in dependency order, blockers first, so each edge can reference a
real identifier. Use the tracker's native blocking or sub-issue link where it has
one; otherwise a `Blocked by` section naming the numbers.

Two shapes recur:

- **Tracer bullet.** A candidate too large for one fresh context window is sliced
  into narrow-but-complete paths through every layer it touches, each slice
  verifiable on its own and blocked by the one before it. Slicing by layer instead
  produces items that cannot be verified alone.
- **Expand–contract.** A **wide refactor** — one mechanical change whose **blast
  radius** fans across the codebase — cannot land green as a single slice. Sequence
  it: expand (add the new form beside the old, breaking nothing), then migrate call
  sites in batches sized by blast radius, each batch blocked by the expand and
  green on its own because the old form still exists, then contract (delete the old
  form) blocked by every batch. The rot lane is where these come from.

## Steps

### 1. Open the ledger

The **ledger** is the routine's whole memory — a firing wakes with no
recollection of the last one. Read it, including every human comment on it, per
the contract in [`LEDGER.md`](LEDGER.md).

Exactly one ledger exists. Absent on a first run, create it from the template.
Two ledgers are two memories, and the dedupe gate stops working the moment they
diverge — keep the older, retire the newer pointing at it, and say so in the
report.

_Complete when:_ one ledger is in hand, and the highest proposal id ever used is
known — new proposals continue that sequence.

### 2. Drain the ledger, before discovering anything new

Two things changed since the last firing, and both are cheaper than discovery.

**Advance the frontier.** Every item in the ledger's Blocked section whose
blockers have all closed is now on the frontier: add the arm marker, drop its
Blocked row, and flip its Filed row to armed. Anything still waiting keeps its row
and its edges. Newly armed items count toward the depth step 3 reads, so a firing
that advances the frontier may legitimately find the queue at target and file
nothing new — the cheapest good outcome this routine has.

**Drain the decisions.** Approvals arrive as comments on the ledger: file this
one, re-route that one to the agent, reject the third with a reason. Act on each,
then move it out of Awaiting review.

An approved item routed to a human is filed **without** the arm marker. That
marker is live dispatch — arming human work spends a whole sandbox run to
rediscover what the triage already knew, and the escape hatch is the host's
disarm command.

A decision naming an id already in Filed or Rejected is a re-read of an old
comment, not a new instruction — skip it silently. **This is the gate that stops
100 firings filing the same item 100 times.** Judge by the ledger's state, never
by the comment's age.

_Complete when:_ every Blocked entry has been re-checked against its blockers and
armed or left with its edges intact, and every undrained decision has produced
either a filed item or a Rejected entry, with the ledger reflecting both.

### 3. Backpressure — how much this firing may file

Run the host's queue query for the live depth `Q` against the target `T`.

- **`Q` ≥ `T` → stop here.** The queue is stocked; another item only deepens a
  backlog nobody is draining. Record the firing as `queue-at-target`, emit the
  quiet line from step 8, and exit. **Most firings should end here in under a
  minute — that backpressure is what makes a daily cadence cheap.**
- **`Q` < `T` → the deficit is `T - Q`, and this firing may file at most
  `min(deficit, cap)` items.**

Backpressure is also what makes autonomous arming safe: at the target the routine
stops filing, so a queue nobody drains cannot grow without bound. The cap holds
even when the deficit is wide — it bounds a bad sweep's **blast radius** to `cap`
bad items, and drains the deficit over several firings by design.

The cap is a ceiling, not an approval gate: every agent item inside the budget is
filed this firing without asking — armed where it sits on the frontier, unarmed
where an edge holds it.

_Complete when:_ `Q` is known, and either the gate tripped and this firing is
over, or a numeric file budget is written down.

### 4. Sweep the lanes

Read the repo's own context first — its agent instructions, roadmap, decision log,
and its record of **dead ends**. A candidate built on a data source that does not
exist is unbuildable however good it sounds, and the dead-end record is what
separates a real candidate from **slop**.

Sweep each bound lane. Breadth beats depth: aim for two to three times the file
budget in candidates and let step 6 cut them.

1. **Coverage** — shipped behaviour with nothing asserting it: a wired-in
   provider no spec names, a controller with no contract test, an error branch no
   test reaches. Name the behaviour at risk, not the file — some modules are
   legitimately not worth testing.
2. **Harness** — whether the checks a contributor and an agent actually run match
   the repo: unconditional skips with no tracking item, a guardrail that cannot
   fail (a threshold nothing trips, an assertion on a value the test itself
   computed), fixtures drifted from what the source records, an agent prompt that
   misdescribes the repo's own gates and so silently caps every run.
3. **Rot** — what would mislead a reader: dead exports nothing imports, logic
   duplicated across siblings, a doc asserting behaviour the code no longer has.
   Prefer misleading over merely untidy.
4. **Gaps** — a capability on one surface but not its analogue, a roadmap item
   never built, a documented-but-unimplemented endpoint. Highest slop rate of the
   four: these duplicate an existing spec most often, and are usually work the
   human wants to scope themselves.

Every surviving candidate carries **provenance** — a named file and line, a
decision-log entry, or a probe verdict — for believing it is real. "Coverage looks
low" has no provenance and is not a candidate.

Then dedupe hard, against open items, recently closed ones, and the ledger's
Rejected. **Judge by theme, not title:** two items about the same subject are one
candidate wearing two names. A duplicate that reaches the queue armed burns an
agent run on tracked work, which makes it the single most expensive outcome here.

Watch for the **false green**: a `grep | wc -l` returning 0 because the pattern
was wrong reads exactly like a clean repo. Eyeball the matching names, never the
count alone. A lane that could not be swept is recorded as **skipped**, which is a
different report line from **empty** — an empty lane is a fine and frequent
outcome.

_Complete when:_ every lane is marked swept, empty, or skipped; and every
surviving candidate states the behaviour it changes, carries provenance, and has
been checked against open, closed, and Rejected.

### 5. Split agent from human on the envelope

The host's **envelope** is the actual boundary — read it rather than guessing. A
candidate is agent-finishable only when **every** acceptance criterion can be met
inside it: commits on a branch, plus whatever API calls the sandbox's credentials
actually carry.

Criteria that typically fall outside: a merge, a CI verdict, a browser check, a
live credential the sandbox lacks, a screenshot, a file path the token cannot
push. A criterion needing a CI verdict is a human criterion even when CI is
perfectly healthy.

Split a mixed candidate rather than filing it whole — the pure-derivation half
becomes an agent item, the half needing eyes becomes a proposal. Filing the
unsplit version means the agent finishes half and the loop closes it as complete
anyway.

**A split leaves an edge, and its direction decides whether the agent half may be
armed.** Two directions, and reading them backwards is how this step produces
slop:

- **Agent first.** The derivation is self-contained and the human work consumes it
  — build and test the logic, then wire it up and look at it. The agent half is on
  the **frontier**: file it armed, with the human half named as out of scope and
  carrying its ledger id.
- **Human first.** The human work establishes something the agent cannot see — the
  live shape of an upstream, a credentialed probe, a CI verdict, a merge. The agent
  half is **blocked**: file it with the edge declared and unarmed, or hold it in the
  ledger until the human half exists to point at. Arming it now buys a run that
  guesses at the shape and a branch that has to be thrown away.

_Complete when:_ every candidate is marked agent or human; every mixed one is
split with its edge direction named; and every human mark names the specific
capability that blocks it.

### 6. File the agent half — up to budget, without asking

Spend the ledger's **Deferred** entries before this sweep's fresh candidates: a
deferred candidate is already researched and already deduped. Re-check it against
the current tree first — code that moved under it sends it to Rejected as
superseded.

Rank by **blast radius**: behaviour that could silently return wrong data beats a
formatting nit. Break ties on cost, cheapest first.

Then size and sequence what survived. A candidate too large for one fresh context
window becomes **tracer bullet** slices, and a **wide refactor** becomes an
**expand–contract** chain — both per the shapes above. File any chain in
dependency order so each edge references a real number, and **arm only its
frontier**; the rest are filed with edges declared and unarmed, and recorded in
the ledger's Blocked section for step 2 to advance.

The budget counts every item filed, armed or not — it bounds slop, and an unarmed
bad item is still a bad item. It is a ceiling, not a quota: filing two when five
were allowed is a normal outcome, and so is filing zero with the full budget
unspent. The target is `T` items an agent can *finish*.

The implementer reads the item body and nothing else, so each carries:

- **Title** — `<area>: <the change>`, in the repo's existing style.
- **Why** — one paragraph naming its provenance.
- **Acceptance criteria** — checkboxes, each reachable inside the envelope.
- **Blocked by** — each blocking item by number, or that it can start immediately.
  A blocked item also says what closing the blocker will make knowable, so the
  implementer picking it up later doesn't re-derive it.
- **Out of scope** — the human half explicitly, with its ledger id, if step 5
  split one.
- **Verification** — the exact commands the sandbox can run.
- **Footer** — the host's marker, which is how a later firing recognises its own
  work.

Labels: the host's type label, plus the arm marker on frontier items only. Create
from a body file, not an inline string — a body containing backticks is how this
step corrupts itself.

Agent candidates the budget will not fit go to **Deferred** with an id and enough
of a note to file them next firing without re-deriving them. They need no
approval — the budget is holding them, not a decision — and step 8 reports how
many are waiting, so a cap that is throttling real work stays visible.

_Complete when:_ each filed item exists and carries the footer; every armed item
is on the frontier and every non-frontier item is unarmed with its edges declared;
and each appears under Filed or Blocked in the ledger with its number — or nothing
was filed and step 8 says why.

### 7. Propose the human half

Each human candidate becomes an Awaiting review entry with a fresh id, and reaches
the human in **one** comment on the ledger that @-mentions them: what it changes,
why it is worth doing, the capability the agent lacks, and the reply syntax from
[`LEDGER.md`](LEDGER.md).

A proposal that **blocks** agent work is named as such, with the items waiting on
it — those are the ones where a decision unblocks a queue rather than adding to
it, and they lead the comment.

These stay in the ledger. No item is opened for them and no arm marker touches
them, and an approval counts only when it appears as a comment on the ledger —
that comment is the only record surviving to the next firing.

A comment goes out only when this firing has a **new** candidate; an existing
proposal gets its sweep count bumped and nothing else. Most firings post no
comment at all, which is correct — a daily @-mention repeating yesterday's two
items is how a routine gets muted. A proposal unanswered after ten firings moves
to Rejected as `no decision after 10 firings` and is named in the report; roughly
a fortnight at a daily cadence, long enough that a busy week doesn't discard a
real proposal.

_Complete when:_ every human candidate has an id under Awaiting review and
appears in at most one @-mentioning comment, and no tracker item exists for any of
them.

### 8. Write the ledger, then report

Rewrite the ledger body first — current sections plus a `Last swept: <date>` line.
A firing that dies mid-sweep looks exactly like a quiet day unless the ledger
records where it stopped, so the ledger is written before the report, always,
including on a firing that tripped the gate at step 3. The routine owns the body;
the human writes only in comments, which stay untouched.

Then the report. Short — most days one line:

- The gate line, always: `queue at Q/T`.
- One line per filed item: number, title, lane, and armed or blocked-by-what.
- Every edge advanced this firing — what closed, and what it armed.
- Every proposal made and every decision drained, by id.
- How many agent candidates are Deferred behind the cap, and how many are Blocked
  behind an edge. A queue starving with items Blocked on one unanswered proposal is
  the signal that most needs to reach the human.
- Each lane that was skipped, named as skipped.
- The last firing's date from the ledger, so a routine that has stopped running is
  visible in its own report.
- The host's disarm command, whenever this firing filed something.

When nothing happened it still gets its **quiet line**:

`<routine> <date>: queue at Q/T, swept <lanes>, N candidates, 0 filed (<why>); M awaiting review — last firing <date>.`

_Complete when:_ the ledger on disk contains this firing's entry, and the report
gives the queue depth, distinguishes filed from deferred from skipped, names the
last firing's date, and carries the disarm command if it filed.

## When a step fails

A failure this skill does not name — an unauthenticated CLI, a network error, a
crash — stops the firing there and is reported as that error. Re-running it or
filing partway leaves a half-filed item with no ledger entry, invisible to the
next firing's dedupe gate.
