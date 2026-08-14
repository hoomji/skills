# Harness engineering system

## Document control

| Field | Value |
| --- | --- |
| Lifecycle state | Active |
| Product owner | Repository maintainers |
| Created | 2026-08-13 |
| Last reviewed | 2026-08-13 |
| Review trigger | Material changes to shared contracts, skill boundaries, risk classes, or target repositories |
| Product surface | `skills/harness/` and the repository artifacts its skills create or consume |
| Authority | This file owns product intent and observable behavior for the harness engineering system |

The [historical engineering specification](../superpowers/specs/2026-08-11-harness-engineering-system.md) preserves design exploration, implementation decisions, and milestone history. It remains supporting evidence; this document is the authoritative product contract when the two differ.

## Executive summary

The harness engineering system is a repository-centered operating model for reliable agent-assisted software delivery. It makes product intent, repository knowledge, development operations, feedback, policy, isolation, lifecycle, hygiene, and governance legible to coding agents.

The product is a family of focused skills and shared artifact contracts. It does not replace a repository's tools or prescribe a universal folder tree. It assesses what exists, identifies the narrowest capability blocking a real workflow, improves that capability, and requires evidence before claiming greater readiness or autonomy.

Its core value is compounding human judgment. Durable knowledge, repeatable methods, and enforceable invariants should survive the conversation in which they were discovered. Subjective judgment must not become policy merely because an agent encountered it once.

## Vision

Make a software repository understandable, operable, verifiable, and maintainable by a coding agent from a cold start, while humans retain control of product judgment, risk, exceptions, and consequential actions.

## Problem

Coding agents can produce changes faster than teams can communicate intent and validate outcomes. In repositories designed around human memory and manual operation:

- authoritative knowledge is scattered across chat, external systems, stale documents, and individuals;
- setup, start, check, test, and recovery paths are ambiguous or non-deterministic;
- product intent and architectural boundaries are hard to discover;
- UI state, logs, metrics, traces, and runtime evidence are invisible to the agent;
- concurrent work collides through shared ports, services, data, or telemetry;
- review feedback repairs one change but does not improve the next run;
- documentation claims capabilities that cannot be reproduced;
- broad autonomy is granted without workflow-specific evidence, recovery, or escalation.

These failures consume human attention, weaken trust, and let agents repeat local mistakes at high speed.

## Users and stakeholders

### Repository maintainer

Wants to adopt agent-assisted workflows without replacing working conventions or installing an oversized platform. Needs a grounded assessment, incremental adoption, safe defaults, and evidence of improvement.

### Product or engineering lead

Defines outcomes, risk appetite, and human decision points. Needs product intent separated from implementation plans and autonomy bounded by evidence.

### Coding agent

Needs a concise map, authoritative sources, deterministic operations, inspectable runtime state, actionable failures, and explicit stop conditions.

### Secondary stakeholders

- reviewers evaluating claims against reproducible evidence;
- platform and security owners defining permissions and protected boundaries;
- contributors who need generated artifacts to remain human-readable;
- operators responsible for runtime inspection and recovery.

## Jobs to be done

1. Assess what an agent can safely do and prove in an unfamiliar repository without mutation.
2. Establish the smallest useful repository map and stable workflow without discarding existing conventions.
3. Identify and deepen the one harness capability blocking a real delivery workflow.
4. Preserve intent, decisions, progress, verification, and human decision points for complex work.
5. Route repeated corrections to the narrowest durable and enforceable layer.
6. Review changes against originating intent and evidence, not only the diff.
7. Detect stale, broken, conflicting, duplicated, or orphaned harness artifacts.
8. Require workflow-specific safety, recovery, audit, and escalation evidence as autonomy increases.

## Desired outcomes

- An agent can locate authoritative intent, architecture, and commands from a small entrypoint.
- Common workflows execute deterministically and produce distinguishing evidence.
- Product requirements map to observable acceptance criteria.
- Runtime behavior required for verification is inspectable within authorized boundaries.
- Repeated human interventions decline because learning becomes durable.
- Capability claims are current, owned, and reproducible.
- Parallel and background work does not corrupt shared state.
- Consequential actions stop at explicit human gates.
- Harness maintenance creates small, reviewable changes instead of noise.

