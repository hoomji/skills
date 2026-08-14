#!/usr/bin/env python3
"""Read-only scan for broken local links and obvious harness drift."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"\[[^]]*\]\(([^)]+)\)")
PLACEHOLDERS = ("[authoritative path]", "[exact evidenced command]", "TODO: replace")


def main() -> int:
    findings: list[str] = []
    markdown_files = sorted(ROOT.rglob("*.md"))
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for placeholder in PLACEHOLDERS:
            if placeholder in text:
                findings.append(
                    f"{path.relative_to(ROOT)} contains unresolved placeholder {placeholder!r}"
                )
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"[A-Za-z][A-Za-z0-9+.-]*://", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                findings.append(
                    f"{path.relative_to(ROOT)} contains broken link {raw_target!r}"
                )

    if findings:
        for finding in findings:
            print(
                "ERROR [garden] "
                f"{finding}. Remediation: repair the pointer or retire the stale artifact."
            )
        return 1
    print(f"PASS: garden scan found no broken links or placeholders ({len(markdown_files)} Markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
