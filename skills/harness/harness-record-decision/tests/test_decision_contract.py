from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "adr.md.template"
HARNESS = ROOT.parent / "harness" / "SKILL.md"
CONTRACTS = ROOT.parent / "harness" / "references" / "contracts.md"


class DecisionContractTests(unittest.TestCase):
    def test_skill_enforces_the_adr_threshold_and_lifecycle(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "Hard to reverse",
            "Surprising without context",
            "A real trade-off",
            "inspect, create, accept, deprecate, or supersede",
            "Never renumber",
            "harness-encode-invariant",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_template_keeps_context_decision_and_rationale_primary(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("context, what was decided, and why", text)
        self.assertIn("## Considered Options", text)
        self.assertIn("## Consequences", text)

    def test_router_and_shared_contract_make_adrs_native(self) -> None:
        self.assertIn("harness-record-decision", HARNESS.read_text(encoding="utf-8"))
        contracts = CONTRACTS.read_text(encoding="utf-8")
        self.assertIn("## Decision records", contracts)
        self.assertIn("ExecPlan decision log", contracts)


if __name__ == "__main__":
    unittest.main()
