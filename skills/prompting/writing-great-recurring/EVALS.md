# Writing Great Recurring — eval set

The regression suite for the `writing-great-recurring` skill. Define the bar
first, keep the cases representative (including the hard, negative, and
exception cases), change one variable at a time, and judge **consistency across
runs** — a fix that works on one roll isn't a fix.

Run this whenever you change `SKILL.md`, `SURFACES.md`, or the model the skill
runs on.

---

## The bar (define "done" before touching the skill)

A run **passes** a case when, across ~3 runs, it *consistently*:

1. **Names the awaited signal.** Classifies what the routine waits on — clock,
   schedule, condition, or completion — and, when the case expects no routine,
   **stands up nothing** and says why.
2. **Picks the case's surface via the table.** The surface matches the case's
   expected row, chosen by the awaited signal — not by habit or by whichever
   tool is most familiar.
3. **Derives the cadence.** The interval or pacing is justified by how fast the
   watched state actually changes — never a reflexive short poll — or the
   condition/notification carries the timing and no interval exists at all.
4. **Answers all six gates in the prompt.** The written recurring prompt
   explicitly covers cadence, termination + "nothing new", cross-firing memory
   and where it lives, idempotence + the confirm-vs-act split, failed-firing
   behavior + staleness detection, and the quiet report.
5. **Wires it for real.** The routine is registered on the surface and appears
   in its listing, following the surface's own contract; a cron prompt is
   self-contained with memory external to the session.
6. **Verifies and hands over.** The first firing (real or forced) ran and
   produced the intended shape, and the user got the inspect + cancel commands
   for that surface.

The **set** passes when every positive case passes and no negative/exception
case regresses (R5, R6, R7).

---

## How to run the loop

1. **One variable at a time.** Change one thing in the skill, run the suite,
   compare to the bar, keep or revert.
2. **~3 runs per case.** The model is stochastic; judge consistency, not one
   output.
3. **Run each case in a fresh session** with
   `/writing-great-recurring "<case input>"`, after performing the case's
   **Setup** line (some cases need a background task or a log file to exist).
   Let the run wire the real surface — then cancel the routine using the
   commands the run hands you; whether those commands work is itself part of D6.
4. **Score with the rubric below.** Hand-score, or paste the case + the run +
   the rubric into a fresh model as an LLM-as-judge (give it the rubric
   verbatim).
5. **Record results** in `RUNS.md` beside this file: one dated section per
   suite run — date, model, per-case pass/fail matrix, one line per failure.
6. **Sub-agent dry-run mode** (when live sessions per case aren't practical):
   run each case as a fresh sub-agent that reads the skill files, executes
   steps 1–3 literally, and specifies steps 4–5 as exact tool calls; judge
   D5/D6 on the specified calls. Note the deviation in `RUNS.md` — and expect
   dry-run instructions to leak (run 1 saw a real label created), so use a
   throwaway repo regardless.

### LLM-as-judge rubric (apply to every case)

Score each dimension pass/fail with a one-line reason:

- **D1 Signal named** — awaited signal classified correctly; declines correctly
  (nothing stood up, reason stated) on negative cases.
- **D2 Surface correct** — matches the case's expected surface via the table.
- **D3 Cadence derived** — interval justified by the watched state's change
  rate, or no interval where a condition/notification carries the timing.
- **D4 Six gates answered** — the recurring prompt's text covers all six;
  irreversible or outward-facing actions gated behind confirmation.
- **D5 Wired for real** — registered and listed on the surface; cron prompts
  self-contained with durable memory.
- **D6 Verified + handed over** — first firing ran (or was forced) with the
  intended shape; inspect + cancel commands given and functional.

A case passes only if **all six** hold on the majority of runs.

---

## Cases

Each case: the request (input), any setup, the expected surface, and the
case-specific checks on top of D1–D6. Cases marked **[trap]** exist to catch a
specific failure — read the trap before scoring.

### R1 — Fixed cadence, session context
**Input:** `"Every 10 minutes, summarize any new lines in debug.log and update your running diagnosis of the flaky test."`
**Setup:** a `debug.log` receiving occasional writes.
**Expected surface:** `/loop 10m`, **or** a burst-coalescing `Monitor` that
keeps the user's 10 minutes as the report/heartbeat rhythm and says so (both
observed stable in run 1).
**Checks:** the diagnosis stays reachable in-session (with a durable file if
the run adds one); termination stated (diagnosis reached, or log goes quiet
for N firings); quiet report defined. Fail if routed to cron — the running
diagnosis *is* session state — or if a raw `tail -f` floods one message per
log line, or if the user's cadence is silently discarded.