## Non-goals

- Requiring all code or documentation to be agent-generated.
- Eliminating human review, product judgment, architecture, or operational ownership.
- Requiring OpenAI's internal stack, repository shape, throughput, or merge policy.
- Defining one application architecture, language, package manager, or CI provider.
- Replacing task trackers, testing frameworks, deployment systems, or observability platforms.
- Installing every possible capability during initial adoption.
- Treating maturity, pull-request count, lines of code, or runtime as standalone success.
- Granting repository-wide autonomy as one on/off setting.
- Encoding subjective preferences that cannot be applied consistently.
- Treating an external article or SDK guide as a normative requirement.

## Product principles

### Humans steer; agents execute bounded work

Humans own priorities, value judgments, risk tolerance, and exceptions. Agents explore, implement, verify, review, and repair only inside explicit authorization boundaries.

### Use a map, not a manual

Root guidance is a concise map to focused sources and stable commands. Detailed knowledge lives where it can be owned, reviewed, linked, and maintained.

### Preserve repository truth

The system adapts to existing authorities and workflows. It does not move or overwrite them merely to match a reference layout.

### Record facts, not aspirations

Manifests and assessments describe evidenced current state. Planned capabilities belong in product specifications or execution plans.

### Improve the narrowest blocking capability

Adoption follows a representative tracer workflow. A repository need not maximize every capability plane before gaining value.

### Enforce invariants, permit local freedom

Security, correctness, dependency direction, data boundaries, and other durable rules should fail mechanically when feasible. Incidental style remains flexible.

### Make failures actionable

Validation output identifies the violated contract, why it matters, and the smallest valid remediation path.

### Earn autonomy per workflow

Inputs, permissions, validation, recovery, and escalation must be reliable for the exact workflow receiving more autonomy.

### Treat entropy collection as normal operation

Agents amplify good and bad patterns. Freshness and cleanup are recurring capabilities, not one-time migrations.

## Domain model

### Harness

The repository-local and connected environment that lets an agent understand, execute, observe, verify, and safely complete engineering work.

### Tracer workflow

A representative end-to-end task used to identify the next capability worth improving and prove the harness in practice.

### Capability planes

| Plane | Product question |
| --- | --- |
| Intent | What outcome is required, and what counts as done? |
| Knowledge | What product, domain, architecture, and operational facts are authoritative? |
| Execution | Can the agent perform setup, build, start, test, migration, and release operations? |
| Feedback | Can the agent observe whether behavior matches intent? |
| Policy | Which important boundaries fail mechanically? |
| Isolation | Can work execute without interfering with other work? |
| Lifecycle | Can work move from intake through delivery, review, recovery, and closure? |
| Hygiene | Can drift, staleness, debt, and repeated workarounds be detected and resolved? |
| Governance | Where must work stop, request approval, or produce an audit trail? |

### Capability levels

| Level | Name | Observable meaning |
| --- | --- | --- |
| 0 | Opaque | A person or inaccessible system is required. |
| 1 | Documented | Instructions exist, but execution or interpretation is manual or ambiguous. |
| 2 | Executable | A deterministic command or tool performs the capability. |
| 3 | Verifiable | Reproducible evidence distinguishes success from failure. |
| 4 | Enforced | Important boundaries fail mechanically with remediation. |
| 5 | Adaptive | Bounded maintenance detects drift and improves the harness. |
| Unknown | Unknown | Available evidence cannot justify a level. |

Report the lowest fully evidenced level. Never average the planes into a flattering repository score.

### Evidence bundle

The completion record for a mutating workflow: starting state, requested scope, changed artifacts, acceptance results, commands and outcomes, runtime evidence, review findings, residual risks, skipped checks, and required follow-up.

### Learning entry

A record of repeated friction, impact, missing plane, selected durable layer, resulting change or decision not to encode, owner, closure evidence, and review date.

## Capability map

