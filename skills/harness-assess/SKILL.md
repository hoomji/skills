---
name: harness-assess
description: Read-only harness assessment for software repositories. Use when the user asks whether a repo is agent-ready, wants a harness-engineering baseline, needs gaps ranked before setup, or wants evidence for improving AGENTS.md, commands, tests, observability, architecture enforcement, isolation, maintenance, or autonomy.
---

# Harness Assess

Produce an evidence-backed baseline without changing repository or external state. Read
[`../harness/references/contracts.md`](../harness/references/contracts.md) before scoring.

## 1. Establish scope and safety

Resolve the repository root, target branch, dirty state, and optional tracer workflow.
Treat the entire run as R0. Do not install dependencies, start services, mutate caches,
create files in the target repository, or call external write APIs. Commands advertised
as read-only still require inspection before execution.

Completion criterion: repository, current state, exclusions, and tracer workflow are
explicit; unresolved scope is labeled `unknown` rather than guessed.

## 2. Inventory evidence

Run:

```bash
python3 <skill-dir>/scripts/inventory.py <repository-root>
```

Use its JSON as a lead, not a verdict. Inspect the actual root guidance, build manifests,
task runner, CI, architecture/domain docs, representative tests, observability setup,
hooks, and worktree/background conventions. Follow pointers that materially affect a
plane. Exclude dependencies, generated trees, caches, unrelated worktrees, and secrets.

Completion criterion: every plane has inspected evidence or an explicit search boundary
and `unknown` result.

## 3. Test claims safely

Prefer static verification in the first pass. Run a repository command only when it is
clearly read-only in effect, already supported by the environment, and useful for
distinguishing two levels. Record timeout, missing credentials, missing services, or
environment failure separately from repository failure.

Completion criterion: each executed command has its outcome and interpretation; no
unexecuted command is represented as working evidence.

## 4. Score plane by plane

Assign the lowest fully evidenced level from 0–5 or `unknown`. For every plane provide:

- level and confidence;
- strongest evidence;
- present capability;
- concrete gap;
- impact on a real workflow;
- smallest next capability;
- risk class of that improvement.

Rank bottlenecks by impact on the tracer workflow, evidence strength, and cost to unlock.
Do not average the planes into one readiness score.

Completion criterion: all nine planes are scored independently and every factual claim
has a path, line, command result, or explicit uncertainty.

## 5. Report

Lead with the repository’s strongest capabilities and its top three blockers. Include:

1. scope and state;
2. plane matrix;
3. evidence-backed findings;
4. recommended adoption sequence;
5. safe first bootstrap boundary;
6. unknowns and actions needed to resolve them;
7. comparison to another assessed repository only when evidence is equivalent.

Return the report in chat unless the user explicitly requests a file. A file request may
write only to the destination the user authorizes; the assessment itself remains R0.

Completion criterion: a maintainer can accept or dispute every conclusion by following
the cited evidence.