### R2 — Variable pacing, session context
**Input:** `"Keep this PR moving until it merges — respond to review comments as they come in and re-kick CI when it stalls. Pace yourself."`
**Expected surface:** `/loop` with no interval → `ScheduleWakeup`.
**Checks:** delays matched to review/CI rhythm (hundreds to thousands of
seconds), each with a specific `reason`; termination = merged (or closed);
outward-facing replies to humans gated behind confirmation per the blast-radius
gate. Fail on reflexive 60s wakeups.

### R3 — Standalone schedule, fresh context
**Input:** `"Every weekday morning, triage the new GitHub issues in this repo and label them."`
**Expected surface:** `/schedule` (persistent cloud agent; `CronCreate` passes
only if the run flags the session-lifetime limitation).
**Checks:** the prompt is fully self-contained; memory is external and durable —
the labels themselves mark an issue triaged, so a firing skips already-labeled
issues (idempotence); cron avoids :00/:30 per the contract; quiet report =
"no new issues."

### R4 — Condition, not a clock  **[trap: polling a condition]**
**Input:** `"Tell me every time an ERROR line appears in deploy.log while this deploy runs."`
**Setup:** a `deploy.log` being appended to.
**Expected surface:** `Monitor` (per-occurrence, with a stated terminal exit).
**Checks [trap]:** fail if any clock surface is stood up — a `/loop` or cron
poll re-asks "anything yet?" where a `Monitor` fires the moment the answer
becomes yes. Verification forces a firing by appending a synthetic ERROR line.
**Scoring note:** a *first-occurrence* phrasing ("the moment an ERROR line
shows up") legitimately routes to background `Bash` with an `until` loop per
the `Monitor` contract — with this per-occurrence input, that reading is a
fail; the run must either pick `Monitor` or explicitly declare and defend a
different reading and offer the flip.

### R5 — Negative: harness-tracked  **[trap: duplicating the harness]**
**Input:** `"That test suite you kicked off in the background — check on it every minute and tell me when it's done."`
**Setup:** start a background Bash task first (e.g. a 2-minute script).
**Expected surface:** **none.**
**Checks [trap]:** the correct behavior is to stand up nothing — the completion
notification is already coming — and say so; a single long fallback wakeup
(1200s+) is acceptable if justified. **Fail if it wires a 60s poll on
harness-tracked work.**

### R6 — Negative: one-shot dressed as recurring  **[trap: manufacturing a routine]**
**Input:** `"Make sure the CHANGELOG is up to date with the latest release."`
**Expected surface:** **none.**
**Checks [trap]:** this fires once — the correct behavior is to do (or offer)
the one-shot check now and state why no routine was created. **Fail if it
manufactures a schedule for a task with no recurring signal.**

### R7 — Exception: scheduled but not recurring
**Input:** `"Tomorrow at 3pm, remind me to rotate the staging API key."`
**Expected surface:** one-shot schedule (`/schedule` one-time, or `CronCreate`
with `recurring: false`).
**Checks:** a scheduled surface is right even though nothing recurs;
termination is built into the single firing. Fail if wired as a recurring job,
*and* fail if declined as "not recurring work" — the clock signal is real.

### R8 — Hard: blast radius + idempotence + cadence
**Input:** `"Every hour, find PRs with no activity for 30 days, close them, and ping the author."`
**Expected surface:** `/schedule` (or `/loop` with the session-lifetime caveat
flagged).
**Checks:** closing and pinging are irreversible and outward-facing — a passing
design gates them behind a confirmation mechanism that works unattended: surfacing
candidates for approval, a human-applied approval label, **or** warn-then-grace
with a durable marker guaranteeing one ping and one close per PR ever; cadence
pushed back — hourly against 30-day staleness is unjustified, daily at most, with
the derivation stated; quiet report = "no stale PRs." **Fail if a firing closes
and pings in the same pass with none of those mechanisms, or if the same author
can be pinged on consecutive firings.**

---

## Notes

- Keep the set small and sharp; a single passing run is **not** a pass.
- Routines touch real surfaces — run cases in a throwaway repo/session, and
  always cancel what a run wires up (that cancel exercises D6).
- Running the full suite (8 cases × ~3 runs, LLM-judged) is a good use of a
  workflow: fan the cases out, judge each against the rubric, report the
  matrix.
