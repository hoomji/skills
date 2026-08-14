from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "SKILL.md"
TEMPLATE = ROOT / "assets" / "exec-plan.md.template"
SLICE_TEMPLATE = ROOT / "assets" / "slice.md.template"
CONTRACTS = ROOT.parent / "harness" / "references" / "contracts.md"
DELIVER_WORK = ROOT.parent / "harness-deliver-work" / "SKILL.md"


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

    def test_milestones_index_their_slices(self) -> None:
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("Slices:", text)
        self.assertIn("fits one agent context", text)

    def test_skill_gates_and_scopes_slices(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("assets/slice.md.template", skill)
        # Slices are cut only when a milestone exceeds one context, never by default.
        self.assertIn("Cut slices only", skill)
        # Self-containment is scoped to the slice, not inherited from the plan.
        self.assertIn("scoped to the slice", skill)
        self.assertIn("harness-deliver-work", skill)

    def test_slice_template_is_executable_alone(self) -> None:
        text = SLICE_TEMPLATE.read_text(encoding="utf-8")
        for required in (
            "## Slice Header",
            "## Outcome",
            "## Orientation",
            "## Change",
            "## Out of Scope",
            "## Completion Criterion",
            "## Verification",
            "## Rollback and Recovery",
            "## Escalate When",
            "## Execution Record",
            "Risk ceiling:",
            "Dirty-state boundary:",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)
        self.assertIn("without reading the parent ExecPlan", text)

    def test_templates_avoid_nested_code_fences(self) -> None:
        for template in (TEMPLATE, SLICE_TEMPLATE):
            with self.subTest(template=template.name):
                self.assertNotIn("```", template.read_text(encoding="utf-8"))

    def test_slice_contract_is_shared_across_skills(self) -> None:
        self.assertIn("## Implementation slice", CONTRACTS.read_text(encoding="utf-8"))
        self.assertIn("ExecPlan slice", DELIVER_WORK.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()