# skills

Personal agent skills for Claude Code and Codex.

## Setup

```bash
git clone git@github.com:hoomji/skills.git ~/Documents/VS/Github/skills
cd ~/Documents/VS/Github/skills
chmod +x install.sh
./install.sh
```

This symlinks the skills in `skills/` into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex).

Also install the Matt Pocock skills plugin (see below) — the engineering skills aren't vendored in this repo anymore, so `install.sh` alone won't provide them.

## Layout

```
skills/        ← agent skills, grouped into category folders (see below); each
                 skill is its own directory with a SKILL.md, install.sh links
                 it by that directory's basename regardless of nesting depth
prompts/       ← reusable one-off prompts (plain markdown, no frontmatter)
teachings/     ← course material and learning records
```

Category folders under `skills/`:

| Folder | What it groups |
|---|---|
| `harness/` | The harness engineering system — assessing, bootstrapping, and maintaining a repo's agent-readiness. |
| `issue-triage/` | Keeping GitHub issues/PRDs triaged and the agent work queue stocked. |
| `review/` | PR review, stacking, and rescoping workflows. |
| `prompting/` | Sharpening prompts and standing up recurring routines. |
| `lateral-thinking/` | Ideation techniques (SCAMPER, six hats, provocation, etc.) for stress-testing ideas. |

## SKILL.md standard

Every skill lives in its own directory under `skills/` and contains a `SKILL.md`
whose frontmatter follows this shape:

```markdown
---
name: my-skill                      # required — kebab-case, matches the directory name
description: One line — what it does # required — what it does + when to trigger it
  and when to use it.
disable-model-invocation: true      # optional — set for user-invoked (slash-only) skills
argument-hint: "What to pass in"    # optional — for slash skills that take an argument
---

# My Skill

Skill body…
```

Field order is `name`, `description`, `disable-model-invocation`, `argument-hint`.
Only `name` and `description` are required — omit the optional fields when they
don't apply (a model-invocable skill has neither; a slash skill that takes no
argument has `disable-model-invocation` but no `argument-hint`).

## Adding a new skill

```
skills/
  my-new-skill/        ← new directory
    SKILL.md           ← required (see standard above)
    assets/            ← optional supporting files
    scripts/           ← optional scripts
```

Run `./install.sh` again after adding a new skill to link it.

## Skills

### harness/

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [harness](skills/harness/harness/SKILL.md) | Route repository harness assessment, setup, operation, and maintenance work. |
| [harness-assess](skills/harness/harness-assess/SKILL.md) | Produce a read-only, evidence-backed baseline of repository agent readiness. |
| [harness-bootstrap](skills/harness/harness-bootstrap/SKILL.md) | Preview, validate, and narrowly group a minimum viable harness change set. |
| [harness-deepen](skills/harness/harness-deepen/SKILL.md) | Improve one harness capability plane for a real tracer workflow. |
| [harness-encode-invariant](skills/harness/harness-encode-invariant/SKILL.md) | Turn a repeated correction into a mechanical repository check. |
| [harness-expose-runtime](skills/harness/harness-expose-runtime/SKILL.md) | Make one runtime surface inspectable and verifiable by agents. |
| [harness-plan-work](skills/harness/harness-plan-work/SKILL.md) | Create a repository-grounded execution plan with evidence gates. |
| [harness-product-spec](skills/harness/harness-product-spec/SKILL.md) | Create and maintain repository-local product intent and acceptance contracts. |
| [harness-design-doc](skills/harness/harness-design-doc/SKILL.md) | Create and maintain indexed, verified design documentation without replacing ADRs. |
| [harness-exec-plan](skills/harness/harness-exec-plan/SKILL.md) | Manage living ExecPlans from creation through evidence-backed completion. |
| [harness-reference](skills/harness/harness-reference/SKILL.md) | Curate durable external reference material in a repository knowledge store. |
| [harness-deliver-work](skills/harness/harness-deliver-work/SKILL.md) | Deliver a change through specialist implementation, verification, and review skills. |
| [harness-review-evidence](skills/harness/harness-review-evidence/SKILL.md) | Review a change against its spec, standards, and evidence bundle. |
| [harness-capture-learning](skills/harness/harness-capture-learning/SKILL.md) | Route repeated agent friction into the narrowest durable improvement. |
| [harness-garden](skills/harness/harness-garden/SKILL.md) | Find stale, conflicting, broken, or orphaned harness artifacts. |
| [harness-quality-report](skills/harness/harness-quality-report/SKILL.md) | Report harness capability levels, trends, regressions, and readiness. |

