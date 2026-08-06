# Discovery Sweep — eval set

The regression suite for the `discovery-sweep` skill. Define the bar first, keep
the cases representative (including the negative and trap cases), change one
variable at a time, and judge **consistency across runs** — a fix that works on
one roll isn't a fix.

Run this whenever you change `SKILL.md`, `LEDGER.md`, `HOSTING.md`, or the model
the skill runs on. A host routine's own bindings changing does **not** need a
suite run; a change to what the method does with them always does.

---

## The bar (define "done" before touching the skill)

A run **passes** a case when, across ~3 runs, it *consistently*:

1. **Gates on depth.** Reads `Q` with the host's query, and either stops at the
   target with a quiet line, or writes down `min(deficit, cap)` as a number before
   filing anything.
2. **Carries provenance.** Every surviving candidate names a file and line, a
   decision-log entry, or a probe verdict. No candidate rests on an unnamed
   impression.
3. **Dedupes by theme.** Checks open, recently closed, and the ledger's Rejected,
   and drops a candidate that restates any of them under a different title.
4. **Splits on the envelope.** Every candidate marked agent or human against the
   host's capability table, and every human mark names the specific capability
   that blocks it.
5. **Gets edges and arming right.** Split direction read correctly; only frontier
   items carry the arm marker; chains filed blockers-first with edges referencing
   real numbers.
6. **Keeps the ledger honest.** Written before the report; every item in the right
   section (Deferred ≠ Blocked); proposal ids continue the sequence.
7. **Reports.** Queue depth, filed vs deferred vs blocked vs skipped, the last
   firing's date, and the disarm command whenever it filed — and the quiet line
   when nothing happened.

The **set** passes when every positive case passes and no trap case regresses.
**E5 and E7 are the arming regressions** — a set that fails either has a routine
that burns agent runs, whatever else it scores.

---

## Fixture

Cases need a tracker to read and a ledger to carry state. Use a **throwaway repo**
with its own issues — never a live one. A dry-run instruction is porous (the
`writing-great-recurring` suite watched one leak and create a real label), so the
isolation has to come from the repo, not from the prompt.

Seed per case:

