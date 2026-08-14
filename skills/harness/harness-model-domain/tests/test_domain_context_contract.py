from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
CONTEXT_TEMPLATE = ROOT / "assets" / "context.md.template"
MAP_TEMPLATE = ROOT / "assets" / "context-map.md.template"
HARNESS = ROOT.parent / "harness" / "SKILL.md"
CONTRACTS = ROOT.parent / "harness" / "references" / "contracts.md"


class DomainContextContractTests(unittest.TestCase):
    def test_skill_keeps_context_as_a_current_domain_glossary(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        for required in (
            "current canonical vocabulary, not a historical log",
            "do not scaffold an empty glossary",
            "do not promote the first glossary term",
            "general programming terms",
            "one or two sentences",
            "_Avoid_",
            "harness-record-decision",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_templates_separate_terms_from_context_relationships(self) -> None:
        context = CONTEXT_TEMPLATE.read_text(encoding="utf-8")
        context_map = MAP_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("## Language", context)
        self.assertIn("_Avoid_:", context)
        self.assertIn("## Contexts", context_map)
        self.assertIn("## Relationships", context_map)
        self.assertIn("<Source> -> <Target>", context_map)
        self.assertNotIn("?", context_map)

    def test_router_and_shared_contract_make_context_native(self) -> None:
        self.assertIn("harness-model-domain", HARNESS.read_text(encoding="utf-8"))
        contracts = CONTRACTS.read_text(encoding="utf-8")
        self.assertIn("## Domain context", contracts)
        self.assertIn("living glossary", contracts)


if __name__ == "__main__":
    unittest.main()