| Capability | Primary skill | Observable output |
| --- | --- | --- |
| Route a request | `harness` | Narrowest applicable workflow and named follow-ons |
| Establish a baseline | `harness-assess` | Read-only findings by plane |
| Install a minimum harness | `harness-bootstrap` | Previewed, repository-aligned, unstaged artifacts |
| Improve one plane | `harness-deepen` | Narrow change with verification and rollback notes |
| Encode an invariant | `harness-encode-invariant` | Enforced rule, tests, remediation, owner, exceptions |
| Expose runtime state | `harness-expose-runtime` | Scoped inspection path, fixture, boundary, evidence, teardown |
| Define product intent | `harness-product-spec` | Indexed behavioral contract with acceptance criteria |
| Maintain design documentation | `harness-design-doc` | Indexed design model with lifecycle and verification status |
| Plan complex execution | `harness-plan-work`, `harness-exec-plan` | Living plan linked to intent, evidence, risks, decisions |
| Deliver a change | `harness-deliver-work` | Verified change and evidence bundle |
| Review evidence | `harness-review-evidence` | Findings against intent, standards, and proof |
| Capture learning | `harness-capture-learning` | Learning entry and narrow durable improvement |
| Curate external knowledge | `harness-reference` | Provenance-first, indexed, bounded reference |
| Garden the harness | `harness-garden` | Read-only drift report or approved repairs |
| Report quality | `harness-quality-report` | Plane-specific levels, trends, regressions, unknowns |

## Primary user journeys

### Assess an unfamiliar repository

1. Select a repository and optional tracer workflow.
2. Discover guidance, architecture, commands, CI, runtime surfaces, permissions, secrets boundaries, and existing artifacts.
3. Keep discovery read-only and identify assessed revision and scope.
4. State present capability, evidence, gap, impact, next capability, risk, and confidence for each finding.
5. Rank tracer-blocking gaps without confusing undiscovered evidence with absence.

Outcome: the team selects the next improvement using evidence rather than a generic checklist.

### Bootstrap a minimum viable harness

1. Approve an assessment and tracer workflow.
2. Preview a narrow change set preserving repository conventions.
3. Establish or reconcile concise guidance, architecture and indexed design-documentation pointers, deterministic commands, manifest, tracer, validator, and learning ledger.
4. Leave the worktree unstaged for review.
5. Confirm a second read-only run creates no unnecessary changes.

Outcome: a clean checkout or worktree can discover and exercise the tracer's minimum development loop.

### Maintain design documentation

1. Resolve the governing product spec, architecture map, related ADRs, code, and evidence.
2. Create or revise an indexed design doc describing rationale, constraints, interfaces, alternatives, and operational implications.
3. Record owner, lifecycle state, last-verified date, verification evidence, and review trigger.
4. Keep discrete decisions in ADRs and implementation sequencing in ExecPlans.
5. Verify links and claims, then update the index without erasing superseded design history.

Outcome: agents can understand how and why a system is designed, while ADRs remain a separate authoritative decision log.

### Deepen one capability

1. A tracer failure or assessment identifies one weak plane.
2. Define the observable improvement and rollback boundary.
3. Implement only necessary knowledge, tooling, feedback, policy, isolation, or governance changes.
4. Update capability status only after reproducible evidence supports it.

Outcome: the blocking workflow gains measurable capability without broad normalization.

### Deliver evidence-backed work

1. Resolve product intent and acceptance criteria.
2. Create a living plan for complex work.
3. Establish a baseline, characterize behavior, implement, verify, self-review, and record evidence.
4. Review against both product intent and repository standards.
5. Stop at the authorization boundary and name residual risks.

Outcome: reviewers can determine delivery without reconstructing chat history.

### Turn correction into capability

1. Record a human intervention or repeated failure with frequency and impact.
2. Classify the missing plane and choose the narrowest durable layer.
3. Keep one-off preferences local; promote stable knowledge, methods, operations, and invariants appropriately.
4. Record closure evidence and review date.

Outcome: repeated friction declines without indiscriminate rules.

### Maintain harness health

1. Scan freshness, links, commands, evidence, duplicate guidance, expired exceptions, orphaned plans, and recurring workarounds.
2. Distinguish confirmed defects, unknowns, and recommendations.
3. Produce only small approved repairs in fix mode.
4. Require prior manual success and isolation before scheduling mutations.

Outcome: guidance and capability claims remain trustworthy.

## Functional requirements

