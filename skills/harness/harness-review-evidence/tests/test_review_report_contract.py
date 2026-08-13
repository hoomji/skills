from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "review-report.md.template"


class ReviewReportContractTests(unittest.TestCase):
    def test_skill_routes_to_template(self) -> None:
        self.assertIn("assets/review-report.md.template", SKILL.read_text())

    def test_template_carries_review_and_evidence_axes(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "**Comparison base:**",
            "**Originating spec:**",
            "**Repository standards:**",
            "**Excluded dirty state:**",
            "## Findings",
            "**Smallest repair:**",
            "## Acceptance matrix",
            "supported, failed, or unknown",
            "## Evidence audit",
            "## Human judgment",
            "**Residual uncertainty:**",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
