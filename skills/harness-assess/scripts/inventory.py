#!/usr/bin/env python3
"""Emit a bounded, read-only repository inventory as JSON."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    ".worktrees",
    ".sandcastle",
    ".seed-henry-sandcastle",
    ".yalc",
    "node_modules",
    "vendor",
    "worktrees",
    "dist",
    "build",
    "coverage",
    "generated",
    "__pycache__",
}

GUIDANCE_NAMES = {"AGENTS.md", "CLAUDE.md"}
BUILD_NAMES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "Taskfile.yml",
    "justfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}
ARCHITECTURE_NAMES = {"ARCHITECTURE.md", "CONTEXT.md", "DESIGN.md"}
HOOK_NAMES = {"hooks.json", ".pre-commit-config.yaml", ".pre-commit-config.yml"}
TEST_MARKERS = ("/test/", "/tests/", ".spec.", ".test.")
OBSERVABILITY_WORDS = (
    "observability",
    "grafana",
    "prometheus",
    "opentelemetry",
    "telemetry",
    "metrics",
)


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def bounded_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".cache"))
        current_path = Path(current)
        for name in sorted(names):
            path = current_path / name
            try:
                if path.is_file() and not path.is_symlink():
                    files.append(path)
            except OSError:
                continue
    return files


def git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def package_scripts(path: Path) -> dict[str, str]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    scripts = parsed.get("scripts", {})
    return {str(key): str(value) for key, value in scripts.items()} if isinstance(scripts, dict) else {}


def make_targets(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return sorted(set(re.findall(r"^([A-Za-z0-9_.-]+):(?:\s|$)", text, re.MULTILINE)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()

    requested = Path(args.repository).expanduser().resolve()
    if not requested.is_dir():
        parser.error(f"not a directory: {requested}")

    top = git(requested, "rev-parse", "--show-toplevel")
    root = Path(top).resolve() if top else requested
    files = bounded_files(root)
    rels = [relative(path, root) for path in files]

    guidance = [rel for rel in rels if Path(rel).name in GUIDANCE_NAMES]
    build_files = [rel for rel in rels if Path(rel).name in BUILD_NAMES]
    architecture = [
        rel
        for rel in rels
        if Path(rel).name in ARCHITECTURE_NAMES or rel.startswith("docs/adr/")
    ]
    workflows = [rel for rel in rels if rel.startswith(".github/workflows/")]
    hooks = [
        rel
        for rel in rels
        if Path(rel).name in HOOK_NAMES or rel.startswith(".husky/") or rel.startswith(".codex/hooks")
    ]
    tests = [rel for rel in rels if any(marker in f"/{rel.lower()}" for marker in TEST_MARKERS)]
    observability = [
        rel
        for rel in rels
        if any(word in Path(rel).name.lower() for word in OBSERVABILITY_WORDS)
        or any(part.lower() in {"grafana", "observability", "telemetry"} for part in Path(rel).parts)
    ]

    packages: dict[str, dict[str, str]] = {}
    makes: dict[str, list[str]] = {}
    for path in files:
        rel = relative(path, root)
        if path.name == "package.json" and rel.count("/") <= 2:
            packages[rel] = package_scripts(path)
        if path.name == "Makefile" and rel.count("/") <= 2:
            makes[rel] = make_targets(path)

    language_counts: dict[str, int] = {}
    for path in files:
        suffix = path.suffix.lower() or "[none]"
        language_counts[suffix] = language_counts.get(suffix, 0) + 1

    status = git(root, "status", "--short")
    output: dict[str, Any] = {
        "repository": str(root),
        "git": {
            "branch": git(root, "branch", "--show-current"),
            "head": git(root, "rev-parse", "HEAD"),
            "dirty_entries": status.splitlines() if status else [],
        },
        "counts": {
            "files_scanned": len(files),
            "tests": len(tests),
            "architecture_and_domain_docs": len(architecture),
            "ci_workflows": len(workflows),
        },
        "guidance": guidance,
        "build_files": build_files,
        "package_scripts": packages,
        "make_targets": makes,
        "architecture_and_domain_docs": architecture[:100],
        "ci_workflows": workflows,
        "hooks": hooks,
        "observability_candidates": observability[:100],
        "test_samples": tests[:100],
        "file_extensions": dict(sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))[:20]),
        "limits": {
            "excluded_directories": sorted(EXCLUDED_DIRS),
            "sample_cap": 100,
            "commands_executed": ["git rev-parse", "git branch --show-current", "git status --short"],
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