### issue-triage/

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [discovery-sweep](skills/issue-triage/discovery-sweep/SKILL.md) | Keep an agent work queue stocked — backpressure gate, lane sweep, agent-vs-human split, armed filing to a budget, ledger for memory. |
| [triaging-sandcastle-issues](skills/issue-triage/triaging-sandcastle-issues/SKILL.md) | Label unified-request GitHub issues ready-for-agent vs ready-for-human for the Sandcastle agent loop. |
| [salvage-sandcastle-run](skills/issue-triage/salvage-sandcastle-run/SKILL.md) | Close out a finished, killed, or stalled Sandcastle run — recover uncommitted work, reconcile rubber-stamped closures, get the branch green. |
| [has-pr-labelling](skills/issue-triage/has-pr-labelling/SKILL.md) | Label the issues an open PR already delivers, so a triage table separates picked-up work from untouched work. |
| [closing-completed-prds](skills/issue-triage/closing-completed-prds/SKILL.md) | Close the PRDs and SPECs whose implementation has actually landed, and label the ones still in flight. |

### review/

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [unblock-pr](skills/review/unblock-pr/SKILL.md) | Address every unresolved review thread on a PR and get its CI green. |
| [rescoping-prs](skills/review/rescoping-prs/SKILL.md) | Cut a PR that has grown past its issue back to the commits that deliver it, and give the rest their own PRs. |
| [stacking-open-prs](skills/review/stacking-open-prs/SKILL.md) | Chain a repo's open PRs into GitHub stacks wherever one genuinely depends on another. |

### prompting/

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [sharpen](skills/prompting/sharpen/SKILL.md) | Rewrite a rough prompt into a sharper one and recommend how to run it (model, effort, workflow). |
| [writing-great-recurring](skills/prompting/writing-great-recurring/SKILL.md) | Stand up a recurring routine end to end — pick the surface, write the recurring prompt, wire it, verify the first firing. |

### lateral-thinking/

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [lateral](skills/lateral-thinking/lateral/SKILL.md) | Toolkit router — diagnoses why you're stuck and picks the right technique below. |
| [analogy](skills/lateral-thinking/analogy/SKILL.md) | Forced Analogy — map the problem onto a structurally similar system from a distant domain and transfer its mechanisms back. |
| [concept-fan](skills/lateral-thinking/concept-fan/SKILL.md) | Concept Fan — climb to the concept the current solution serves, then fan out alternative concepts and implementations. |
| [inversion](skills/lateral-thinking/inversion/SKILL.md) | Assumption Inversion — flip each unquestioned assumption behind the current approach and see where the flip could be true. |
| [provocation](skills/lateral-thinking/provocation/SKILL.md) | Provocation (Po) — state something deliberately absurd about the problem and extract useful movement from it. |
| [random-stimulus](skills/lateral-thinking/random-stimulus/SKILL.md) | Random Stimulus — force-fit an unrelated object or phenomenon onto the problem to break familiar associations. |
| [scamper](skills/lateral-thinking/scamper/SKILL.md) | SCAMPER — run one existing idea through seven systematic transformations for disciplined variations. |
| [six-hats](skills/lateral-thinking/six-hats/SKILL.md) | Six Thinking Hats — examine one decision through sequential, non-blended perspectives (facts, feelings, risks, benefits, alternatives, synthesis). |
| [worst-idea](skills/lateral-thinking/worst-idea/SKILL.md) | Worst Possible Idea — design deliberately terrible solutions, then invert what makes them bad into strong features. |

