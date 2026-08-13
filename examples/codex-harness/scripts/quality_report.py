#!/usr/bin/env python3
"""Emit an evidence-oriented harness quality snapshot without mutation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANES = {
    "intent": (3, "docs/product-specs/status-summary.md"),
    "knowledge": (3, "docs/design-docs/index.md"),
    "execution": (3, "scripts/setup.py"),
    "feedback": (3, "tests/test_status_summary.py"),
    "policy": (4, "scripts/check.py"),
    "isolation": (1, "docs/operations/isolation.md"),
    "lifecycle": (2, "docs/harness/lifecycle.md"),
    "hygiene": (2, "scripts/garden.py"),
    "governance": (1, "docs/harness/governance.md"),
}


def main() -> int:
    missing = [evidence for _, evidence in PLANES.values() if not (ROOT / evidence).is_file()]
    if missing:
        for path in missing:
            print(f"ERROR [quality] missing evidence path: {path}")
        return 1
    report = {
        name: {"level": level, "evidence": evidence}
        for name, (level, evidence) in PLANES.items()
    }
    print(json.dumps({"planes": report}, indent=2, sort_keys=True))
    print("PASS: quality levels are reported independently; no aggregate score was computed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
