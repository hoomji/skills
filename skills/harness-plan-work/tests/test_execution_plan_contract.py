from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "execution-plan.md.template"


class ExecutionPlanContractTests(unittest.TestCase):
    def test_skill_routes_to_template(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("assets/execution-plan.md.template", skill)
        self.assertIn("maximum class is R1", skill)
        self.assertIn("do not publish from this skill", skill)

    def test_template_carries_shared_execution_contract(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "**Originating goal/spec:**",
            "**Baseline:**",
            "**Maximum authorized risk:**",
            "## Acceptance evidence",
            "## Milestones",
            "**Completion criterion:**",
            "**Verify:**",
            "**Rollback:**",
            "**Escalate when:**",
            "## Progress log",
            "## Decision log",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