### FR-1: Routing

- Select the narrowest skill that completes the requested job.
- Name the primary action and later phases for cross-cutting requests.
- Do not infer authorization for implementation, publishing, deployment, or other external action.

### FR-2: Repository grounding

- Read applicable repository guidance before acting.
- Reconcile relevant specs, architecture, indexed design docs, ADRs, plans, references, and observable behavior.
- Surface conflicting authorities rather than silently choosing a tradeoff.
- Preserve user-owned changes.

### FR-3: Progressive disclosure

- Keep entrypoints concise and link to deeper authorities.
- Do not duplicate detailed knowledge across guidance surfaces without clear ownership.
- Add nested guidance only where a subtree genuinely differs.

### FR-4: Assessment

- Assessment is read-only.
- Every factual claim cites a path, command, source, or explicit unknown.
- Findings include revision, scope, confidence, tracer relevance, present capability, gap, impact, next capability, and risk.
- Report planes independently and distinguish absent evidence from evidence of absence.

### FR-5: Bootstrap

- Require an approved tracer and change preview.
- Adapt to repository paths and tools.
- Reconcile existing guidance instead of overwriting it.
- Leave changes unstaged and provide narrow change groups.
- Define stable setup, start, check, test, and validation entrypoints, using `unknown` only where permitted.
- Be idempotent or explain repeat-run differences.

### FR-6: Product intent

- Specifications name users, problem, outcomes, non-goals, constraints, sources, state, and owner.
- Required behavior maps to observable acceptance criteria.
- Product intent stays separate from implementation sequence and architecture decisions.
- Historical specs are preserved or explicitly superseded with links.

### FR-6a: Design documentation

- Design documentation is indexed and records state, owner, last verification, evidence, and review trigger.
- Design docs own system or feature rationale, constraints, interfaces, alternatives, and operational implications.
- Design docs link product specs, architecture maps, ADRs, plans, and implementation evidence without taking over their authority.
- ADRs remain separate records of discrete decisions and are never replaced by design-doc history.

### FR-7: Plans and delivery

- Complex work has a repository-local plan containing progress, decisions, verification, and recovery.
- Delivery establishes a baseline and verifies changed behavior proportionately to risk.
- Completion claims include an evidence bundle.
- Skipped checks and residual risks are explicit.

### FR-8: Runtime legibility

- Target one concrete surface: UI, logs, metrics, traces, performance, database state, or external API behavior.
- Define access scope, credential boundary, fixtures, inspection path, expected evidence, and teardown.
- Distinguish task-local state from shared or production state.
- Keep secrets and sensitive data out of references and evidence bundles.

### FR-9: Policy encoding

- Candidate invariants arise from stable requirements or repeated evidence.
- Enforcement includes positive and negative tests.
- Failures identify the rule and remediation.
- Exceptions are narrow, owned, auditable, and expiring where appropriate.
- Reject subjective or inconsistently testable preferences.

### FR-10: References

- Every local source has a consumer and local-copy reason.
- Record title, canonical source, publisher, version or retrieval date, owner, consumers, and freshness.
- Prefer concise summaries and separate sourced facts from repository inference.
- Index references and link them to consuming product artifacts.

### FR-11: Learning and hygiene

- Classify repeated friction before proposing a durable change.
- Support an explicit decision not to encode.
- Default gardening to read-only behavior.
- Findings name evidence, impact, owner or next action, and freshness.
- Recurrence must avoid duplicate or low-value churn.

### FR-12: Quality reporting

- Show plane-specific status, trends, regressions, and unknowns.
- Require reproducible evidence for higher levels.
- Do not conceal a blocking plane behind aggregation.
- Tie metrics to workflows and repository areas.

## Artifact contract

