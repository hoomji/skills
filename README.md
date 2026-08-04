# skills

Personal agent skills for Claude Code and Codex.

## Setup

```bash
git clone git@github.com:hoomji/skills.git ~/Documents/VS/Github/skills
cd ~/Documents/VS/Github/skills
chmod +x install.sh
./install.sh
```

This symlinks the skills into `~/.claude/skills/` (Claude Code) and `~/.agents/skills/` (Codex).

## Layout

```
skills/        ← agent skills (one directory per skill, each with a SKILL.md)
prompts/       ← reusable one-off prompts (plain markdown, no frontmatter)
teachings/     ← course material and learning records
```

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

| Skill                              | Description                                                                                      |
|------------------------------------|--------------------------------------------------------------------------------------------------|
| [sharpen](skills/sharpen/SKILL.md) | Rewrite a rough prompt into a sharper one and recommend how to run it (model, effort, workflow). |
| [writing-great-recurring](skills/writing-great-recurring/SKILL.md) | Stand up a recurring routine end to end — pick the surface, write the recurring prompt, wire it, verify the first firing. |
| [unblock-pr](skills/unblock-pr/SKILL.md) | Address every unresolved review thread on a PR and get its CI green. |
| [triaging-sandcastle-issues](skills/triaging-sandcastle-issues/SKILL.md) | Label unified-request GitHub issues ready-for-agent vs ready-for-human for the Sandcastle agent loop. |
| [salvage-sandcastle-run](skills/salvage-sandcastle-run/SKILL.md) | Close out a finished, killed, or stalled Sandcastle run — recover uncommitted work, reconcile rubber-stamped closures, get the branch green. |

## Matt Pocock skills

Vendored copies of skills from [mattpocock/skills](https://github.com/mattpocock/skills),
kept here for reference and local tweaks. They're already installed globally, so
`install.sh` does not link these.

| Skill                                                                | Description                                                                                     |
|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| [grill-with-docs](skills/grill-with-docs/SKILL.md)                   | A relentless interview to sharpen a plan or design, creating ADRs and a glossary as it goes.    |
| [grilling](skills/grilling/SKILL.md)                                 | Grill the user relentlessly about a plan or design to stress-test it before building.           |
| [domain-modeling](skills/domain-modeling/SKILL.md)                   | Build and sharpen a project's domain model — terminology, ubiquitous language, and ADRs.        |
| [to-spec](skills/to-spec/SKILL.md)                                   | Turn the current conversation into a spec and publish it to the project issue tracker.          |
| [to-tickets](skills/to-tickets/SKILL.md)                             | Break a plan, spec, or conversation into tracer-bullet tickets with blocking edges.             |
| [triage](skills/triage/SKILL.md)                                     | Move issues and external PRs through a state machine of triage roles into agent-ready briefs.   |
| [implement](skills/implement/SKILL.md)                               | Implement a piece of work based on a spec or set of tickets.                                     |
| [tdd](skills/tdd/SKILL.md)                                           | Test-driven development — red-green-refactor for features and bugfixes.                         |
| [code-review](skills/code-review/SKILL.md)                           | Review changes since a fixed point along two axes: repo Standards and originating Spec.         |
| [wayfinder](skills/wayfinder/SKILL.md)                               | Plan a large chunk of work as a shared map of investigation tickets, resolved one at a time.    |
| [resolving-merge-conflicts](skills/resolving-merge-conflicts/SKILL.md) | Resolve an in-progress git merge/rebase conflict.                                             |
| [setup-matt-pocock-skills](skills/setup-matt-pocock-skills/SKILL.md) | Configure a repo for the engineering skills — issue tracker, triage labels, domain doc layout.  |