## Matt Pocock skills

These used to be vendored copies of skills from [mattpocock/skills](https://github.com/mattpocock/skills),
committed under `skills/` alongside the personal skills above. As of 2026-08-06 they're
installed from the **official Claude Code plugin marketplace** instead — the plugin
tracks upstream releases directly, so there's no vendored snapshot to fall behind.

**Install (once per machine):**

```bash
claude plugin marketplace add mattpocock/skills
claude plugin install mattpocock-skills@mattpocock --scope user
```

`--scope user` matches how these used to be available globally via symlinks — every
project on the machine gets them, not just this repo. Run `claude plugin update
mattpocock-skills` to pick up new releases; a running session needs a restart to see
the update.

| Skill                       | Description                                                                                    |
|------------------------------|-------------------------------------------------------------------------------------------------|
| `mattpocock-skills:grill-with-docs` | A relentless interview to sharpen a plan or design, creating ADRs and a glossary as it goes. |
| `mattpocock-skills:grilling` | Grill the user relentlessly about a plan or design to stress-test it before building.          |
| `mattpocock-skills:domain-modeling` | Build and sharpen a project's domain model — terminology, ubiquitous language, and ADRs. |
| `mattpocock-skills:to-spec` | Turn the current conversation into a spec and publish it to the project issue tracker.          |
| `mattpocock-skills:to-tickets` | Break a plan, spec, or conversation into tracer-bullet tickets with blocking edges.           |
| `mattpocock-skills:triage`  | Move issues and external PRs through a state machine of triage roles into agent-ready briefs.   |
| `mattpocock-skills:implement` | Implement a piece of work based on a spec or set of tickets.                                   |
| `mattpocock-skills:tdd`     | Test-driven development — red-green-refactor for features and bugfixes.                         |
| `mattpocock-skills:code-review` | Review changes since a fixed point along two axes: repo Standards and originating Spec.    |
| `mattpocock-skills:wayfinder` | Plan a large chunk of work as a shared map of investigation tickets, resolved one at a time.   |
| `mattpocock-skills:resolving-merge-conflicts` | Resolve an in-progress git merge/rebase conflict.                             |
| `mattpocock-skills:setup-matt-pocock-skills` | Configure a repo for the engineering skills — issue tracker, triage labels, domain doc layout. |

The plugin also ships several skills this repo never vendored (`diagnosing-bugs`,
`improve-codebase-architecture`, `prototype`, `research`, `codebase-design`, `wizard`,
and the productivity bucket) — see the [upstream README](https://github.com/mattpocock/skills)
for the current full list.

**What changed by moving off vendored copies:**

- **Invocation names gained a plugin prefix.** Plugin-provided skills resolve as
  `mattpocock-skills:<skill-name>`, not the bare name (`triage`, `wayfinder`, …) the
  vendored copies used. Any doc, skill, or slash-command reference to one of these
  by bare name needs the prefix — [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md)
  and [`docs/agents/domain.md`](docs/agents/domain.md) in this repo have already been
  updated; check any other repo's `CLAUDE.md`/`AGENTS.md` that references them.
- **The skills no longer travel with a `git clone` of this repo.** They lived as
  committed files before; now they're a separate machine-level install. A teammate,
  CI box, or fresh machine that clones this repo does not get them until it also runs
  the `claude plugin install` command above.
- **Codex is unaffected but also unhelped.** Codex doesn't consume Claude Code
  plugins, so `~/.agents/skills/` keeps whatever copies of these skills were already
  there independently of this repo. This repo's `install.sh` was never the source for
  Codex's copies of these particular skills, so nothing broke there — but nothing here
  keeps Codex's copies in sync with upstream either.
