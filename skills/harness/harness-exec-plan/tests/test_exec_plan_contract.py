from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "exec-plan.md.template"


class ExecPlanContractTests(unittest.TestCase):
    def test_skill_uses_the_canonical_template(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("assets/exec-plan.md.template", skill)
        self.assertIn("self-contained", skill)
        self.assertIn("one `md`", skill)
        self.assertIn("revision note", skill)

    def test_template_carries_the_living_plan_contract(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "## Purpose / Big Picture",
            "## Progress",
            "## Surprises & Discoveries",
            "## Decision Log",
            "## Outcomes & Retrospective",
            "## Context and Orientation",
            "## Milestones",
            "Completion criterion:",
            "Verification:",
            "Rollback and recovery:",
            "Escalate when:",
            "## Concrete Steps",
            "## Validation and Acceptance",
            "## Idempotence and Recovery",
            "## Interfaces and Dependencies",
            "## Revision Note",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()