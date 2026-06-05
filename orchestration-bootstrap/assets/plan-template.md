# Project Milestones And Validation

@@PROJECT_OVERVIEW@@

The project overview above is only the starting point. During planning, refine it into a concrete description of what the system does, who consumes it, which external systems it depends on, and which contracts must remain stable.

## HOW TO PLAN A MILESTONE

If the user asks you to plan a milestone, these are the steps to take.

1. Read all of `PLAN.md` (the current document) to learn about the milestone in the context of past and future milestones. This document lists only the essential deliverables and validation steps for each milestone.
2. Read all prior `PLAN_M{n}.md` or `PLAN-M{n}.md` milestone documents.
3. Ask any important initial clarifying questions about the milestone you might have.
   - If you are not asking any questions at all for the entire planning, something is probably wrong. This file is intentionally not fully specified. There must be important things to clarify.
   - It is better to eliminate unknowns by discovering facts, not by asking the user. Do not ask questions that can be answered from the repo or system, such as which route owns an endpoint, which command exists, which schema/model is used, or where a core function lives. Explore first.
   - Discoverable facts (repo/system truth): explore first. Before asking, run targeted searches and check likely sources of truth: entrypoints, routes/controllers/handlers, schemas/models, service modules, adapters, persistence definitions, generated assets, scripts, tests, docs, `README*`, package/build config, and existing architecture docs. Ask only if multiple plausible candidates remain, nothing found but a missing identifier is required, or the ambiguity is product intent. If asking, present concrete candidates and recommend one.
   - Preferences/tradeoffs (not discoverable): ask early. These are intent or implementation preferences that cannot be derived from exploration. Provide 2-4 mutually exclusive options plus a recommended default. If unanswered, proceed with the recommended option and record it as an assumption in the final plan.
   - When you ask a question, the user does not have your context. Phrase questions with full context, tradeoffs, background, and explanation of terms. Do not use unexplained jargon. A good question is typically 2-5 sentences long.
   - Questions should materially change the spec/plan, confirm or lock an assumption, or choose between meaningful tradeoffs. They must not be answerable by research.
   - Keep asking until you can clearly state: goal, success criteria, audience, in/out of scope, constraints, current state, and key preferences/tradeoffs.
   - Once intent is stable, keep asking until the spec is decision complete: approach, interfaces (APIs/schemas/I/O), data flow, edge cases/failure modes, testing and acceptance criteria, rollout/monitoring, and any migrations/compatibility constraints.
4. Research milestone-relevant aspects of how this repo works and how to use it. These are your resources:
   - Read `README*`, package/build config, test config, env examples, and the relevant module entrypoints.
   - Start from app/library/job entrypoints and dependency wiring before changing runtime behavior.
   - For API/UI/CLI work, read the relevant route/command/component, request/response/input schemas, service layer, tests, and user-facing docs before changing behavior.
   - For data/persistence work, read model/schema definitions, migrations, adapters, tests, and operational docs.
   - For generated or synced output, identify the source of truth first, then the generator/sync command.
5. Research milestone-relevant implementation details by following the flow from entrypoint into domain logic, adapters, persistence, and output contracts. Identify whether the change touches public/user-facing behavior, generated assets, external integrations, auth, persistence, observability, migrations, or deployment/runtime configuration.
6. Flesh out the milestone deliverables and validation steps as needed.
   - Focus on validation in everything you do.
   - The validation steps should explain how someone implementing this milestone can validate that the implementation is good.
   - Include the basics: primary build/typecheck/test commands, targeted tests, lint/static checks when relevant, and generated/synced commands when generated assets or public metadata change.
   - Prefer focused tests over broad brittle tests. Include unit tests for pure/domain logic and route/service/integration tests when behavior crosses boundaries.
7. Develop your plan for the milestone and write it to a new `PLAN_M{n}.md` or `PLAN-M{n}.md` file, matching the repo's existing milestone style.
   - A great plan is detailed enough that it can be handed to another engineer or agent and implemented right away. It must be decision complete, so the implementer does not need to make product or architecture decisions. It must be self-contained: the implementer will know nothing of your research other than what is in the milestone plan file.
   - The plan must include validation steps: how someone implementing the plan will validate that they have done it well.
8. Are there better-engineering blockers? If so, bail.
   - The user wants things done the right way, with clean engineering and good architecture. Never use shortcuts that hide broken architecture, stale generated artifacts, missing validation, poor error handling, weak auth, brittle persistence, or observability gaps.
   - If the architectural problem is small enough to solve, include that as a phase in your plan. If it is major enough to deserve a separate plan, stop, explain the problem, and leave room for a new milestone.
9. Present your milestone plan file to Claude and ask for feedback when the user, plan, or local process requires second-opinion review.
   - If Claude cannot run for whatever reason, report what is wrong.
   - Invoke Claude exactly as described in `AGENTS.md`: write a self-contained prompt to `@@REPO_ROOT@@/claude.{id}.input.md`, then run Claude from `@@REPO_ROOT@@` and write output to `@@REPO_ROOT@@/claude.{id}.output.md`.
   - You can trust Claude will read `AGENTS.md` and is able to do its own autonomous research.
   - If Claude found no problems with your plan, you may proceed.
   - Otherwise, address the issues Claude found: if you agree, update your plan; if you disagree, update your plan to defend your perspective better.
   - Keep iterating with Claude until you no longer make changes. If you take more than 10 rounds, something is wrong, so stop and tell the user.
   - We are not looking for "blocker vs non-blocker" decisions. For every suggestion from Claude, evaluate whether it will improve the plan. If so, modify the plan. If not, pre-emptively defend in the plan why not.
   - Do not reference previous rounds when you invoke Claude. Claude does best starting from scratch each round, with the current state of files and repo on disk.
10. Ask the user any further important clarifying questions that arose as a result of your research and Claude.
    - Postpone these questions until after research and review when possible. That way you can do as much planning as possible without slowing the user down.
    - Every course correction the user gives you likely represents a gap that should be added to `LEARNINGS.md` or an architecture note. Use `LEARNINGS.md` for durable engineering wisdom, architecture docs for stable system design, and milestone plan files for milestone-specific notes.
11. Present the plan for user review and signoff.
    - First, double-check that it is a completely self-contained handoff document.

Please use the following format for milestone plan files:

```md
@@MILESTONE_TEMPLATE@@
```

## HOW TO EXECUTE A MILESTONE

Please include this section verbatim when you write a milestone plan file. It will be used to guide anyone who executes on your plan.

@@GENERIC_EXECUTION_WORKFLOW@@

## Milestone 1: Development infrastructure

@@REPO_SPECIFIC_M1@@

## Milestone 2: Architecture and core flow

@@REPO_SPECIFIC_M2@@

## Milestone 3: First user-selected feature or integration

@@REPO_SPECIFIC_M3@@