| Artifact | Purpose | Minimum metadata |
| --- | --- | --- |
| Guidance map | Locate authority and commands | ownership boundary, links, exact commands |
| Product specification | Define behavior | state, owner, sources, outcomes, non-goals, criteria |
| Architecture/domain record | Define structure and language | scope, boundaries, ADR links |
| Harness manifest | Record evidenced capabilities | version, owners, entrypoints, commands, evidence, policies, freshness |
| Tracer workflow | Prove adoption | workflow, prerequisites, completion evidence, risk |
| Execution plan | Coordinate delivery | scope, progress, decisions, verification, recovery |
| Assessment | Report capability | revision, findings, evidence, confidence, next capability |
| Design document | Explain a system or feature design | state, owner, scope, rationale, constraints, linked ADRs/specs, verification, review trigger |
| Evidence bundle | Support completion | scope, criteria, commands, evidence, risks |
| Learning ledger | Preserve friction and response | observation, frequency, impact, layer, owner, closure, review |
| Reference | Preserve bounded external knowledge | provenance, consumers, summary, inference, freshness |

### Manifest behavior

- Use YAML as the initial interchange format and record current facts.
- Statuses are `missing`, `documented`, `executable`, `verified`, or `automated`.
- Every `verified` or `automated` claim links to reproducible evidence.
- Every policy names enforcement, owner, and remediation.
- Validate declared paths and commands where possible.
- Preserve unknown commands as `unknown`; do not invent completeness.

### Instruction placement

| Need | Authoritative surface |
| --- | --- |
| One task's constraint | Prompt, issue, or acceptance criteria |
| Durable navigation and commands | `AGENTS.md` or equivalent map |
| Detailed stable knowledge | Focused versioned document |
| Product behavior | Product specification |
| Discrete architectural choice and status history | ADR |
| Multi-step implementation | Execution plan |
| Repeatable method | Skill |
| System or feature design | Indexed design document |
| Deterministic operation | Script or task-runner command |
| Checkable invariant | Test, lint, schema, hook, or CI gate |
| Live external state | Scoped connector, MCP server, or tool |
| Stable recurrence | Scheduled task invoking a tested workflow |

## Safety and governance

### Risk classes

| Class | Boundary | Default behavior |
| --- | --- | --- |
| R0 | Read-only inspection | Proceed autonomously in authorized scope |
| R1 | Reversible local changes | Proceed with evidence and preservation of user changes |
| R2 | Shared reversible changes | Require explicit workflow authorization and audit |
| R3 | Consequential shared changes | Require explicit gate and recovery path |
| R4 | Production, destructive, secret, or policy-sensitive changes | Require human approval at action time; normally outside skill scope |

### Mandatory escalation

Stop and request human judgment when:

- acceptance criteria conflict or require an unresolved product tradeoff;
- evidence cannot distinguish a safe outcome;
- permissions or credentials exceed authorization;
- destructive or irreversible action is required;
- authoritative sources materially disagree;
- a protected invariant needs an exception;
- recovery is absent or untested for consequential action;
- regulated, customer, private, or secret data would enter an inappropriate artifact.

### Scheduled work

- Initial scheduled workflows are R0 and read-only.
- R1 scheduling requires prior manual success and worktree-equivalent isolation.
- R2 through R4 retain workflow-specific gates.
- Scheduled tasks stop with a precise handoff at interactive approval boundaries.

## Failure and recovery behavior

| Failure | Required behavior |
| --- | --- |
| Required source inaccessible | Name the missing authority and avoid unsupported claims |
| Unrelated working-tree changes | Preserve them and constrain edits |
| Artifact-location conflict | Follow repository guidance or explicitly reconcile authority |
| Command unavailable or unstable | Record the limit and do not claim executable maturity |
| Validation fails | Report the check, affected criterion, and remediation or blocker |
| Runtime evidence ambiguous | Treat the criterion as unproven |
| Credentials or production access required | Stop at the authorization boundary |
| Repeat run creates unnecessary changes | Treat idempotence as failed and explain drift |
| External source stale or gone | Mark freshness risk and identify a successor if available |
| Repair weakens safety | Reject or escalate it |

Every mutation preserves a recovery path proportional to risk. For documentation this is a small inspectable diff; shared systems require an explicit recovery plan before action.

## Compatibility and integrations

- Codex is the primary interaction surface; shared repository artifacts remain agent-neutral.
- Tool-specific pointers may exist, but shared guidance must not be duplicated across products.
- Skills operate across greenfield, mature, legacy, service-only, and UI-heavy repositories without assuming one language or build system.
- Existing issue trackers, source hosts, CI, observability, and deployment systems remain authoritative for live state.
- External runtimes, including the OpenAI Agents SDK, may provide orchestration, tools, state, guardrails, tracing, or evaluation, but are optional integrations.
- Plugin packaging is deferred until contracts work in the target repositories without repository-specific branching in core workflows.

