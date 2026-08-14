from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).parents[1]
ASSETS = SKILL_ROOT / "assets"
STORE_ASSETS = ASSETS / "knowledge-store"
VALIDATOR = ASSETS / "harness-validate.py"

# Every store index the bootstrap installs, and the template it is installed from.
INSTALLED = {
    "docs/design-docs/index.md": "design-docs-index.md.template",
    "docs/design-docs/core-beliefs.md": "core-beliefs.md.template",
    "docs/exec-plans/index.md": "exec-plans-index.md.template",
    "docs/exec-plans/tech-debt-tracker.md": "tech-debt-tracker.md.template",
    "docs/generated/index.md": "generated-index.md.template",
    "docs/product-specs/index.md": "product-specs-index.md.template",
    "docs/product-specs/template.md": "product-spec.md.template",
    "docs/references/index.md": "references-index.md.template",
}
STORE_INDEXES = {
    "design_docs": "docs/design-docs/index.md",
    "exec_plans": "docs/exec-plans/index.md",
    "generated": "docs/generated/index.md",
    "product_specs": "docs/product-specs/index.md",
    "references": "docs/references/index.md",
}


class KnowledgeStoreTemplateTests(unittest.TestCase):
    """The bundled templates must satisfy the contract the validator enforces."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name) / "repository"
        (self.root / "docs" / "harness").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        for lifecycle in ("active", "completed"):
            directory = self.root / "docs" / "exec-plans" / lifecycle
            directory.mkdir(parents=True)
            (directory / ".gitkeep").write_text("", encoding="utf-8")
        for target, template in INSTALLED.items():
            destination = self.root / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((STORE_ASSETS / template).read_bytes())
        (self.root / "PLAN.md").write_bytes((ASSETS / "PLAN.md.template").read_bytes())
        (self.root / "ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")
        (self.root / "Makefile").write_text(
            "setup:\n\t@true\n\ncheck:\n\t@true\n\ntest:\n\t@true\n\nstart:\n\t@true\n",
            encoding="utf-8",
        )
        (self.root / "scripts" / "harness-validate.py").write_bytes(
            VALIDATOR.read_bytes()
        )
        (self.root / "docs" / "harness" / "tracer-workflow.md").write_bytes(
            (ASSETS / "tracer-workflow.md.template").read_bytes()
        )
        (self.root / "docs" / "harness" / "learning-ledger.md").write_bytes(
            (ASSETS / "learning-ledger.md.template").read_bytes()
        )
        pointers = "\n".join(f"- `{path}`" for path in STORE_INDEXES.values())
        (self.root / "AGENTS.md").write_text(
            "# Agent guidance\n\n## Knowledge store\n\n"
            f"{pointers}\n\n## Commands\n\n"
            "- Setup: `make setup`\n- Start: `make start`\n- Check: `make check`\n"
            "- Test: `make test`\n"
            "- Harness validation: `python3 scripts/harness-validate.py .`\n",
            encoding="utf-8",
        )
        stores = "\n".join(
            f'  {key}: "{path}"' for key, path in STORE_INDEXES.items()
        )
        (self.root / "docs" / "harness" / "manifest.yaml").write_text(
            "version: 1\n"
            'owners:\n  harness: "platform-team"\n'
            "entrypoints:\n"
            '  guidance: "AGENTS.md"\n'
            '  architecture: "ARCHITECTURE.md"\n'
            '  tracer: "docs/harness/tracer-workflow.md"\n'
            f"knowledge_store:\n{stores}\n"
            "commands:\n"
            '  setup: "make setup"\n  start: "make start"\n  check: "make check"\n'
            '  test: "make test"\n'
            '  validate: "python3 scripts/harness-validate.py ."\n'
            "capabilities: {}\npolicies: []\n"
            "freshness:\n  review_after_days: 90\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_freshly_installed_knowledge_store_validates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_installed_template_exists(self) -> None:
        for template in INSTALLED.values():
            with self.subTest(template=template):
                self.assertTrue((STORE_ASSETS / template).is_file())

    def test_skill_documents_every_installed_path(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for target in INSTALLED:
            with self.subTest(target=target):
                self.assertIn(target, skill)

    def test_manifest_template_declares_every_store(self) -> None:
        manifest = (ASSETS / "manifest.yaml.template").read_text(encoding="utf-8")
        for key, path in STORE_INDEXES.items():
            with self.subTest(store=key):
                self.assertIn(f"{key}: \"{path}\"", manifest)

    def test_agent_map_template_advertises_every_store(self) -> None:
        agents = (ASSETS / "AGENTS.md.template").read_text(encoding="utf-8")
        for path in STORE_INDEXES.values():
            with self.subTest(path=path):
                self.assertIn(path, agents)


if __name__ == "__main__":
    unittest.main()
