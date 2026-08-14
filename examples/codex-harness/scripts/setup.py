#!/usr/bin/env python3
"""Perform an idempotent, read-only setup check."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CONTEXT.md",
    "docs/harness/manifest.yaml",
    "docs/harness/tracer-workflow.md",
    "src/status_summary.py",
    "tests/test_status_summary.py",
)


def main() -> int:
    errors: list[str] = []
    if sys.version_info < (3, 11):
        errors.append(
            f"Python 3.11+ is required; found {sys.version_info.major}.{sys.version_info.minor}"
        )
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"required repository file is missing: {relative}")
    if errors:
        for error in errors:
            print(f"ERROR [setup] {error}")
        return 1
    print("PASS: setup prerequisites and required repository files are available")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