## Product experience

Workflows must be:

- grounded in inspected authority;
- progressive in the context they disclose;
- predictable about inspection, mutation, and external action;
- evidence-first in completion reporting;
- actionable when they fail;
- quiet when no change is needed;
- human-readable without agent tooling;
- traceable across requirements, plans, decisions, references, and evidence.

## Adoption and rollout

### Stage 0: Baseline

Assess one tracer workflow without mutation. Record gaps and risk boundaries.

### Stage 1: Minimum viable map

Reconcile concise guidance, architecture and indexed design-documentation pointers, stable commands, manifest, tracer, validator, and learning ledger.

### Stage 2: Reproducible execution and verification

Make the tracer operable from a clean checkout or worktree and back its criteria with distinguishing evidence.

### Stage 3: Runtime legibility and enforcement

Expose runtime surfaces required by observed workflows and encode a small set of high-value invariants from failure history.

### Stage 4: Lifecycle integration

Connect product specs, plans, delivery, review, learning, and recovery into an evidence-backed path.

### Stage 5: Hygiene and bounded automation

Introduce gardening, quality trends, and scheduled read-only maintenance. Expand autonomy only after manual evidence and isolation are reliable.

### Rollback and exit

- Each stage is independently reviewable and removable.
- Removing a skill does not invalidate authoritative docs or standard engineering commands.
- Generated artifacts are identifiable and can be retired without deleting human decisions.
- Scheduled tasks, hooks, and policy gates have documented disable paths.

## Measurement

### North star

Increase correctly completed, evidence-backed repository workflows per unit of human attention without increasing escaped defects, unsafe actions, or maintenance burden.

### Leading indicators

- cold-start time to locate context and commands;
- clean-checkout and clean-worktree setup success;
- percentage of acceptance criteria backed by reproducible evidence;
- time from request to reviewable evidence;
- first-pass completion rate for named tracers;
- interventions per workflow, classified by plane;
- repeated corrections promoted to an appropriate durable layer;
- current capability ownership and freshness metadata.

### Guardrails

- post-merge regression and escaped-defect rate;
- revert and rollback rate;
- unsafe or unauthorized action attempts;
- broken-reference and stale-document rate;
- gardening and enforcement false positives;
- background recovery failures;
- harness maintenance effort;
- exceptions without owners or expiry.

Lines of code, PR count, prompt length, model runtime, and maturity averages are anti-metrics unless tied to outcomes and guardrails.

## Acceptance criteria

### AC-1: Discoverability

From a clean checkout, an agent can locate product intent, architecture or domain knowledge, indexed design documentation, ADRs, common commands, tracer workflow, and risk boundaries from a concise entrypoint.

### AC-2: Assessment evidence

`harness-assess` produces a read-only report where every finding cites reproducible evidence or an explicit unknown, identifies scope and confidence, and reports planes independently.

### AC-3: Bootstrap preservation

With existing guidance and a dirty worktree, `harness-bootstrap` previews a narrow change, preserves unrelated work and authoritative conventions, leaves changes unstaged, and creates no unnecessary differences on a second read-only run.

### AC-4: Executable tracer

A clean checkout or isolated worktree can follow declared setup and verification for the tracer, or the manifest truthfully identifies missing capability without claiming success.

### AC-5: Product-to-evidence traceability

Every required outcome maps to an observable criterion, and completion reports the result and evidence for each criterion.

### AC-6: Runtime legibility

When a tracer depends on runtime behavior, the agent can inspect the required task-local surface inside its access boundary and distinguish success, failure, and ambiguity.

### AC-7: Enforced invariant

A compliant example passes, a violating example fails, and the failure identifies the selected stable rule, reason, and repair.

### AC-8: Safe autonomy

At an R2 through R4 boundary or mandatory escalation condition, the system stops unless the exact authorization and recovery contract are present.

### AC-9: Durable learning

