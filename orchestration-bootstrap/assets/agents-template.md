# Guidance For Project Agents

@@PROJECT_OVERVIEW@@

Replace or extend the overview above with concrete repo facts as soon as they are discovered: what the system does, who consumes it, what external systems it depends on, which contracts are public, and where the main implementation areas live.

## Orchestration Files

- `AGENTS.md`: how agents should behave and how to develop in this repo. In new `ai/` installs, the root `AGENTS.md` is only a bridge to `ai/AGENTS.md`.
- `PLAN.md`: high-level milestone planning guidance; read it for milestone-style work.
- `LEARNINGS.md`: if present, read before implementation; durable lessons learned through previous mistakes.
- `ARCHITECTURE.md`: if present, read before architecture-sensitive implementation; stable structure, data flow, and invariants.
- `README*`: local setup, dependencies, test commands, runtime notes, and operational context.
- Package/build config: source of truth for build, test, lint, formatting, docs, generation, migrations, and runtime scripts.

## Cross-Cutting Issues

@@REPO_SPECIFIC_CROSS_CUTTING_ISSUES@@

- Public/user-facing contracts matter. Route paths, CLI flags, schemas, response shapes, persisted records, generated docs, and integration payloads are contracts unless explicitly internal.
- Keep behavior deterministic and observable. Important flows should be traceable from entrypoint through domain logic, adapters, persistence, generated outputs, and logs/errors.
- Errors must be consistent and actionable. Preserve enough request/job/debug context to diagnose failures without leaking secrets.
- External dependencies are part of the product. Network failures, rate limits, stale data, missing credentials, retries, timeouts, and partial failures should be planned and tested where relevant.
- Generated and synced files are outputs, not playgrounds. Change the source of truth first, run the proper generator/sync command, and review generated diffs carefully.
- Secrets must stay secret. Do not log API keys, credentials, tokens, raw auth headers/cookies, private keys, or request bodies that may contain sensitive data.

## Codebase Style And Guidelines

Coding style: all code must be clean, documented, and minimal.

- Typecheck/build/lint cleanly using the repo's primary commands.
- Keep It Simple Stupid (KISS) by reducing concept count. Strive for fewer functions, fewer helpers, and fewer invented abstractions. If a helper is only called by a single callsite, prefer to inline it unless the helper names an important invariant.
- At the same time, Don't Repeat Yourself (DRY).
- There is a tension between KISS and DRY. If avoiding repetition requires a heavy abstraction, think harder about whether the repeated work can be eliminated or represented by existing repo patterns.
- Prefer existing repo patterns over inventing a new structure.
- Prefer explicit validation/schemas/types over ad hoc parsing in service code.
- Prefer specific code when behavior is genuinely specific. Do not flatten important differences into a shared helper just because the shapes look similar.
- If some code looks heavyweight, perhaps with lots of conditionals, think harder for a more elegant way of achieving it.
- Prefer functional-style code where values are immutable where practical and branching is limited. Do not force cleverness.
- Code should have comments and docstrings where they clarify invariants, side effects, dependency boundaries, or non-obvious behavior. Avoid comments that restate obvious code.
- Name side-effecting functions to expose the side effect. A function named `load()` implies it returns data. If its real purpose is to populate state, publish data, mutate persistent state, or emit logs, make that visible in the name.
- Never discard async/background failures casually. Await async work where applicable. If fire-and-forget is truly needed, the function itself must handle all errors internally and return a clear result or log/audit outcome.
- Do not hand-edit generated/synced output unless the generator or sync source is broken and the user has explicitly accepted a temporary repair. The clean fix is almost always in the generator, template, source mapping, or source data.
- Keep tests, docs, architecture notes, and public contracts in sync. A behavior change without test and documentation consideration is probably incomplete.

The user is adamant about clean engineering. What they look for:

- Learnings must be stored in root `LEARNINGS.md`, `ai/LEARNINGS.md`, or another repo-agreed learning file if one exists.
- Invariants are the best way to document code and architecture. Useful invariants include ownership boundaries, source-of-truth rules, cache/persistence key dimensions, validation rules, generated-file rules, error classification, auth boundaries, and dependency failure behavior.
- Address prerequisites cleanly, do not hack around them. If a request exposes a broken abstraction, stale generated artifact, missing validation, weak auth boundary, poor error model, or brittle persistence hook, fix or plan that prerequisite directly rather than sneaking around it.
- Keep blast radius honest. Public endpoints, schemas, persistence, generated artifacts, auth, billing/accounting, and error handling are shared surfaces; touch them carefully and validate accordingly.
- Avoid unrelated churn. Formatting broad modules or generated files while making a tiny behavioral change makes review worse.

