#!/usr/bin/env python3
"""Install the file-driven orchestration workflow into a repository."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = SKILL_DIR / "assets"
ROOT_BRIDGE = "# Agent Guidance\n\nRead `ai/AGENTS.md` for project agent instructions.\n"
GITIGNORE_BLOCK = "# Agent review artifacts\nclaude.*.input.md\nclaude.*.output.md\n"
PLACEHOLDER_RE = re.compile(r"@@[A-Z0-9_]+@@")
TODO = "TODO(repo)"
ROOT_MARKERS = (
    "HOW TO PLAN A MILESTONE",
    "HOW TO EXECUTE A MILESTONE",
    "PLAN_M{n}.md",
    "PLAN-M{n}.md",
    "LEARNINGS.md is",
    "ARCHITECTURE.md",
    "stateless Claude",
)


@dataclass
class OperationState:
    created: list[Path] = field(default_factory=list)
    candidates: list[Path] = field(default_factory=list)
    overwritten: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    gitignore_updated: bool = False
    report_path: Path | None = None


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def asset(name: str) -> str:
    return (ASSETS_DIR / name).read_text(encoding="utf-8")


def render(template: str, values: dict[str, str]) -> str:
    text = template
    for key, value in values.items():
        text = text.replace(f"@@{key}@@", value)
    return text


def has_root_markers(path: Path) -> bool:
    text = read_text(path)
    if not text:
        return False
    hits = sum(1 for marker in ROOT_MARKERS if marker in text)
    return hits >= 2


def detect_root_workflow(repo: Path) -> bool:
    candidates = [repo / "PLAN.md", repo / "AGENTS.md", repo / "LEARNINGS.md", repo / "ARCHITECTURE.md"]
    return any(has_root_markers(path) for path in candidates)


def detect_milestone_style(repo: Path, workflow_root: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    search_roots = [workflow_root, repo]
    for root in search_roots:
        if any(root.glob("PLAN-M*.md")):
            return "hyphen"
        if any(root.glob("PLAN_M*.md")):
            return "underscore"
    return "underscore"


def discover_repo(repo: Path, state: OperationState) -> dict[str, str]:
    root_markers = [
        "README.md",
        "README",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "go.mod",
        "Cargo.toml",
        ".git",
    ]
    if not any((repo / marker).exists() for marker in root_markers):
        state.warnings.append("No obvious repo root markers found; treating --repo as the root.")

    package_json = repo / "package.json"
    pyproject = repo / "pyproject.toml"
    makefile = repo / "Makefile"
    go_mod = repo / "go.mod"
    cargo = repo / "Cargo.toml"
    readmes = sorted(repo.glob("README*"))

    if package_json.exists():
        overview = "This repository appears to be a Node/TypeScript or JavaScript project based on `package.json`."
        commands = commands_from_package_json(package_json)
    elif pyproject.exists():
        overview = "This repository appears to be a Python project based on `pyproject.toml`."
        commands = commands_from_makefile(makefile) if makefile.exists() else "- Install/test commands should be confirmed from `pyproject.toml` and project docs."
    elif go_mod.exists():
        overview = "This repository appears to be a Go project based on `go.mod`."
        commands = "- Build/test commands should be confirmed from `go.mod` and project docs."
    elif cargo.exists():
        overview = "This repository appears to be a Rust project based on `Cargo.toml`."
        commands = "- Build/test commands should be confirmed from `Cargo.toml` and project docs."
    elif readmes:
        overview = f"This repository has `{readmes[0].name}` but no common package manifest was identified during bootstrap."
        commands = "- Build/test commands should be confirmed from the README and project files."
    else:
        overview = "This repository did not expose a clear framework during bootstrap. Fill in the system purpose after deeper review."
        commands = "- TODO(repo): Document build and test commands after identifying the project stack."

    generated = detect_generated_surfaces(repo)
    return {
        "PROJECT_OVERVIEW": overview,
        "DISCOVERED_SYSTEM_OVERVIEW": overview,
        "DISCOVERED_CORE_FLOW": "TODO(repo): Document the primary request, data, UI, or job flow after inspecting the main entrypoints.",
        "INVARIANT_1": "TODO(repo): Document a stable invariant after deeper architecture review.",
        "INVARIANT_2": "TODO(repo): Document a second stable invariant after deeper architecture review.",
        "LOCAL_RUN_ASSUMPTIONS": "TODO(repo): Document local run assumptions.",
        "TESTING_ASSUMPTIONS": "TODO(repo): Document testing assumptions.",
        "GENERATED_FILE_ASSUMPTIONS": generated,
        "GENERATED_SURFACES": generated,
        "REPO_SPECIFIC_CROSS_CUTTING_ISSUES": "- TODO(repo): Document cross-cutting correctness, security, performance, data, or UX risks.",
        "REPO_SPECIFIC_DEVELOPMENT_GUIDE": "- Start from the README, package/build config, and main entrypoints before changing behavior.",
        "REPO_SPECIFIC_TESTING_GUIDE": commands,
        "REPO_SPECIFIC_DEBUGGING_GUIDE": "- TODO(repo): Document common failure modes and where to inspect them.",
        "REPO_SPECIFIC_COMMANDS": commands,
        "REPO_SPECIFIC_M1": "Establish local development infrastructure: install dependencies, run the app or library locally, identify primary build/typecheck/test commands, and document local assumptions.\n\nValidate: run the primary build/typecheck command and one targeted test or smoke command.",
        "REPO_SPECIFIC_M2": "Document architecture and core flow: identify main entrypoints, important modules, data/request flow, generated files, external services, and stable invariants.\n\nValidate: update `ARCHITECTURE.md` with discovered facts and confirm command references match repo files.",
        "REPO_SPECIFIC_M3": "Plan the first user-selected feature or integration after product intent is clear.\n\nValidate: create a decision-complete milestone plan with AI and user validation steps.",
    }


def commands_from_package_json(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "- TODO(repo): `package.json` exists but could not be parsed; confirm build/test commands manually."
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict) or not scripts:
        return "- TODO(repo): `package.json` has no scripts; confirm build/test commands manually."
    lines = []
    for name in ("build", "typecheck", "test", "lint", "dev", "start"):
        if name in scripts:
            lines.append(f"- `{package_runner(path.parent)} {name}`")
    if not lines:
        sample = sorted(scripts)[:5]
        lines = [f"- `{package_runner(path.parent)} {name}`" for name in sample]
    return "\n".join(lines)


def commands_from_makefile(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    targets: list[str] = []
    for name in ("setup", "test", "lint", "lint-imports", "format", "fix", "run", "run-worker", "run-beat", "docker-dev", "docker-build"):
        if re.search(rf"^{re.escape(name)}\s*:", text, re.MULTILINE):
            targets.append(f"- `make {name}`")
    if not targets:
        return "- Build/test commands should be confirmed from `Makefile`, `pyproject.toml`, and project docs."
    return "\n".join(targets)


def package_runner(repo: Path) -> str:
    if (repo / "yarn.lock").exists():
        return "yarn"
    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm"
    return "npm run"


def detect_generated_surfaces(repo: Path) -> str:
    names = []
    for dirname in ("generated", "dist", "build", "coverage"):
        if (repo / dirname).exists():
            names.append(f"- `{dirname}/` appears to be generated or build output.")
    if (repo / "app" / "admin" / "static" / "css" / "app.css.in").exists():
        names.append("- `app/admin/static/css/app.css` may be generated from `app/admin/static/css/app.css.in`.")
    if (repo / "bigquery" / "scheduled_queries").exists():
        names.append("- `bigquery/scheduled_queries/` may be synced with external scheduled-query definitions.")
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        if isinstance(scripts, dict):
            for name in sorted(scripts):
                lower = name.lower()
                if any(token in lower for token in ("generate", "gen", "docs", "openapi", "schema")):
                    names.append(f"- Package script `{name}` may generate files.")
    if not names:
        return "- No likely generated surfaces were identified during bootstrap. Revisit this after deeper repo review."
    return "\n".join(names)


def generic_execution_workflow() -> str:
    return "\n".join(
        [
            "If the user asks you to execute on a plan, these are the steps to take.",
            "",
            "1. Implement the plan",
            "   - Check your work with autonomous validation and testing.",
            "   - The implementation should require minimal user interaction, preferably none.",
            "   - Once complete, fill in the \"AI VALIDATION RESULTS\" section at the bottom of the plan showing how you validated it and what the results were.",
            "   - If you discover better engineering work, either do it when tightly scoped or record it as backlog when it deserves its own milestone.",
            "2. Perform your testing and validation",
            "   - Update the \"AI VALIDATION RESULTS\" section of your `PLAN_M{n}.md` file.",
            "   - For most changes, run the repo's primary typecheck/build command and targeted tests relevant to the changed module.",
            "   - Run lint/static checks when style, typing, or architecture-boundary risk is relevant.",
            "   - Run generated-output, docs, schema, migration, or sync commands when public API, generated metadata, schemas, docs, migrations, or generated assets changed.",
            "3. Review your own code. Also, use Claude to review your work when required.",
            "   - Invoke Claude exactly as described in `AGENTS.md`: write a self-contained prompt file in the repo root, run Claude from the repo root, and write output to `claude.{id}.output.md`.",
            "   - Provide context: your plan document `PLAN_M{n}.md` and the files/functions changed. Ask Claude to review validation steps as well.",
            "   - If Claude found no blockers or problems, proceed. Do static checking. If you need fixes, run static checks again.",
            "   - If Claude cannot run for whatever reason, try again. If it still cannot be completed, stop and report the issue to the user.",
            "   - Keep iterating with Claude until you no longer make changes. If you take more than 10 rounds, stop and let the user know.",
            "   - For every suggestion from Claude, evaluate whether it will improve the code. If so, modify the code. If not, pre-emptively defend in comments, tests, or plan notes why not.",
            "   - Do not reference previous rounds when you invoke Claude. Each round must start from scratch and ask Claude to review the current state of the repo.",
            "4. After implementation, do a better-engineering phase",
            "   - Clean up `LEARNINGS.md` and `ARCHITECTURE.md`. If any information just restates other files, delete it. If it belongs better elsewhere, move it.",
            "   - Review correctness, style, learnings compliance, milestone completeness, and KISS/refactoring opportunities.",
            "   - If you make changes, run static checking and targeted tests again.",
            "   - If you decide not to do better engineering yourself, write the needed follow-up in the \"BETTER ENGINEERING INSIGHTS + BACKLOG ADDITIONS\" section of the plan.",
            "   - Tell the user how you handled code cleanup. The user is passionate about clean code and wants to know how quality improved.",
            "5. Upon completion, ask for user review. Tell the user what to test, what commands to use, what calls/UI flows to try, and what behavior to look for.",
        ]
    )


def build_files(repo: Path, workflow_root: Path, root_workflow: bool, style: str, values: dict[str, str]) -> dict[Path, str]:
    plan_file = "PLAN.md"
    agents_file = "AGENTS.md"
    learnings_file = "LEARNINGS.md"
    architecture_file = "ARCHITECTURE.md"
    values = dict(values)
    values.update(
        {
            "REPO_ROOT": repo.as_posix(),
            "PLAN_FILE": plan_file,
            "AGENTS_FILE": agents_file,
            "LEARNINGS_FILE": learnings_file,
            "ARCHITECTURE_FILE": architecture_file,
            "GENERIC_EXECUTION_WORKFLOW": generic_execution_workflow(),
            "MILESTONE_TEMPLATE": asset("milestone-template.md").rstrip(),
        }
    )
    files = {
        workflow_root / plan_file: render(asset("plan-template.md"), values),
        workflow_root / agents_file: render(asset("agents-template.md"), values),
        workflow_root / learnings_file: asset("learnings-template.md"),
        workflow_root / architecture_file: render(asset("architecture-template.md"), values),
        workflow_root / "orchestration" / "README.md": render(asset("orchestration-readme.md"), values),
    }
    if not root_workflow:
        files[repo / "AGENTS.md"] = ROOT_BRIDGE
    return files


def candidate_path(path: Path) -> Path:
    return path.with_name(path.name + ".candidate.md")


def is_substantive_root_agents(path: Path) -> bool:
    text = read_text(path).strip()
    return bool(text and text != ROOT_BRIDGE.strip())


def write_files(repo: Path, files: dict[Path, str], force: bool, state: OperationState) -> None:
    for path, content in files.items():
        is_root_agents = path == repo / "AGENTS.md"
        if path.exists():
            if is_root_agents and is_substantive_root_agents(path):
                target = candidate_path(path)
                target.write_text(content, encoding="utf-8")
                state.candidates.append(target)
                continue
            if force:
                path.write_text(content, encoding="utf-8")
                state.overwritten.append(path)
            else:
                target = candidate_path(path)
                target.write_text(content, encoding="utf-8")
                state.candidates.append(target)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        state.created.append(path)


def update_gitignore(repo: Path, state: OperationState) -> None:
    gitignore = repo / ".gitignore"
    if not gitignore.exists() and not (repo / ".git").exists():
        return
    existing = read_text(gitignore)
    needed = [line for line in ("claude.*.input.md", "claude.*.output.md") if line not in existing]
    if not needed:
        return
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    block = GITIGNORE_BLOCK
    if "# Agent review artifacts" in existing:
        block = "\n".join(needed) + "\n"
    gitignore.write_text(existing + prefix + block, encoding="utf-8")
    state.gitignore_updated = True


def validate(repo: Path, workflow_root: Path, root_workflow: bool, state: OperationState) -> None:
    paths = [
        p
        for p in workflow_root.rglob("*.md")
        if ".candidate.md" not in p.name and not candidate_path(p).exists()
    ]
    paths.extend(state.candidates)
    if not root_workflow and (repo / "AGENTS.md").exists():
        bridge_candidate = candidate_path(repo / "AGENTS.md")
        paths.append(bridge_candidate if bridge_candidate.exists() else repo / "AGENTS.md")
    for path in paths:
        text = read_text(path)
        placeholders = PLACEHOLDER_RE.findall(text)
        if placeholders:
            state.validation_errors.append(f"{rel(path, repo)} has unresolved placeholders: {', '.join(sorted(set(placeholders)))}")
        if TODO in text and not todo_allowed(path, text, workflow_root, repo):
            state.validation_errors.append(f"{rel(path, repo)} has illegal TODO(repo) placement")
    for required in ("PLAN.md", "AGENTS.md", "LEARNINGS.md", "ARCHITECTURE.md", "orchestration/README.md"):
        if not (workflow_root / required).exists() and not candidate_path(workflow_root / required).exists():
            state.validation_errors.append(f"Missing required workflow file: {rel(workflow_root / required, repo)}")
    check_non_placeholder_overview(preferred_validation_path(workflow_root / "PLAN.md"), "Project Milestones", state, repo)
    check_non_placeholder_overview(preferred_validation_path(workflow_root / "AGENTS.md"), "Guidance", state, repo)
    architecture = preferred_validation_path(workflow_root / "ARCHITECTURE.md")
    if architecture.exists() and "## System Overview\n\nTODO(repo)" in read_text(architecture):
        state.validation_errors.append(f"{rel(architecture, repo)} has placeholder System Overview")


def preferred_validation_path(path: Path) -> Path:
    candidate = candidate_path(path)
    return candidate if candidate.exists() else path


def todo_allowed(path: Path, text: str, workflow_root: Path, repo: Path) -> bool:
    if path == workflow_root / "ARCHITECTURE.md":
        return True
    if path == workflow_root / "PLAN.md":
        bad_sections = ("## HOW TO PLAN A MILESTONE", "## HOW TO EXECUTE A MILESTONE")
        for section in bad_sections:
            part = section_text(text, section)
            if TODO in part:
                return False
        return True
    if path == workflow_root / "AGENTS.md":
        generic_sections = ("## Orchestration Files", "## Codebase Style And Guidelines", "## Agent Peer Review", "## Agent Interaction Rules With Human", "## Second Opinion By Claude")
        for section in generic_sections:
            if TODO in section_text(text, section):
                return False
        return True
    return False


def section_text(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    in_fence = False
    start_index: int | None = None
    end_index = len(lines)
    for index, line in enumerate(lines):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        stripped = line.rstrip("\n")
        if in_fence:
            continue
        if start_index is None:
            if stripped == heading:
                start_index = index
            continue
        if line.startswith("## "):
            end_index = index
            break
    if start_index is None:
        return ""
    return "".join(lines[start_index:end_index])


def check_non_placeholder_overview(path: Path, label: str, state: OperationState, repo: Path) -> None:
    if not path.exists():
        return
    text = read_text(path)
    body = text.split("\n\n", 1)[1] if "\n\n" in text else ""
    first = body.strip().splitlines()[0] if body.strip() else ""
    if not first or TODO in first or PLACEHOLDER_RE.search(first):
        state.validation_errors.append(f"{rel(path, repo)} lacks non-placeholder {label} overview")


def write_report(repo: Path, report_path: Path, state: OperationState) -> None:
    lines = [
        "# Bootstrap Report",
        "",
        "## Summary",
        "",
        f"- Created: {len(state.created)}",
        f"- Candidates: {len(state.candidates)}",
        f"- Overwritten: {len(state.overwritten)}",
        f"- Gitignore updated: {'yes' if state.gitignore_updated else 'no'}",
        f"- Warnings: {len(state.warnings)}",
        f"- Validation errors: {len(state.validation_errors)}",
    ]
    for title, paths in (("Created", state.created), ("Candidates", state.candidates), ("Overwritten", state.overwritten)):
        if paths:
            lines += ["", f"## {title}", ""]
            lines += [f"- `{rel(path, repo)}`" for path in paths]
    if state.warnings:
        lines += ["", "## Warnings", ""]
        lines += [f"- {warning}" for warning in state.warnings]
    if state.validation_errors:
        lines += ["", "## Validation Errors", ""]
        lines += [f"- {error}" for error in state.validation_errors]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    state.report_path = report_path


def print_summary(repo: Path, state: OperationState) -> None:
    print(f"Created: {len(state.created)}")
    print(f"Candidates: {len(state.candidates)}")
    print(f"Overwritten: {len(state.overwritten)}")
    print(f"Gitignore updated: {'yes' if state.gitignore_updated else 'no'}")
    print(f"Warnings: {len(state.warnings)}")
    print(f"Validation errors: {len(state.validation_errors)}")
    print(f"Report: {rel(state.report_path, repo) if state.report_path else 'none'}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Target repository root")
    parser.add_argument("--force", action="store_true", help="Overwrite workflow files in the detected workflow location")
    parser.add_argument("--milestone-style", choices=("auto", "underscore", "hyphen"), default="auto")
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo = Path(args.repo).expanduser().resolve()
    state = OperationState()
    root_workflow = detect_root_workflow(repo)
    workflow_root = repo if root_workflow else repo / "ai"
    style = detect_milestone_style(repo, workflow_root, args.milestone_style)
    values = discover_repo(repo, state)
    values["MILESTONE_STYLE"] = style

    files = build_files(repo, workflow_root, root_workflow, style, values)
    write_files(repo, files, args.force, state)
    update_gitignore(repo, state)

    validate(repo, workflow_root, root_workflow, state)

    report_needed = bool(state.candidates or state.overwritten or state.warnings or state.validation_errors)
    if report_needed:
        report_path = workflow_root / "orchestration" / "BOOTSTRAP_REPORT.md"
        write_report(repo, report_path, state)
    print_summary(repo, state)
    return 1 if state.validation_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
