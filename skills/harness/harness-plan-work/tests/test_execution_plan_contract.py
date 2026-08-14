from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT.parent / "harness-exec-plan" / "assets" / "exec-plan.md.template"


class ExecutionPlanContractTests(unittest.TestCase):
    def test_skill_routes_to_template(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("../harness-exec-plan/assets/exec-plan.md.template", skill)
        self.assertIn("maximum class is R1", skill)
        self.assertIn("do not publish from this skill", skill)

    def test_template_carries_shared_execution_contract(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "## Acceptance Evidence",
            "## Milestones",
            "Completion criterion:",
            "Verification:",
            "Rollback and recovery:",
            "Escalate when:",
            "## Progress",
            "## Decision Log",
            "## Surprises & Discoveries",
            "## Outcomes & Retrospective",
            "## Idempotence and Recovery",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()