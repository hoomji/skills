# Agentic Orchestration Workflow

A lightweight, file-driven approach to long-horizon autonomous coding sessions with Codex and stateless Claude review. The workflow uses markdown files and explicit prompts rather than framework-specific orchestration code.

## Overview

This workflow enables long-horizon autonomous coding by:

1. Breaking a project into milestones defined in `@@PLAN_FILE@@`
2. Having Codex generate a detailed plan for each milestone into `PLAN_M{n}.md`
3. Having a fresh Codex instance implement that plan autonomously
4. Using isolated Claude instances as reviewers across multiple dimensions
5. Running dedicated better-engineering milestones to keep code quality high

The AI writes milestone plans for AI implementers. Humans should focus on product decisions, architecture judgment, and review outputs.

## File Structure

```txt
project/
+-- @@PLAN_FILE@@
+-- PLAN_M1.md
+-- PLAN_M2.md
+-- @@AGENTS_FILE@@
+-- @@LEARNINGS_FILE@@
+-- @@ARCHITECTURE_FILE@@
+-- orchestration/
    +-- README.md
```

## Workflow

### Planning A Milestone

```txt
Please read @@PLAN_FILE@@. I'd like you to make a plan for milestone M3, per the instructions in that file.
```

Codex researches the repo, asks only questions that cannot be answered from repo context, and writes a self-contained `PLAN_M3.md`.

### Implementing A Milestone

Start a fresh Codex instance and run:

```txt
Please read PLAN_M3.md. I'd like you to implement this plan, per the instructions in that file.
```

Codex implements, validates, updates the plan's `AI VALIDATION RESULTS`, and gives user validation suggestions.

### Better Engineering Milestones

Run better-engineering milestones regularly. They are dedicated quality passes for simplification, consolidation, refactoring, test hardening, and cleanup of stale `LEARNINGS.md` or `ARCHITECTURE.md` content.

## Claude Review

Claude review is stateless by design. Each review round should start from the current repo state and must not reference previous rounds.

Default review dimensions:

| Review | Focus |
| --- | --- |
| Correctness | Logic bugs, edge cases, broken assumptions |
| Style | Adherence to `@@AGENTS_FILE@@` conventions |
| Learnings | Compliance with `@@LEARNINGS_FILE@@` |
| Goals | Whether the work satisfies the milestone |
| KISS | Consolidation, refactoring, simplification opportunities |

Small or docs-only milestones may collapse these into one review.

## Design Principles

- Prune instructions per agent. Give each agent the files it needs, not every file in the repo.
- Prefer explicit prompts such as "Please read PLAN_M3.md" over hoping auto-discovery picks the right context.
- Never reference prior Claude review rounds in a new Claude prompt.
- `@@LEARNINGS_FILE@@` is durable agent memory.
- `@@ARCHITECTURE_FILE@@` is for stable finished-repo behavior and invariants.
- `PLAN_M{n}.md` is for milestone-specific notes.

## Learnings Decision Tree

| Type of learning | File |
| --- | --- |
| Durable engineering wisdom | `@@LEARNINGS_FILE@@` |
| Applies to this codebase in its finished state | `@@ARCHITECTURE_FILE@@` |
| Specific to one milestone | `PLAN_M{n}.md` |