- Open issues to set `Q` (label them with the fixture's arm marker).
- A ledger issue carrying `<!-- DISCOVERY-LEDGER:v1 -->`, with the sections the
  case needs populated.
- A host routine file supplying the bindings — copy `HOSTING.md`'s template and
  point it at the fixture repo, target 20 / cap 5 unless the case says otherwise.

Cases run as a fresh session (or fresh sub-agent) reading the host file and
following it. Where a case's expected outcome is "files nothing", let it run for
real; where it files, either let it file into the fixture and clean up after, or
have the run specify the exact `gh` calls and judge those.

---

## How to run the loop

1. **One variable at a time.** Change one thing, run the suite, compare to the
   bar, keep or revert.
2. **~3 runs per case.** Judge consistency, not one output.
3. **Score with the rubric.** Hand-score, or paste the case + the run + the rubric
   verbatim into a fresh model as an LLM-as-judge.
4. **Record results** in `RUNS.md`: one dated section per suite run — date, model,
   per-case matrix, one line per failure.
5. Running the full suite (10 cases × ~3 rolls) is a good use of a workflow: fan
   the cases out, judge each against the rubric, report the matrix.

### LLM-as-judge rubric (apply to every case)

Score each dimension pass/fail with a one-line reason:

- **D1 Gate** — `Q` read; stopped at target, or a numeric budget written down.
- **D2 Provenance** — every candidate names its source.
- **D3 Dedupe** — open + closed + Rejected checked; theme-level duplicates dropped.
- **D4 Envelope** — agent/human split correct; each human mark names its blocker.
- **D5 Edges & arming** — direction read correctly; only frontier items armed;
  chains ordered blockers-first.
- **D6 Ledger** — written before the report; correct sections; ids continue.
- **D7 Report** — depth, the four outcome classes distinguished, last firing date,
  disarm command; quiet line when nothing happened.

A case passes only if all seven hold on the majority of rolls. Dimensions a case
cannot exercise (D5 on a gated firing) are scored **n/a**, not pass.

---

## Cases

Each case: the fixture state, the expected outcome, and the case-specific checks
on top of D1–D7. **[trap]** cases exist to catch a specific failure — read the
trap before scoring.

### Core

### E1 — Gate trips  **[trap: sweeping anyway]**
**Fixture:** `Q` = 22 against target 20. Ledger has a clean previous firing.
**Expected:** stops at step 3. Nothing swept, nothing filed.
**Checks [trap]:** a ledger row recording `queue-at-target`, the quiet line, and
an exit. **Fail if it sweeps a single lane** — the whole point of backpressure is
that this firing costs under a minute. Fail if the ledger row is missing (a gated
firing still writes).

### E2 — Deficit with budget
**Fixture:** `Q` = 12 (deficit 8, cap 5). Eight plausible candidates reachable
across the lanes.
**Expected:** budget = 5, five filed, the rest Deferred with ids.
**Checks:** the budget is written as a number *before* filing; ranking is by blast
radius with the reasoning visible; Deferred entries carry enough to file next
firing without re-deriving. Fail if it files 8, or if the cap is raised "to close
the deficit faster".

### E3 — Nothing survives  **[trap: padding to budget]**
**Fixture:** `Q` = 4 (deficit 16, cap 5). Every discoverable candidate already
matches an open issue or a Rejected ledger entry.
**Expected:** **zero filed**, with the reason stated.
**Checks [trap]:** **fail if it files anything** — a manufactured candidate to
avoid an empty report is the exact failure the "ceiling, not a quota" line
defends. The quiet line must still name the depth and the unspent budget.

### E4 — Theme duplicate  **[trap: title-level dedupe]**
**Fixture:** `Q` = 15. An open issue reads "pause the allFills subscription on
hidden tabs"; the sweep will surface "reduce CU burn from always-on
subscriptions".
**Expected:** dropped as a duplicate.
**Checks [trap]:** **fail if both are filed** — no title token overlaps, and
title-level dedupe passes it through. The run must state the theme it matched on.

### E5 — Human-first edge  **[trap: arming blocked work]** ⭐
**Fixture:** `Q` = 8. A candidate to parse a new upstream response shape whose
actual shape is unrecorded — the host's envelope has no credential for the live
probe that would establish it.
**Expected:** split. The parser is filed **unarmed** with the edge declared (or
held in the ledger); the probe is proposed to the human.
**Checks [trap]:** **fail if the parser carries the arm marker.** The loop selects
on that marker alone, so arming it dispatches an agent to guess at a shape nobody
has seen — a full run and a branch to throw away. Also fail if the parser is filed
armed *with a note* saying it depends on the probe: a note is not an edge. A pass
puts a Blocked row in the ledger naming what closing the probe makes knowable.

### E6 — Agent-first edge  **[trap: over-applying E5]**
**Fixture:** `Q` = 8. A candidate whose derivation is self-contained and testable,
with a UI wiring step that needs eyes on it.
**Expected:** the derivation filed **armed** on the frontier; the wiring proposed,
named as out of scope in the filed body with its ledger id.
**Checks [trap]:** **fail if the derivation is withheld or filed unarmed** — this
is the symmetric error to E5, and a routine that learns "splits mean unarmed"
stops feeding the queue entirely. Also fail if filed whole and unsplit.

### E7 — Frontier advance  **[trap: ignoring the Blocked section]** ⭐
**Fixture:** `Q` = 19 against target 20. The ledger has two Blocked items; one's
blocker was closed since the last firing, the other's is still open.
**Expected:** step 2 arms the unblocked one (taking `Q` to 20), the gate then
trips, and the firing files nothing new.
**Checks [trap]:** **fail if it sweeps for fresh candidates while a Blocked item
sits ready** — advancing an edge is strictly cheaper than discovering, and the
skill calls this the cheapest good outcome. Fail if it re-files the item as a new
issue instead of arming the existing one. Fail if the still-blocked item is armed
or dropped. The report must name what closed and what it armed.

### Extended

### E8 — Wide refactor  **[trap: one item]**
**Fixture:** `Q` = 10. A rot-lane candidate to retype a shared symbol used in
~200 call sites across several packages.
**Expected:** an expand → migrate-batches → contract chain, filed blockers-first,
with only the expand armed.
**Checks [trap]:** **fail if filed as a single item** — no agent lands 200 call
sites green in one branch. Batches sized per package or directory; the contract
blocked by every batch; each batch's body stating it stays green because the old
form still exists.

### E9 — Stale decision  **[trap: re-reading an old comment]**
**Fixture:** the ledger has a comment `APPROVE: D-7`, and D-7 is already listed
under Filed with an issue number.
**Expected:** skipped silently; no second issue.
**Checks [trap]:** **fail if it files D-7 again** — this is the gate that stops 100
firings filing the same item 100 times, and it must judge by the ledger's state,
not the comment's age or position. A pass may mention the skip in the report but
never acts on it.

### E10 — False green  **[trap: reading a zero as clean]**
**Fixture:** a lane whose evidence command fails in a way that yields zero rather
than an error — a test runner missing a native binary so every suite fails to
load and the count reports 0, or a `grep` whose pattern matches nothing because
it's wrong.
**Expected:** the lane reported **skipped**.
**Checks [trap]:** **fail if the lane is reported empty or clean.** A pass either
eyeballs the matching names rather than the count, or notices the zero is
structurally impossible and says the lane could not be swept. The report must
distinguish skipped from empty in its own wording.

---

## Notes

- Keep the set sharp; a single passing run is **not** a pass.
- E1–E7 are the core regression set — run these on any change. E8–E10 are the
  extended set, worth a full run when the filing or lane logic moves.
- Every case writes to a tracker if it passes. Use a throwaway repo, and clean up
  what a roll files before the next roll — a leftover issue from roll `a` is a
  fixture change for roll `b`, which breaks the one-variable rule.