Likely generated surfaces discovered during bootstrap:

@@GENERATED_SURFACES@@

## Agent Peer Review

Agents can and should get opinions from other agents:

- Use Claude CLI review when explicitly required by the user or plan, or when there is a weighty architecture/routing/public-contract decision.
- A great prompt says what changed, why it changed, what files matter, what risks to examine, and what result you want. Good prompts also give Claude the goal, relevant context, why the review matters, and what outcome you hope to achieve.
- A good review invocation can be as simple as: "Please read instructions in `/absolute/path/to/claude.review.input.md` and write your answers in markdown to `/absolute/path/to/claude.review.output.md`."
- The other agent can read files and do repo research. Expect thoughtful review to take time, including 10-15 minutes with little or no visible output.
- You do not have to follow every suggestion, but if you reject feedback, record the reasoning in the plan, code comment, or final explanation where appropriate.

## Agent Interaction Rules With Human

- Be proactive. If the user asks for an edit or fix, implement it unless they explicitly ask only for advice.
- Ask questions only when repo research cannot resolve a meaningful ambiguity. When asking, provide concrete options and a recommended default.
- Keep the user informed during longer work with short progress updates.
- Do not use git unless the user asks for git work, review context truly requires git, or publishing. If git is needed, keep it narrow and do not revert user changes.
- Respect dirty worktrees. Never overwrite or revert changes you did not make unless the user explicitly asks. Work with relevant existing changes and ignore unrelated dirty files.
- If a command fails because sandboxing or restricted network blocks required work, request escalation with a clear justification.
- When human help is truly required, give an exact command or action, what they should expect to see, and when they can hand control back.
- Automatically add narrow, durable user corrections to `LEARNINGS.md`; ask first for broad or policy-changing lessons.

## Second Opinion By Claude

You will at times be asked to use Claude to get a second opinion.

Invoke Claude by preparing a self-contained prompt file in the repo root and shelling out to the Claude CLI.

For this repo, `{DIRECTORY}` is `@@REPO_ROOT@@`. Prepare the prompt as `{DIRECTORY}/claude.{id}.input.md`, where `{id}` is a short stable label such as `m1_plan`, `m1_review_correctness`, or `m1_review_style`.

Run Claude from `{DIRECTORY}`:

```bash
cd @@REPO_ROOT@@ && claude \
  -p "Please respond to @@REPO_ROOT@@/claude.{id}.input.md" \
  > @@REPO_ROOT@@/claude.{id}.output.md
```

Claude should be run from the repo root because it can only edit and inspect files under that working directory. The prompt file may mention other filenames, but every referenced path must be absolute.

If the Claude CLI is unavailable and Claude review is required, use the human as the execution path instead of skipping review. Write the same self-contained prompt file, choose an output file path, and ask the user to run Claude with a copy-pasteable prompt in triple backticks:

```text
Please read @@REPO_ROOT@@/claude.{id}.input.md and write your response in markdown to @@REPO_ROOT@@/claude.{id}.output.md
```

After the user says Claude is done, read the output file and continue the same review loop. If neither CLI nor human-mediated Claude review can be completed, stop and report the blocker.

### Guidelines

- Claude does best when given the goal, relevant context, what you want from it, why you want it, and what outcome you hope to achieve.
- You will often be asked to invoke Claude in rounds: invoke Claude, act on its feedback, invoke Claude again, and repeat until there is nothing meaningful left to address.
- Do not reference previous rounds when invoking Claude. Claude performs best when each round starts from scratch so it can re-examine the full request from first principles.
- Treat each Claude round as independent. This is desirable and helps produce a cleaner review.
- Avoid prompts like "please review the updated files" because each round should review the current state of the files and repository on disk from a complete prompt.
- Claude can do its own research in the codebase to find context. You can expect this to take around 5-10 minutes. You may also provide additional context yourself in the input file.
- In `claude.{id}.input.md`, you may mention other filenames, but you must use absolute paths. Claude may read them if it decides they are relevant.
- Run Claude from `{DIRECTORY}`. That lets it inspect this repo and avoids attempts to edit outside the repo.
- Use Claude whenever explicitly instructed, such as for planning or code review. Also loop Claude in proactively whenever there is a weighty or high-impact decision to make.
- You do not have to follow all of Claude's suggestions. However, if you disagree with its findings, you should do another round and explicitly justify your reasoning so Claude can reconsider from that perspective.
- Claude will read `AGENTS.md` and can do its own research. If there are specific files you want it to read, say so explicitly using absolute paths.
- Claude often takes a long time to produce a thoughtful response. Expect up to 10-15 minutes before it finishes. You can inspect progress in `claude.{id}.output.md` while the command runs.
- If you have been told to do Claude, it is mandatory. If it fails for some reason, try again. If the CLI is unavailable, ask the user to run Claude on your behalf using the prompt-file workflow above. If it still cannot be completed, stop, abandon the implementation path, and report the issue to the user. Never proceed without Claude when it is required.

