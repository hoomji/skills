#!/usr/bin/env python3
"""Run dependency-free static and structural checks."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOTS = (ROOT / "src", ROOT / "scripts", ROOT / "tests")
REQUIRED = (
    "AGENTS.md",
    "ARCHITECTURE.md",
    "CONTEXT.md",
    "docs/product-specs/index.md",
    "docs/design-docs/index.md",
    "docs/adr/index.md",
    "docs/harness/manifest.yaml",
    "docs/harness/tracer-workflow.md",
    "docs/harness/governance.md",
    "docs/harness/learning-ledger.md",
)


def python_files() -> list[Path]:
    return sorted(path for root in PYTHON_ROOTS for path in root.rglob("*.py"))


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"required harness artifact is missing: {relative}")

    for path in python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as error:
            errors.append(f"{path.relative_to(ROOT)} cannot be parsed: {error}")
            continue
        if path == ROOT / "src" / "status_summary.py":
            for node in ast.walk(tree):
                names: list[str] = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module]
                for name in names:
                    if name == "scripts" or name.startswith("scripts.") or name == "tests" or name.startswith("tests."):
                        errors.append(
                            "src/status_summary.py violates domain dependency direction by importing "
                            f"{name!r}. Remediation: move adapter or test concerns outside the pure domain module."
                        )

    if errors:
        for error in errors:
            print(f"ERROR [check] {error}")
        return 1
    print(f"PASS: static and structural checks ({len(python_files())} Python files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
