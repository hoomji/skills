from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "learning-ledger-entry.md.template"


class LearningEntryContractTests(unittest.TestCase):
    def test_skill_routes_to_template(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("assets/learning-ledger-entry.md.template", skill)
        self.assertIn("freshness.review_after_days", skill)
        self.assertIn("maximum class is R1", skill)
        self.assertIn("requires R2–R4 authority", skill)

    def test_template_carries_shared_learning_contract(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "**Observed friction:**",
            "**Expected behavior:**",
            "**Evidence:**",
            "**Frequency:**",
            "**Impact:**",
            "**Missing harness plane:**",
            "**Mechanism:**",
            "**Durable layer:**",
            "**Disposition:** implemented | proposed | not encoded",
            "**Owner:**",
            "**Closure evidence:**",
            "**Review date:**",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
