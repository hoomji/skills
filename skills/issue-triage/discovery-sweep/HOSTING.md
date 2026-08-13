# Hosting a discovery sweep — reference

How to stand a discovery routine up on this method. Reference for
[`SKILL.md`](SKILL.md), which owns the steps; a host routine holds only the
repo-specific facts and points here.

Pick and wire the recurring surface with `writing-great-recurring` — this file
covers what the prompt on that surface must say.

## What belongs where

The host prompt is short by design. Anything that would read the same for a second
repo belongs in `SKILL.md` and is a **single source of truth** violation in the
host: the gate arithmetic, the ledger contract, the dedupe rule, the report shape.
Two host routines that both restate the gate drift apart the first time the target
changes.

The host names its bindings, then hands over:

```markdown
Read the `discovery-sweep` skill and follow its steps with these bindings.
```

## The bindings

| Binding | How to fix it | Worked: `unified-request` | Worked: `hyperscope` |
|---|---|---|---|
| **Repo & tracker** | Absolute path, remote, and which CLI is authenticated as whom | `~/…/unified-request`, `Uniblock-dev/unified-request`, `gh` as `hoomji` | `~/…/hyperscope`, `Uniblock-dev/hyperscope`, `gh` as `hoomji` |
| **Arm marker** | Read the agent loop's own selector and copy it exactly | `Sandcastle` label (`.sandcastle/plan-prompt.md` gates on this alone) | same |
| **Queue query** | The command that returns the live depth, nothing broader | `gh issue list --state open --label Sandcastle --limit 200 --json number --jq 'length'` | same |
| **Target & cap** | See below | 20 / 5 | 20 / 5 |
| **Lanes** | Which of coverage, harness, rot, gaps apply, and the file that holds each one's evidence | `test/coverage-thresholds.json`, `test/README.md`, `docs/` | `src/lib/*.test.ts`, `.github/workflows/ci.yml`, `plan.md`, `docs/probes/` |
| **Envelope** | The sandbox's real capability table, verified not guessed | `triaging-sandcastle-issues` | that skill's *method*, plus a hyperscope table — no `UNIBLOCK_API_KEY`, so no live call |
| **Dead ends** | Where the repo records data sources known not to exist | — | `CONTEXT.md` → Data-source truths |
| **Edge shapes** | The dependency directions this repo produces, so step 5 reads them the right way round | cassette recording → the spec that consumes it; a merge → anything building on it | a live probe → the parser for that shape; a `src/lib` derivation → the page that renders it |
| **Blocking link** | Whether the tracker has a native blocking relationship, or edges live in a `Blocked by` section | GitHub sub-issues, else `Blocked by` | same |
| **Ledger home** | A tracker item with a marker, or a state file | state file (`ledger.json`) | ledger issue, `<!-- DISCOVERY-LEDGER:v1 -->` |
| **Footer marker** | The string a later firing recognises its own work by | `<!-- filed-by-daily-work-discovery -->` | `Discovered by: discovery sweep <date>, ledger #<n> (D-<id>)` |
| **Disarm command** | The one-liner that pulls an item back out of the queue | `gh issue edit <n> --remove-label Sandcastle` | same |
| **House patterns** | Precedents an agent should follow when a candidate needs a seam | — | injectable class + singleton on top (`PinnedWalletsStore`) |
| **Verification commands** | Exactly what the sandbox can run, so acceptance criteria stay reachable | `yarn test:unit`, `yarn lint:check`, `yarn typecheck:build`, `yarn format:check` | `npm test`, `npm run typecheck`, `npx prettier --check` |

An **envelope** copied from another repo is the most expensive binding to get
wrong: the method transfers, the capability table does not. Where the repo's own
docs say honest verification means watching something load live data, and the
sandbox has no credential for that, every candidate touching it is human work.

## Setting target and cap

**Target** is the queue depth the agent loop needs to stay fed between firings —
enough that a manual run always finds work, not so much that it becomes a backlog
nobody reads. It is the human's number; ask for it rather than deriving one.

**Cap** is the blast radius of a single bad sweep. Set it so an empty queue refills
over several firings: `cap ≈ target / 4` at a daily cadence fills in about four
days. A cap raised to close a deficit faster converts one bad sweep into a full
queue of slop, which is the failure the cap exists to bound.

## Host template

```markdown
---
name: <repo>-discovery
description: <cadence> refill of <repo>'s agent queue to <target> — sweeps for
  <lanes>, files the agent-finishable ones armed, proposes the human ones in the
  ledger.
---

Read the `discovery-sweep` skill and follow its steps. The sweep is read-only on
this repo; a dirty working tree is normal and stays as found.

## Bindings

- **Repo & tracker:** …
- **Arm marker:** …
- **Queue query:** `…`
- **Target / cap:** … / …
- **Lanes:** … — evidence lives in …
- **Envelope:** … (read <skill or table>; verified <date>)
- **Edge shapes:** … blocks …; … blocks …
- **Blocking link:** …
- **Dead ends:** …
- **Ledger home:** …
- **Footer marker:** `…`
- **Disarm:** `…`
- **Verification commands:** `…`

## Repo notes

<Only what a firing cannot read off the repo itself: which suites are slow or
flaky, which lanes are usually empty here, a precedent an agent should follow.>
```