For repeated correction evidence, `harness-capture-learning` records frequency and impact, selects the narrowest layer or declines encoding, and links closure evidence and review date.

### AC-10: Reference provenance

For a local external source, a reader can identify canonical URL, publisher, retrieval or version date, owner, consumers, sourced summary, inference, and freshness trigger.

### AC-11: Hygiene

A read-only garden run reports stale, broken, conflicting, or orphaned artifacts with evidence and impact; approved fix mode changes only named findings.

### AC-12: Honest reporting

Incomplete or contradictory evidence remains unknown or regressed and cannot elevate or hide a capability plane.

### AC-13: Portability

Core contracts work in two repositories with different languages, validation layouts, and architecture conventions without repository-specific branching in shared skills.

### AC-14: Recoverability

Every mutating workflow reports changed artifacts, validation, residual risk, and a recovery or disable path proportionate to the action.

### AC-15: Design-document ownership

An indexed design doc exposes lifecycle and verification status, links its governing specs and ADRs, and does not replace the architecture map, ADR decision history, or execution plan.

## Validation strategy

Evaluate against:

1. a greenfield application with minimal guidance;
2. a mature monorepo with established CI and architecture contracts;
3. a legacy repository with incomplete setup or flaky checks;
4. a service whose evidence is logs, metrics, traces, and external dependencies;
5. a UI application requiring browser-visible verification.

Each evaluation covers no-op behavior, dirty-worktree preservation, evidence quality, actionable errors, safe permission boundaries, and whether a second run improves or needlessly repeats the first.

The initial portability gate uses `Uniblock-dev/unified-request` and `Uniblock-dev/auto-route`, as recorded in the historical engineering specification.

## Dependencies and sources

- [OpenAI harness engineering](../references/openai-harness-engineering.md) provides background observations and an operating model.
- [OpenAI Agents SDK](../references/openai-agents-sdk.md) provides optional runtime, orchestration, guardrail, tracing, and evaluation context.
- Repository guidance, domain records, design docs, ADRs, behavior, CI, and operational tools remain authoritative for repository-specific facts.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Cargo-culting a reference repository | Specify observable capabilities and adapt to local authority. |
| Monolithic guidance | Keep entrypoints concise and validate focused ownership and links. |
| Aspirational capability claims | Require evidence and explicit unknowns. |
| Policy encodes taste | Require stable evidence, consistent tests, ownership, and exceptions. |
| Destructive normalization | Assess first, preview, preserve dirty worktrees, and reconcile authority. |
| Premature autonomy | Gate by workflow, risk, recovery, and evidence. |
| Noisy maintenance | Default to read-only scans and small approved fixes; measure false positives. |
| Duplicate specialist tooling | Compose existing tools behind shared contracts. |
| Repository/runtime divergence | Add scoped live inspection and label observed, generated, and inferred evidence. |
| External-source drift | Record retrieval, consumers, and freshness; keep decisions local. |
| Harness becomes an end in itself | Prioritize tracer-blocking capabilities and human attention saved. |

## Resolved product decisions

1. The product is focused skills with shared contracts, not one prompt or autonomous platform.
2. Readiness is assessed across nine independent planes.
3. The initial manifest format is YAML and records facts rather than plans.
4. Adoption is incremental and driven by a real tracer workflow.
5. Codex is the primary interaction surface; repository guidance remains agent-neutral.
6. Bootstrap produces an unstaged local change set and does not publish it.
7. Initial scheduled work is R0 read-only; higher-risk automation is earned per workflow.
8. Product specs, design docs, ADRs, plans, references, and evidence retain separate ownership.
9. Plugin packaging waits for portability across both target repositories.
10. The OpenAI Agents SDK is an optional integration and does not replace repository-local intent, evidence, or governance.

## Open decisions

No unresolved product decision blocks this specification. Implementation choices discovered in repository trials belong in an ExecPlan or ADR and enter this file only if they change observable product behavior.

## Change policy

Revise this specification when product outcomes, user journeys, behavioral boundaries, risk rules, shared artifact contracts, or acceptance criteria change. Preserve delivered history through links and lifecycle notes. Put system and feature design in indexed design docs, discrete architectural choices in ADRs, implementation sequencing in an ExecPlan, and external facts in references.

