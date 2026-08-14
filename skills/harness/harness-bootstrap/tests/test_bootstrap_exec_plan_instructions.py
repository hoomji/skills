from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
REPOSITORY_ROOT = Path(__file__).parents[4]
SKILL = SKILL_ROOT / "SKILL.md"
PLAN_SOURCE = REPOSITORY_ROOT / "PLAN.md"
PLAN_TEMPLATE = SKILL_ROOT / "assets" / "PLAN.md.template"


class BootstrapExecPlanInstructionTests(unittest.TestCase):
    def test_bootstrap_plan_template_matches_the_canonical_source_byte_for_byte(self) -> None:
        self.assertEqual(PLAN_TEMPLATE.read_bytes(), PLAN_SOURCE.read_bytes())

    def test_bootstrap_requires_verbatim_plan_installation(self) -> None:
        skill = SKILL.read_text(encoding="utf-8")
        self.assertIn("assets/PLAN.md.template", skill)
        self.assertIn("byte-for-byte", skill)
        self.assertIn("rather than overwriting divergent user guidance", skill)


if __name__ == "__main__":
    unittest.main()