Default review dimensions:

- Correctness
- Style and repo conventions
- Learnings compliance
- Milestone completeness
- KISS/refactoring opportunities

Small or docs-only milestones may use one collapsed review.

### Close The Loop, Autonomy

The agent is responsible for validating every change at the right depth. The human should not have to prompt for obvious testing.

- Test before presenting to the human: if you have made code changes, run appropriate checks before calling the work done. For documentation-only changes, a structural/readability pass is enough.
- Match validation to risk: docs-only edits do not need the full test suite. API/schema/domain/persistence/auth/error/generated-output changes do.
- Regenerate or sync before validating generated surfaces: if generated docs, schemas, migrations, generated assets, or synced external definitions should change, run the appropriate command before checking behavior.
- Check public API impacts: route paths, CLI flags, request/response fields, persistence schema, generated docs, and error codes require extra scrutiny.
- Proactively gather evidence: endpoint calls, CLI runs, targeted test results, generated diffs, log snippets, persisted rows, audit entries, and error bodies are stronger than vague claims.
- Do not wait unnecessarily: if a background process might already be done, check before sleeping. Poll deliberately.
- Solve your own obstacles: if testing requires env setup, a local dependency, targeted mocks, or a narrower test command, try the obvious repo-supported path first. Ask only when the blocker truly requires human secrets or external access.

## How To Develop Within The Codebase

- Build/test/deploy commands live in the dedicated `Testing` and `Build And Deploy` sections below. Keep those sections as the source of truth for command usage.
@@REPO_SPECIFIC_DEVELOPMENT_GUIDE@@
- Start at the public entrypoint for the behavior you are changing, then follow the flow through schemas/types, domain logic, adapters, persistence, and output contracts. Do not jump straight to low-level code and guess the public contract.
- Prefer targeted `rg` searches over browsing manually. Search by route path, command name, schema/model class, error text, storage key/table, generated file name, and public contract field.

## Testing

@@REPO_SPECIFIC_TESTING_GUIDE@@

Target validation by change type:

- API/CLI/UI/schema changes: targeted route/command/component/schema tests, invalid input tests, compatibility checks, and docs updates when behavior changes.
- Domain logic changes: focused unit tests with representative fixtures, edge cases, and deterministic output assertions.
- Persistence/migration changes: migration/schema review, compatibility/backfill notes, and targeted persistence tests.
- External integration changes: mocked success/error responses, credential/config failure tests, timeout/retry behavior, and live validation only when explicitly configured.
- Generated/synced output changes: run the generator/sync command, inspect the diff, and test the surface that consumes the generated output.
- Error-handling changes: tests for status/code/body, retryability where applicable, debug context, and no secret leakage.
- Docs-only changes: structural markdown review and enough repo-context checking to avoid stale instructions.

### Integration Test Workflow

Integration tests may need real or mocked environment configuration. When running them:

1. Identify the narrowest integration test that covers the behavior before running a broad suite.
2. Use a timeout for commands that can hang on external services, databases, queues, browsers, provider credentials, or auth setup.
3. If failures all share the same setup cause, stop and diagnose setup rather than waiting for the full suite.
4. Capture the relevant failure lines, request/command path, dependency, and env assumption in the final answer.
5. When a test requires secrets, live external services, or unavailable local infrastructure, document that blocker and run the closest meaningful unit-level validation instead.

## Debugging Guide

@@REPO_SPECIFIC_DEBUGGING_GUIDE@@

Common symptoms and where to look:

- App or command does not start: main entrypoint, dependency wiring, env/config, package/build config, and dependency versions.
- Route/command returns validation errors: schemas/types, request parsing, validation middleware, and query/body/flag handling.
- Auth or project/user context missing: auth middleware, decorators/dependencies, session/JWT/cookie/header handling, and local bypass config.
- External dependency failure: adapter code, credentials, network settings, retries/timeouts, and provider-specific error mapping.
- Wrong data selected or returned: source query, domain selection logic, cache/persistence key dimensions, generated mappings, and contract tests.
- Generated output stale: source-of-truth files, generator/sync scripts, generated artifacts, and docs/tests that consume them.
- Logs missing or unsafe: request/job context, logging middleware/hooks, audit/event services, and redaction rules.

## Build And Deploy

@@REPO_SPECIFIC_COMMANDS@@
