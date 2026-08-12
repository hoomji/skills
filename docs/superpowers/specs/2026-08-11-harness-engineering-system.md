# Harness Engineering System

**Date:** 2026-08-11

**Status:** Milestones 1–2 complete; Milestone 3 ready for repository trials

**Primary inspiration:** [OpenAI, “Harness engineering: leveraging Codex in an agent-first world”](https://openai.com/index/harness-engineering/)
**Target:** A reusable specification plus a family of skills for establishing, operating, and improving an agent-ready software repository

## Executive summary

This project turns “harness engineering” from an article and a collection of good
ideas into an installable, inspectable operating system for agent-assisted software
development.

The product is not one large prompt, one `AGENTS.md`, or a claim that agents should
write all code. It is a **repository control system** that makes intent, knowledge,
execution, evidence, constraints, and feedback directly legible and actionable to
agents. Humans choose goals, risk tolerance, and tradeoffs. Agents perform bounded
work, produce evidence, and improve the harness when repeated friction reveals a
missing capability.

The first release should deliver three things:

1. A normative specification describing the concepts, artifact contracts, maturity
   levels, safety model, and success measures.
2. Setup skills that assess a repository, propose an adoption plan, and install the
   minimum viable harness incrementally.
3. Day-to-day skills that use the harness to plan, implement, verify, review, capture
   learning, and perform recurring maintenance.

The central design rule is: **store judgment at the most enforceable useful layer**.
A one-off constraint belongs in a prompt; durable navigation in `AGENTS.md`; detailed
knowledge in versioned docs; a repeatable method in a skill; an invariant in a lint,
test, hook, or CI check; live external state behind a tool; and stable recurring work
in an automation.

## Problem

Coding agents can generate code faster than humans can specify, inspect, and validate
it. In an ordinary repository, this moves the bottleneck rather than removing it:

- important context is scattered across chat, external documents, and people;
- setup and verification steps are incomplete or not executable by an agent;
- architecture and “taste” exist as prose that cannot fail a build;
- runtime behavior, UI state, logs, metrics, and traces are invisible to the agent;
- concurrent work collides in shared environments;
- review feedback fixes one change but does not improve future runs;
- agent output amplifies inconsistent patterns already present in the repository;
- unattended autonomy is introduced without an explicit risk or escalation model.

OpenAI’s article reports that its team addressed these problems by shifting human
work toward environment design, intent specification, and feedback loops. It describes
a short `AGENTS.md` as a map into a structured repository knowledge base, mechanically
enforced architecture, worktree-local application and observability environments,
agent-to-agent review, execution plans, and recurring “garbage collection.” The
article also reports an experimental “no manually-written code” constraint and a
high-throughput merge philosophy. Those two operating choices are evidence from one
context, not requirements of this system.

## Goal

Create a progressive, technology-neutral method for making a software repository:

- understandable from a cold start;
- safely operable by an agent;
- explicit about product and architectural intent;
- self-verifying wherever a claim can be checked mechanically;
- observable at build time and runtime;
- isolated enough for parallel and background work;
- able to turn repeated human corrections into compounding system improvements;
- measurable, auditable, and reversible as autonomy increases.

## Non-goals

- Mandating that all code be agent-generated.
- Eliminating human review or judgment.
- Replacing product management, architecture, or engineering discipline with prompts.
- Requiring OpenAI’s internal stack, repository shape, scale, or merge policy.
- Generating a giant `AGENTS.md` or duplicating every document into agent instructions.
- Installing every possible tool, connector, hook, or automation on day one.
- Promising end-to-end autonomy before the repository can produce trustworthy evidence.
- Defining one universal architecture or style guide for all codebases.

## Concept Fan: widening the initial idea

### Starting solution

Write a comprehensive harness-engineering spec, then create skills that set it up and
support daily use.

### First climb

**What is this a way of doing?** Operationalizing agent-first engineering in a real
repository.

Sibling concepts:

1. **Declarative repository standard** — define required capabilities and artifact
   contracts, then generate or repair them.
2. **Maturity and assessment system** — measure current agent readiness and advance one
   bottleneck at a time.
3. **Repository control plane** — encode policy, evidence, observability, isolation,
   and escalation around agent work.
4. **Prompt library with setup instructions** — the original idea with less structure;
   it does not create a materially different system and is **pruned**.

### Second climb

**What is operationalizing agent-first engineering a way of doing?** Turning scarce
human judgment into reusable, executable, compounding organizational capability.

Sibling concepts:

1. **Capability flywheel** — every repeated failure is classified as missing knowledge,
   tooling, feedback, policy, or judgment and improves that layer.
2. **Repository digital twin** — the repository exposes enough product, architecture,
   runtime, and operational truth for an agent to reason about the system directly.
3. **Autonomy budget** — grant autonomy by demonstrated evidence and reversible risk,
   not as one global on/off setting.
4. **Skill marketplace alone** — skills without shared artifact contracts merely
   standardize prompts, so this branch is **pruned** as insufficient.

### Promising branches dropped back to implementation

#### A. Living repository contract

- A short `AGENTS.md` maps agents to authoritative documents and commands.
- A manifest declares available capabilities, owners, evidence, and freshness.
- A validator checks links, commands, required artifacts, and declared invariants.

#### B. Capability flywheel

- A retrospective skill classifies why an agent needed human intervention.
- A learning ledger records the failure, chosen system layer, owner, and closure evidence.
- A gardening workflow promotes repeated guidance from prose into scripts, tests, or policy.

#### C. Maturity-gated autonomy

- An assessment skill scores knowledge, execution, verification, observability,
  isolation, enforcement, and maintenance independently.
- Each workflow declares prerequisites and an escalation boundary.
- Background work and auto-merge remain unavailable until their required evidence gates
  are met.

### Meta-pattern and honest ranking

The useful branches all separate **capability** from **instruction**. Instructions tell
an agent what ought to happen; a harness gives it the context and machinery to do it,
prove it, and improve the next attempt.

Ranked by value:

1. Living repository contract plus capability flywheel.
2. Maturity-gated assessment and adoption.
3. Focused setup and operational skills that share those contracts.
4. A broad autonomous platform in the first release — weak because it front-loads
   infrastructure before repository-specific bottlenecks are known.

## Core model

### Definition

A **software-agent harness** is the repository-local and connected environment that
lets an agent understand, execute, observe, verify, and safely complete engineering
work with bounded human attention.

The agent model is replaceable. The harness is the durable asset.

### Planes

| Plane | Question it answers | Typical artifacts |
|---|---|---|
| Intent | What outcome is wanted and what counts as done? | product specs, issue briefs, acceptance criteria, execution plans |
| Knowledge | What is true about this product and codebase? | `AGENTS.md`, `ARCHITECTURE.md`, domain docs, ADRs, references, generated schemas |
| Execution | How can the agent operate the system? | deterministic setup, build, test, seed, migrate, and release commands |
| Feedback | How does the agent see whether reality matches intent? | tests, UI driving, screenshots, logs, metrics, traces, performance checks |
| Policy | Which boundaries must never drift? | linters, structural tests, schemas, hooks, CI gates, remediation messages |
| Isolation | How can work run without corrupting other work? | Git worktrees, ephemeral services, namespaced data, per-task ports and telemetry |
| Lifecycle | How does work move from request to completion? | plan, implementation, review, feedback handling, recovery, PR and merge workflows |
| Hygiene | How is accumulated entropy detected and removed? | quality scorecards, debt ledgers, stale-doc checks, recurring cleanup tasks |
| Governance | Where must the agent stop or ask? | permission policy, risk classes, approval gates, audit trail, escalation rules |

No plane is sufficient alone. A repository with excellent documentation but no
executable verification is descriptive, not harnessed. A repository with exhaustive
tests but no discoverable intent can prove the wrong outcome very efficiently.

## Governing principles

### Humans steer; agents execute bounded work

Humans own priorities, value judgments, risk appetite, and exceptions. Agents should
own mechanically tractable exploration, implementation, testing, review, and repair
inside explicit boundaries.

### A map, not a manual

Keep the root instruction file short and stable. It should identify authoritative
sources and the commands that begin common workflows. Detailed knowledge belongs in
focused documents reachable through progressive disclosure.

### Repository knowledge is the durable system of record

Information required for engineering work must be versioned, discoverable, and owned.
External tools may remain the source of live business state, but stable decisions and
operating knowledge needed by agents must have a repository-visible representation or
an explicit tool path.

### Legibility is a capability

If an agent cannot inspect a UI, query logs, observe metrics, discover schema, or run a
service in its environment, that part of the system is effectively absent. Add
legibility where it closes a real verification loop.

### Enforce invariants, allow local freedom

Mechanically enforce dependency direction, boundaries, data validation, security,
reliability, and other high-value invariants. Avoid encoding personal stylistic
preferences unless inconsistency creates measurable cost.

### Error messages are remediation context

Checks should explain the violated rule, why it matters, and the smallest valid repair.
The failure output is part of the agent interface.

### Work depth-first through missing capabilities

When an agent stalls, do not merely retry with more exhortation. Classify what is
missing: intent, knowledge, execution access, feedback, policy, isolation, or human
judgment. Repair the narrowest missing capability.

### Autonomy is earned per workflow

Autonomy is not a repository-wide boolean. A workflow can become more autonomous only
when its inputs, safety bounds, validation evidence, recovery path, and escalation
conditions are reliable.

### Entropy requires continuous collection

Agents reproduce local patterns, including bad ones. Small recurring cleanup and
freshness checks are part of normal operation, not a later refactor phase.

### Human attention is the scarce resource, not the only metric

Optimize for useful outcomes per unit of human attention while protecting correctness,
security, maintainability, user impact, and reversibility. Raw lines of code and PR
counts are not success measures.

## Instruction placement rules

| Need | Correct surface |
|---|---|
| Constraint for one task | Prompt or issue/spec acceptance criteria |
| Durable repository navigation and commands | Root or nested `AGENTS.md` |
| Detailed stable knowledge | Focused versioned document |
| Long multi-step work with decisions and progress | Execution plan |
| Repeatable human/agent workflow | Skill |
| Deterministic operation | Script or task runner command |
| Mechanically checkable invariant | Test, lint, schema, hook, or CI check |
| Live external state or action | MCP server, connector, or other scoped tool |
| Stable recurring workflow | Scheduled task invoking a tested skill |
| Installable cross-repository bundle | Plugin, after individual skills stabilize |

Promotion rule: if guidance repeatedly appears in prompts, move it to durable guidance
or a skill. If the same correction repeatedly appears in review, encode it as a check
when feasible. If a check repeatedly needs judgment, keep the decision human and make
the escalation explicit.

## Reference repository shape

This is a logical contract, not a mandatory exact tree:

```text
AGENTS.md                         # short map and common commands
ARCHITECTURE.md                   # top-level domains, boundaries, dependency direction
.codex/
  config.toml                    # trusted project-specific Codex configuration
  hooks.json                     # optional lifecycle enforcement
.agents/
  skills/                        # shared repository skills, if the team uses them
docs/
  design-docs/
    index.md
    core-beliefs.md
  product-specs/
    index.md
  exec-plans/
    active/
    completed/
    tech-debt.md
  operations/
    development.md
    testing.md
    observability.md
    release.md
  references/
  generated/
  harness/
    manifest.yaml
    maturity.md
    quality-score.md
    learning-ledger.md
scripts/
  setup
  dev
  check
  test
  harness-validate
```

The system must adapt to existing repository conventions instead of moving files merely
to match this example.

## Harness manifest

The specification should define a small machine-readable manifest. YAML is shown for
readability; the implementation may choose another format.

```yaml
version: 1
owners:
  harness: platform-team
entrypoints:
  guidance: AGENTS.md
  architecture: ARCHITECTURE.md
  tracer: docs/harness/tracer-workflow.md
commands:
  setup: ./scripts/setup
  start: ./scripts/dev
  check: ./scripts/check
  test: ./scripts/test
  validate: python3 scripts/harness-validate.py .
capabilities:
  reproducible_setup:
    status: verified
    evidence:
      - .github/workflows/ci.yml
  runtime_logs:
    status: documented
    evidence:
      - docs/operations/observability.md
  ui_verification:
    status: missing
policies:
  - id: dependency-direction
    enforcement: ./scripts/check architecture
    owner: platform-team
    remediation: Run ./scripts/check architecture and repair the reported boundary.
freshness:
  review_after_days: 90
```

Required semantics:

- `entrypoints` names guidance, architecture/domain, and tracer workflow sources;
- `commands` names setup, start, focused check, full test, and harness validation paths;
- statuses are `missing`, `documented`, `executable`, `verified`, or `automated`;
- every verified or automated capability names reproducible evidence;
- every enforced policy names an owner and remediation path;
- paths and commands are validated mechanically;
- the manifest records facts and capability state, not aspirational prose.

## Maturity model

Maturity is scored per plane, not as one flattering overall number.

| Level | Name | Meaning |
|---|---|---|
| 0 | Opaque | Critical knowledge or operation depends on a person or inaccessible system |
| 1 | Documented | An agent can discover what should happen, but execution is manual or ambiguous |
| 2 | Executable | The agent can perform the workflow through deterministic commands or tools |
| 3 | Verifiable | The agent can produce evidence that the workflow succeeded |
| 4 | Enforced | Important boundaries fail mechanically with actionable remediation |
| 5 | Adaptive | Recurring maintenance detects drift and improves the harness with bounded review |

Repositories adopt the system by improving the lowest capability blocking a real
workflow, not by pursuing Level 5 everywhere.

## Initial setup

### Phase 0: Baseline and risk profile

The setup workflow performs read-only discovery first:

- identify languages, frameworks, package managers, services, databases, CI, and deploy
  surfaces;
- locate existing agent guidance, architecture docs, ADRs, specs, commands, scripts,
  skills, hooks, and automations;
- run or inspect existing setup and verification paths without rewriting them;
- identify secrets, production access, destructive commands, regulated data, and
  irreversible workflows;
- record which agent surfaces and environments the team actually uses;
- select one representative change workflow as the adoption tracer.

Output: baseline report, risk classification, gaps by plane, and proposed adoption
sequence. No mutations occur in assessment mode.

### Phase 1: Minimum viable map

- Create or shorten the root `AGENTS.md` into a table of contents.
- Point to existing authoritative docs instead of duplicating them.
- Record exact setup, start, check, test, and review commands.
- Add nested guidance only where a subtree genuinely differs.
- Define “done” for the representative tracer workflow.

### Phase 2: Reproducible execution

- Make setup idempotent or explicitly resumable.
- Normalize common operations behind stable commands without hiding useful errors.
- Document prerequisites and credential boundaries.
- Ensure clean-checkout and, where relevant, worktree execution.
- Add deterministic fixture, seed, and local dependency handling.

### Phase 3: Verification and evidence

- Establish fast local checks plus the authoritative full validation path.
- Add missing acceptance tests for the tracer workflow.
- Make UI state, logs, metrics, traces, and performance measurable where needed.
- Define the evidence bundle a completed task must report.

### Phase 4: Knowledge system of record

- Establish indexes, owners, status, and freshness for architecture, product, design,
  operations, references, and plans.
- Create a lightweight execution-plan contract for multi-hour work.
- Generate volatile reference material from source where practical.
- Add link and freshness validation.

### Phase 5: Policy and architecture enforcement

- Identify a small set of high-impact invariants from actual failure history.
- Encode them as structural tests, linters, schemas, hooks, or CI checks.
- Write remediation-focused failure messages.
- Keep exceptions explicit, narrow, owned, and expiring where possible.

### Phase 6: Isolation and lifecycle

- Make the application bootable per worktree when concurrent execution matters.
- Isolate ports, local data, services, logs, and telemetry by task.
- Define task states from intake through plan, implementation, verification, review,
  recovery, and merge.
- Define escalation conditions and who makes each judgment call.

### Phase 7: Skills and recurring maintenance

- Package only proven repeated workflows as focused skills.
- Validate each skill against representative scenarios before scheduling it.
- Add recurring documentation gardening, quality scanning, and debt collection.
- Use isolated worktrees for background mutations by default.

## Minimum viable harness

The first useful release for a repository requires only:

1. a short, accurate root map;
2. deterministic setup and verification commands;
3. one authoritative architecture or domain map;
4. one representative workflow with explicit acceptance evidence;
5. a read-only harness assessment;
6. a learning ledger for repeated friction.

Runtime observability, custom linters, hooks, automations, multi-agent review, and
auto-merge are later additions driven by demonstrated need.

## Skill architecture

Skills share the manifest, maturity vocabulary, evidence format, and escalation model.
They must compose rather than duplicate repository knowledge. Each skill has one job,
declares whether it is read-only or mutating, and stops when its safety prerequisites
are absent.

### Setup skills

#### `harness-assess`

- **Purpose:** Produce a read-only capability and risk baseline.
- **Inputs:** repository root; optional target workflow.
- **Outputs:** plane-by-plane maturity, evidence links, missing capabilities, ranked
  bottlenecks, and an adoption proposal.
- **Must not:** edit files, install dependencies, or confuse absent evidence with
  evidence of absence.

#### `harness-bootstrap`

- **Purpose:** Install the minimum viable harness into an existing or new repository.
- **Inputs:** approved assessment and selected tracer workflow.
- **Outputs:** map, manifest, stable command entrypoints, initial docs, validator, and
  change report.
- **Safety:** preview changes; preserve existing conventions; prepare incremental change
  groups and a narrow commit plan while leaving the worktree unstaged;
  never overwrite authoritative docs without explicit reconciliation.

#### `harness-deepen`

- **Purpose:** Improve one selected weak plane after the bootstrap.
- **Modes:** knowledge, execution, feedback, policy, isolation, lifecycle, hygiene, or
  governance.
- **Outputs:** a narrow design, implementation, verification evidence, manifest update,
  and rollback notes.

#### `harness-encode-invariant`

- **Purpose:** Promote a repeated review rule or failure pattern into mechanical
  enforcement.
- **Outputs:** invariant definition, scope, enforcement implementation, positive and
  negative tests, actionable failure message, owner, and exception policy.
- **Must reject:** subjective preferences that cannot be tested consistently.

#### `harness-expose-runtime`

- **Purpose:** Make a concrete runtime surface inspectable by an agent.
- **Modes:** UI, logs, metrics, traces, performance, database state, or external API.
- **Outputs:** scoped tool/command, fixture, access boundary, verification example, and
  teardown path.

### Day-to-day skills

#### `harness-plan-work`

Turns a goal into an execution plan linked to authoritative knowledge, risks,
acceptance criteria, verification commands, and human decision points.

#### `harness-deliver-work`

Runs the repository’s normal change lifecycle: baseline, reproduce or characterize,
implement, verify, self-review, collect evidence, and prepare the handoff or PR. This
skill should call existing specialized skills for debugging, TDD, code review, or PR
handling rather than reimplement them.

#### `harness-review-evidence`

Reviews a change against both its originating spec and repository standards. It checks
the evidence bundle, not only the diff, and distinguishes a product judgment from a
mechanically repairable defect.

#### `harness-capture-learning`

Classifies a correction or intervention, records it in the learning ledger, and
proposes the narrowest durable improvement. It does not automatically convert every
preference into policy.

#### `harness-garden`

Scans for stale docs, broken links and commands, orphaned plans, expired exceptions,
duplicated guidance, architecture drift, and repeated local workarounds. Default mode
is read-only; fix mode produces small reviewable changes.

#### `harness-quality-report`

Updates capability maturity and trend metrics from reproducible evidence. It must show
unknowns and regressions rather than collapsing them into one score.

### Possible plugin boundary

After the skills and artifact contracts stabilize, package them as a plugin containing:

- the setup and operational skills;
- manifest schema and validators;
- reusable scripts and document templates;
- optional hooks that enforce validated policies;
- reference material and migration guidance.

Live repository hosting, issue tracking, observability, or deployment actions should
remain connectors or MCP tools rather than being simulated inside the plugin.

## Shared skill output contracts

### Assessment finding

```yaml
id: feedback.runtime-logs
plane: feedback
level: 1
confidence: high
scope: credential-free tracer execution on assessed-ref@commit
required_for_tracer: true
evidence:
  - docs/operations/observability.md
present_capability: Runtime logging is documented but has no task-local query path.
gap: Agents cannot query task-local logs.
impact: Runtime defects require human reproduction.
next_capability: Add a read-only log query command for the tracer service.
risk: R1
```

### Task evidence bundle

Every completed mutating workflow reports:

- starting state and scope;
- changed artifacts;
- acceptance criteria and result for each;
- commands run and meaningful outputs;
- runtime evidence where applicable;
- review findings and resolutions;
- residual risks, skipped checks, and reasons;
- required human judgment or follow-up.

### Learning ledger entry

Every durable improvement records:

- observed friction or failure;
- frequency and impact;
- missing plane or capability;
- chosen storage/enforcement layer;
- change made or decision not to encode;
- owner and evidence of closure;
- review or expiry date.

## Autonomy and safety model

### Risk classes

| Class | Examples | Default behavior |
|---|---|---|
| R0: inspect | read files, query local state, analyze history | autonomous, read-only |
| R1: reversible local | edit tracked files, run tests, create worktree | autonomous in workspace with evidence |
| R2: shared reversible | push branch, open draft PR, update non-production issue | explicit workflow authorization and audit |
| R3: consequential | merge, deploy staging, mutate shared test data | explicit gate plus recovery path |
| R4: high consequence | production deploy, destructive migration, secrets, policy changes | human approval at action time; often outside skill scope |

Each skill declares its maximum class. A scheduled task may not depend on interactive
approval; it must either stay below that boundary or stop with a precise handoff.

### Escalation contract

Agents escalate when:

- acceptance criteria conflict or require a product tradeoff;
- evidence cannot distinguish safe outcomes;
- permissions, credentials, or data access exceed the authorized workflow;
- a destructive or irreversible action is required;
- the repository’s sources of truth disagree materially;
- an exception would weaken a protected invariant;
- recovery is unavailable or untested for the proposed action.

## Measurement

Measure trends per workflow and repository area:

- cold-start time to locate authoritative context and commands;
- clean-checkout and clean-worktree setup success rate;
- percentage of acceptance criteria backed by executable evidence;
- first-pass task success and post-merge regression rate;
- human interventions per completed task, classified by missing plane;
- median time from request to reviewable evidence;
- percentage of repeated corrections promoted to a durable layer;
- documentation freshness and broken-reference rate;
- architecture/invariant violations caught before review;
- background task recovery and false-positive rate;
- revert, rollback, and escaped-defect rate.

Do not optimize lines of code, prompt length, agent runtime, or PR count in isolation.

## Acceptance criteria for this project

### Specification

- Defines all planes, principles, maturity levels, instruction placement rules, and
  safety boundaries in technology-neutral language.
- Separates article-derived observations, recommended defaults, and context-dependent
  choices.
- Includes an initial setup sequence for both greenfield and existing repositories.
- Defines manifest, assessment, evidence, and learning-ledger contracts.
- Describes incremental adoption and rollback rather than a one-shot rewrite.

### Setup workflow

- On an unfamiliar repository, `harness-assess` produces a read-only report whose claims
  link to evidence.
- `harness-bootstrap` previews changes and installs the minimum viable harness without
  discarding existing guidance or workflow conventions.
- A clean checkout or worktree can follow the documented setup and run the declared
  checks.
- The harness validator detects broken paths, commands, and unsupported capability
  claims.

### Day-to-day operation

- A representative change can move from goal to evidence-backed review using the shared
  artifact contracts.
- A repeated correction can be captured and routed to the right durable layer.
- A maintenance run can detect stale or drifting harness artifacts without mutating by
  default.
- Every mutating workflow reports residual risk and stops at its declared autonomy
  boundary.

## Validation strategy

Test the skills against a small repository matrix:

1. Greenfield application with minimal documentation.
2. Mature monorepo with existing guidance, CI, and architectural conventions.
3. Legacy repository with incomplete setup and flaky validation.
4. Service with no UI but meaningful logs, metrics, and external dependencies.
5. Frontend application requiring browser-visible verification.

For each repository, evaluate at least:

- no-op behavior when the capability already exists;
- preservation of user-owned conventions and dirty worktrees;
- quality and traceability of assessment evidence;
- usefulness of generated maps and remediation messages;
- ability to stop safely when credentials or judgment are required;
- whether a second run improves or merely repeats the first.

## Rollout

### Milestone 1: Vocabulary and assessment

- Finalize this specification and manifest schema.
- Implement `harness-assess` in read-only mode.
- Run it on two contrasting repositories and revise the model.

Completion evidence: [`skills/harness-assess/RUNS.md`](../../../skills/harness-assess/RUNS.md)
compares the initial `unified-request` and `auto-route` runs. The revisions make the
assessed ref, default-ref divergence, tracer-scoped split scores, stable citations, and
comparison equivalence explicit.

### Milestone 2: Minimum viable bootstrap

- Implement `harness-bootstrap` for the root map, stable commands, architecture pointer,
  tracer workflow, validator, and learning ledger.
- Require preview and a narrow commit plan; the skill leaves the change set unstaged.

Completion evidence: the skill requires a reviewed preview and narrow change groups,
ships templates for every minimum artifact, and includes a zero-dependency
`harness-validate` asset with behavior tests. [`skills/harness-bootstrap/RUNS.md`](../../../skills/harness-bootstrap/RUNS.md)
compares successful unstaged trials in `unified-request` and `auto-route`; both
repository-local validators pass and a read-only second pass is a no-op. The remaining
cases in [`EVALS.md`](../../../skills/harness-bootstrap/EVALS.md) are broader hardening,
not blockers for Milestone 3.

### Milestone 3: Daily lifecycle

- Implement `harness-plan-work`, `harness-review-evidence`, and
  `harness-capture-learning`.
- Compose existing implementation, debugging, review, and PR skills where available.

Initial implementation evidence: each skill now ships a concrete output contract and a
static contract test. Their `EVALS.md` files define repository-trial cases and their
`RUNS.md` files record local validation. Real lifecycle trials remain open before
Milestone 3 is called complete.

### Milestone 4: Deepening capabilities

- Add `harness-deepen`, `harness-encode-invariant`, and `harness-expose-runtime` based
  on gaps observed in real repositories.

### Milestone 5: Hygiene and automation

- Add gardening and quality-report skills.
- Test them manually before introducing scheduled tasks.
- Package a plugin only after shared contracts have survived cross-repository use.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Cargo-culting OpenAI’s exact repository | Specify capabilities and evidence, not one folder tree or toolchain |
| Building a giant instruction corpus | Keep `AGENTS.md` as a map; validate ownership, links, and freshness |
| Premature autonomy | Gate per workflow and risk class; require evidence and recovery |
| Excessive policy | Encode only high-value, consistently testable invariants; support owned exceptions |
| Harness maintenance becomes its own product tax | Start from tracer workflows and measure human attention actually saved |
| Agents game a maturity score | Score planes separately and require reproducible evidence |
| Existing repos are destructively normalized | Assess first, preview, adapt to conventions, and use incremental change groups |
| Skills duplicate specialized workflows | Compose existing skills behind shared contracts |
| Scheduled cleanup creates noisy churn | Default to read-only reports, small diffs, worktree isolation, and false-positive tracking |
| Repository truth diverges from production reality | Connect live state through scoped tools and label generated or observed evidence clearly |

## Resolved implementation decisions

1. The first evaluation repositories are `Uniblock-dev/unified-request` and
   `Uniblock-dev/auto-route`. The capability model remains portable, but these two repos
   decide the initial implementation’s usefulness.
2. The manifest uses YAML. It is directly reviewable and has mature validation support;
   the schema can later gain JSON-schema tooling without changing the authoring format.
3. The pair deliberately contrasts a large TypeScript/NestJS service with many specialized
   validation lanes and a Python/FastAPI service with a consolidated `Makefile` gate and
   import-linter architecture contracts.
4. Delivery skills wrap Matt Pocock engineering skills where possible: grilling,
   domain-modeling, spec/ticket creation, wayfinding, diagnosis, TDD, implementation,
   code review, and merge-conflict resolution. Harness skills retain repository grounding,
   risk gates, artifact contracts, and evidence reporting.
5. `harness-bootstrap` prepares an unstaged change set. It does not stage, commit, push,
   or open a PR.
6. Codex is the primary surface. Shared instructions live in `AGENTS.md`; `CLAUDE.md` is a
   minimal pointer to it, with Claude-only guidance added only when a real difference
   exists.
7. Initial scheduled tasks are R0 read-only. R1 is allowed only for a workflow proven
   manually and isolated in a worktree. R2–R4 remain workflow-specific; R4 requires a
   human gate and normally stays outside a skill.
8. Skills remain repository-portable during evaluation. Plugin packaging is deferred
   until the contracts have survived both target repositories without repository-specific
   branching in the core workflows.

## Sources and provenance

Primary source:

- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) — the
  experimental operating model, repository knowledge pattern, legibility, enforcement,
  autonomy loop, and recurring garbage-collection concepts.

Supporting official guidance:

- [AGENTS.md](https://agents.md/) — the open agent-guidance format and nested-instruction
  behavior.
- [OpenAI: Using PLANS.md for multi-hour problem solving](https://developers.openai.com/cookbook/articles/codex_exec_plans) — execution-plan structure and use.
- [OpenAI Codex: Best practices](https://learn.chatgpt.com/guides/best-practices) — current
  guidance on progressive setup, `AGENTS.md`, skills, tools, verification, worktrees,
  and scheduled tasks.
- [OpenAI Codex: Build skills](https://learn.chatgpt.com/docs/build-skills) — current
  skill placement, structure, triggering, and testing guidance.
- [OpenAI Codex: Worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) —
  local isolation and background-work behavior.
- [OpenAI Codex: Hooks](https://learn.chatgpt.com/docs/hooks) — lifecycle enforcement,
  trust, and configuration behavior.
- [OpenAI Codex: Scheduled tasks](https://learn.chatgpt.com/docs/automations) — recurring
  workflow, skill composition, isolation, and permission constraints.

Interpretive additions in this spec—not direct claims from the article—include the
nine-plane model, manifest, maturity scale, autonomy risk classes, shared skill output
contracts, and proposed skill family.
