"""CLI adapter that emits structured runtime evidence."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Iterable, Mapping

from src.status_summary import parse_check_results, summarize


def task_namespace(root: Path) -> str:
    try:
        worktree = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        worktree = str(root.resolve())
    digest = hashlib.sha256(worktree.encode("utf-8")).hexdigest()[:10]
    return f"codex-harness-{digest}"


def run(
    items: Iterable[Mapping[str, object]], root: Path | None = None
) -> dict[str, object]:
    repository = root or Path.cwd()
    summary = summarize(parse_check_results(items))
    return {
        "event": "status_summary.completed",
        "task_namespace": task_namespace(repository),
        "summary": summary.to_dict(),
    }


def main() -> int:
    fixture = [
        {"name": "repository-map", "state": "pass"},
        {"name": "runtime-observability", "state": "pass"},
        {"name": "production-release", "state": "unknown"},
    ]
    print(json.dumps(run(fixture), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
