# Exec Plans for Coding Agents (OpenAI Codex Cookbook)

- **Source**: [Exec Plans for Coding Agents](https://developers.openai.com/cookbook/articles/codex_exec_plans) — OpenAI Codex Cookbook (author and publication date not shown on the page)
- **Retrieved**: 2026-08-14
- **Owner**: harness skills (`skills/harness/`)
- **Local-copy reason**: durable summary — this article is the origin concept for the
  ExecPlan lifecycle that `harness-exec-plan` implements (self-contained, living,
  novice-guiding, outcome-focused plans for autonomous multi-hour agent work). A link alone
  risks drift: the repository's ExecPlan template has already diverged from the source in
  named ways (see Repository inference), and future readers need the original definition to
  tell "inherited from source" apart from "repository-specific addition."
- **Consumers**:
  - [skills/harness/harness-exec-plan/SKILL.md](../../skills/harness/harness-exec-plan/SKILL.md) —
    implements the ExecPlan lifecycle (create/resume/maintain/complete) this article defines
  - [skills/harness/harness-exec-plan/assets/exec-plan.md.template](../../skills/harness/harness-exec-plan/assets/exec-plan.md.template) —
    the repository's concrete ExecPlan skeleton, built on this article's required sections

## Sourced facts

- ExecPlans are thorough design documents that let a coding agent (Codex) implement complex,
  multi-hour tasks autonomously. They are "living documents": iteratively updated as work
  proceeds, written so that a complete novice with no prior repository knowledge could
  implement the feature end-to-end from the plan alone.
- Required sections in the source template:
  - Purpose/Big Picture — user-visible outcomes and how to observe them
  - Progress — a checkbox list with timestamps tracking granular steps
  - Surprises & Discoveries — unexpected behaviors or insights, with evidence
  - Decision Log — every design decision with rationale and date
  - Outcomes & Retrospective — achievements and lessons learned
  - Context & Orientation — repository state, assuming zero prior knowledge
  - Plan of Work — prose describing edits and additions
  - Concrete Steps — exact commands, working directories, expected outputs
  - Validation & Acceptance — observable behavior, test commands, success criteria
- Non-negotiable principles: self-containment (all needed knowledge lives in the plan, no
  external references), plain language (define specialized terms on first use), observable
  outcomes (acceptance framed as demonstrable behavior, not internal code attributes), and
  idempotence (steps must be safely re-runnable).
- Lifecycle: author the plan as a single fenced Markdown code block following the skeleton;
  the agent then proceeds autonomously without prompting the user for next steps, updating
  every section at stopping points; the plan must stay fully self-contained so work can
  resume from the document alone at any time.
- Positioned as distinct from a typical PRD/spec: agent-executable rather than
  human-referential, iteratively maintained rather than fixed once written, and explicitly
  self-sufficient (no pointers to external docs or prior chat context).

## Repository inference

- `harness-exec-plan`'s template ([exec-plan.md.template](../../skills/harness/harness-exec-plan/assets/exec-plan.md.template))
  keeps every source-required section but adds several the article does not mention:
  Acceptance Evidence as a distinct per-criterion section, per-milestone structure (goal,
  completion criterion, verification, rollback/recovery, escalation boundary), a top-level
  Idempotence and Recovery section, Artifacts and Notes, and Interfaces and Dependencies.
  These additions reflect this repository's broader emphasis on rollback paths, escalation
  boundaries, and evidence-backed review (see `harness-review-evidence`,
  `harness-plan-work`) rather than anything sourced from the article.
- The article's "single fenced Markdown code block" authoring format is narrowed by the
  repository contract: ExecPlan files omit the outer fence themselves, and only gain one
  when embedded inside another Markdown document — a repository-specific packaging rule, not
  a source requirement.
- The source does not specify a lifecycle index, a completed-plan location, or coordination
  with ADRs/domain-language skills; `harness-exec-plan` step 4 (index update, move to
  completed location) and its links to `harness-record-decision` and
  `harness-model-domain` are repository additions layered on top of the source concept.

## Freshness

- Cookbook article with no visible publish/update date; treat the "Sourced facts" above as
  the state observed on 2026-08-14. Re-check if `harness-exec-plan`'s template diverges
  further and the divergence needs re-justifying against the source, or opportunistically
  during the next `harness-garden` pass over `docs/references/`.
