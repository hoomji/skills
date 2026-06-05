---
name: orchestration-bootstrap
description: Set up a file-driven Codex/Claude orchestration workflow in an existing repository by creating or updating PLAN.md, AGENTS.md, LEARNINGS.md, ARCHITECTURE.md, orchestration README docs, and milestone-plan templates. Use when a repo does not already have this workflow, when porting the unified-request AI orchestration structure to another codebase, or when refreshing an existing orchestration layer while preserving repo-specific guidance.
---

# Orchestration Bootstrap

Use this skill to install the full file-driven Codex/Claude orchestration workflow into an existing repository.

## Workflow

1. Inspect the target repository before running the script.
   - Read top-level `README*`, package/build config, test config, and any existing agent or architecture docs.
   - If root `PLAN.md`, `LEARNINGS.md`, or `ARCHITECTURE.md` exists, treat it as ordinary project documentation unless it has at least two orchestration markers.
   - Do not copy `unified-request`-specific backend, provider, endpoint, DTO, billing, or test details into another repo.
2. Run the bootstrap script from this skill:

   ```bash
   python .agents/skills/orchestration-bootstrap/scripts/bootstrap_orchestration.py \
     --repo /path/to/repo \
     --milestone-style auto
   ```

   Use `--force` only when the user explicitly wants existing workflow files refreshed. `--force` never overwrites a substantive root `AGENTS.md`.

3. Review the script output.
   - Missing workflow files are created directly.
   - Existing workflow files become `.candidate.md` files unless `--force` was passed.
   - Root `AGENTS.md` bridge is created only for new `ai/` workflows when no root `AGENTS.md` exists.
   - `BOOTSTRAP_REPORT.md` is written when candidates, warnings, validation failures, or force overwrites occur.
4. Improve generated repo-specific sections manually when needed.
   - Replace `TODO(repo)` only with facts discovered from the target repo or explicit user decisions.
   - Keep generic orchestration rules complete; `TODO(repo)` is not allowed in generic workflow sections.
   - Preserve the expanded generic guidance in generated `PLAN.md` and `AGENTS.md`: research-before-questions planning, decision-complete milestone plans, stateless Claude review loops, close-the-loop validation, better-engineering cleanup, generated-output discipline, and dirty-worktree safety.
5. Validate:

   ```bash
   python .agents/skills/orchestration-bootstrap/scripts/test_bootstrap_orchestration.py
   ```

## Important Rules

- New installs live under `ai/`.
- Root-level workflow output is used only when an existing root orchestration workflow is detected.
- Do not install partial/adoption/audit modes; this skill installs the full system.
- Claude review remains enabled by default through plain CLI output.
- Generated `LEARNINGS.md` must not contain `TODO(repo)`.
- Generated `PLAN.md`, `AGENTS.md`, and `ARCHITECTURE.md` must include non-placeholder project overviews.
