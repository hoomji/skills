from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).parents[1] / "assets" / "harness-validate.py"

KNOWLEDGE_STORE_BLOCK = """knowledge_store:
  design_docs: "docs/design-docs/index.md"
  exec_plans: "docs/exec-plans/index.md"
  generated: "docs/generated/index.md"
  product_specs: "docs/product-specs/index.md"
  references: "docs/references/index.md"
"""


class HarnessValidateTests(unittest.TestCase):
    def write_knowledge_store(self) -> None:
        docs = self.root / "docs"
        for directory in (
            "design-docs",
            "exec-plans/active",
            "exec-plans/completed",
            "generated",
            "product-specs",
            "references",
        ):
            (docs / directory).mkdir(parents=True, exist_ok=True)
        (docs / "design-docs" / "index.md").write_text(
            "# Design documents\n\nVerification status vocabulary.\n\n"
            "| Document | Verification status |\n|---|---|\n"
            "| [Core beliefs](core-beliefs.md) | unverified |\n",
            encoding="utf-8",
        )
        (docs / "design-docs" / "core-beliefs.md").write_text(
            "# Core beliefs\n\nEvidence outranks assertion.\n", encoding="utf-8"
        )
        (docs / "exec-plans" / "index.md").write_text(
            "# Execution plans\n\n## Active\n\n_None._\n\n## Completed\n\n_None._\n\n"
            "Debt lives in [the tracker](tech-debt-tracker.md).\n",
            encoding="utf-8",
        )
        (docs / "exec-plans" / "tech-debt-tracker.md").write_text(
            "# Technical debt tracker\n\n_No recorded debt._\n", encoding="utf-8"
        )
        for lifecycle in ("active", "completed"):
            (docs / "exec-plans" / lifecycle / ".gitkeep").write_text(
                "", encoding="utf-8"
            )
        (docs / "generated" / "index.md").write_text(
            "# Generated documentation\n\n| Artifact | Producing command |\n|---|---|\n",
            encoding="utf-8",
        )
        (docs / "product-specs" / "index.md").write_text(
            "# Product specifications\n\nStatus vocabulary: draft, delivered.\n\n"
            "Write specifications with [the template](template.md).\n",
            encoding="utf-8",
        )
        (docs / "product-specs" / "template.md").write_text(
            "# [Specification title]\n\n- Status: `draft`\n", encoding="utf-8"
        )
        (docs / "references" / "index.md").write_text(
            "# External references\n\n| Reference | Source | Review date |\n|---|---|---|\n",
            encoding="utf-8",
        )

    def add_generated_artifact(self, command: str = "make docs") -> Path:
        path = self.root / "docs" / "generated" / "db-schema.md"
        path.write_text(
            f"<!-- Do not edit. Generated file. -->\n"
            f"<!-- Producing command: `{command}` -->\n\n# Database schema\n",
            encoding="utf-8",
        )
        index = self.root / "docs" / "generated" / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8")
            + "| [Database schema](db-schema.md) | `make docs` |\n",
            encoding="utf-8",
        )
        return path

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.root = self.workspace / "repository"
        self.root.mkdir()
        (self.root / "docs" / "harness").mkdir(parents=True)
        (self.root / "scripts").mkdir()
        (self.root / "AGENTS.md").write_text(
            """# Agent map

- Architecture: [architecture](docs/architecture.md)
- Tracer: [workflow](docs/harness/tracer-workflow.md)

## Knowledge store

- Design: `docs/design-docs/index.md`
- Plans: `docs/exec-plans/index.md`
- Generated: `docs/generated/index.md`
- Product: `docs/product-specs/index.md`
- References: `docs/references/index.md`

## Commands

- Setup: `make setup`
- Start: `make start`
- Check: `make check`
- Test: `make test`
- Harness validation: `python3 scripts/harness-validate.py .`
""",
            encoding="utf-8",
        )
        (self.root / "CLAUDE.md").write_text(
            "Read and follow [AGENTS.md](./AGENTS.md).\n", encoding="utf-8"
        )
        (self.root / "docs" / "architecture.md").write_text(
            "# Architecture\n", encoding="utf-8"
        )
        (self.root / "docs" / "harness" / "tracer-workflow.md").write_text(
            "# Tracer workflow\n\n## Acceptance criteria\n\n- Change works.\n\n"
            "## Evidence\n\n- `make test`\n",
            encoding="utf-8",
        )
        (self.root / "docs" / "harness" / "learning-ledger.md").write_text(
            "# Harness learning ledger\n\nObserved friction\nMissing harness plane\n"
            "Closure evidence\nReview date\n",
            encoding="utf-8",
        )
        (self.root / "Makefile").write_text(
            "setup:\n\t@true\n\nstart:\n\t@true\n\ncheck:\n\t@true\n\n"
            "test:\n\t@true\n\ndocs:\n\t@true\n",
            encoding="utf-8",
        )
        self.write_knowledge_store()
        (self.root / "scripts" / "harness-validate.py").write_text(
            "# repository-local validator placeholder used only as path evidence\n",
            encoding="utf-8",
        )
        self.write_manifest()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_manifest(
        self,
        *,
        architecture: str = "docs/architecture.md",
        check: str = "make check",
        start: str = "make start",
        capability: str | None = None,
        knowledge_store: str = KNOWLEDGE_STORE_BLOCK,
    ) -> None:
        capability_block = (
            capability
            or """  reproducible_checks:
    status: \"verified\"
    evidence:
      - \"Makefile\"
"""
        )
        (self.root / "docs" / "harness" / "manifest.yaml").write_text(
            f"""version: 1
owners:
  harness: \"platform-team\"
entrypoints:
  guidance: \"AGENTS.md\"
  architecture: \"{architecture}\"
  tracer: \"docs/harness/tracer-workflow.md\"
{knowledge_store}commands:
  setup: \"make setup\"
  start: \"{start}\"
  check: \"{check}\"
  test: \"make test\"
  validate: \"python3 scripts/harness-validate.py .\"
capabilities:
{capability_block}policies:
  - id: \"test-gate\"
    enforcement: \"make test\"
    owner: \"platform-team\"
    remediation: \"Run make test and repair the reported failure.\"
freshness:
  review_after_days: 90
""",
            encoding="utf-8",
        )

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(self.root)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_harness_passes_without_mutating_repository(self) -> None:
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))

        result = self.run_validator()

        after = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS: harness contract is internally consistent", result.stdout)
        self.assertEqual(after, before)

    def test_broken_path_and_make_target_fail_with_remediation(self) -> None:
        self.write_manifest(architecture="docs/missing.md", check="make missing")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("entrypoints.architecture", result.stdout)
        self.assertIn("make target 'missing'", result.stdout)
        self.assertIn("Remediation:", result.stdout)

    def test_verified_capability_without_evidence_is_rejected(self) -> None:
        self.write_manifest(
            capability="""  reproducible_checks:
    status: \"verified\"
    evidence: []
"""
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("capabilities.reproducible_checks.evidence", result.stdout)
        self.assertIn("verified", result.stdout)

    def test_unknown_required_verification_command_is_rejected(self) -> None:
        self.write_manifest(check="unknown")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("commands.check", result.stdout)
        self.assertIn("cannot remain 'unknown'", result.stdout)

    def test_opaque_tool_command_must_be_wrapped_in_a_stable_entrypoint(self) -> None:
        self.write_manifest(check="python3 -m definitely_missing_harness_module")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("command.opaque", result.stdout)
        self.assertIn("task-runner", result.stdout)

    def test_bare_opaque_command_is_rejected(self) -> None:
        for command in ("false", "make", "npm", "npm run"):
            with self.subTest(command=command):
                self.write_manifest(check=command)

                result = self.run_validator()

                self.assertEqual(result.returncode, 1)
                self.assertRegex(result.stdout, r"command\.(opaque|package-script)")

    def test_unknown_start_requires_evidence_that_no_runtime_exists(self) -> None:
        self.write_manifest(start="unknown")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            agents.replace("`make start`", "`unknown`"), encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("commands.start", result.stdout)
        self.assertIn("startable_runtime", result.stdout)

    def test_unknown_start_is_allowed_when_no_runtime_is_evidenced(self) -> None:
        self.write_manifest(
            start="unknown",
            capability="""  startable_runtime:
    status: \"missing\"
    evidence:
      - \"AGENTS.md\"
""",
        )
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            agents.replace("`make start`", "`unknown`"), encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN [commands.start]", result.stdout)

    def test_guidance_link_cannot_escape_repository(self) -> None:
        outside = self.workspace / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            agents + "\n[Outside](../outside.md)\n", encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("guidance.link-outside", result.stdout)

    def test_unsupported_capability_status_is_rejected(self) -> None:
        self.write_manifest(
            capability="""  reproducible_checks:
    status: \"aspirational\"
    evidence:
      - \"Makefile\"
"""
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("capabilities.reproducible_checks.status", result.stdout)
        self.assertIn("unsupported", result.stdout)

    def test_enforced_policy_requires_remediation(self) -> None:
        manifest = self.root / "docs" / "harness" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '    remediation: "Run make test and repair the reported failure."\n',
                "",
            ),
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("policies[0].remediation", result.stdout)
        self.assertIn("Remediation:", result.stdout)

    def test_claude_guidance_must_route_to_shared_agent_map(self) -> None:
        (self.root / "CLAUDE.md").write_text("# Claude-only rules\n", encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("CLAUDE.md", result.stdout)
        self.assertIn("AGENTS.md", result.stdout)

    def test_advertised_commands_must_appear_in_agent_map(self) -> None:
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            agents.replace("`make test`", "`make unit`"), encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("commands.test", result.stdout)
        self.assertIn("AGENTS.md", result.stdout)

    def test_generated_artifact_with_provenance_and_real_producer_passes(self) -> None:
        self.add_generated_artifact()

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_undeclared_knowledge_store_is_rejected(self) -> None:
        self.write_manifest(
            knowledge_store=KNOWLEDGE_STORE_BLOCK.replace(
                '  references: "docs/references/index.md"\n', ""
            )
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("knowledge_store.references is not declared", result.stdout)

    def test_missing_knowledge_store_block_is_rejected(self) -> None:
        self.write_manifest(knowledge_store="")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("knowledge-store.type", result.stdout)
        self.assertIn("product_specs", result.stdout)

    def test_store_index_must_be_advertised_in_agent_map(self) -> None:
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        (self.root / "AGENTS.md").write_text(
            agents.replace("`docs/references/index.md`", "`somewhere else`"),
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("guidance.knowledge-store", result.stdout)
        self.assertIn("references", result.stdout)

    def test_store_index_missing_its_contract_sections_is_rejected(self) -> None:
        (self.root / "docs" / "exec-plans" / "index.md").write_text(
            "# Execution plans\n\nDebt lives in [the tracker](tech-debt-tracker.md).\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.index-contract", result.stdout)
        self.assertIn("Active, Completed", result.stdout)

    def test_orphaned_store_artifact_is_rejected(self) -> None:
        (self.root / "docs" / "product-specs" / "checkout.md").write_text(
            "# Checkout\n", encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.unlisted", result.stdout)
        self.assertIn("docs/product-specs/checkout.md", result.stdout)

    def test_generated_artifact_without_provenance_header_is_rejected(self) -> None:
        artifact = self.add_generated_artifact()
        artifact.write_text("# Database schema\n", encoding="utf-8")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.provenance", result.stdout)
        self.assertIn("Do not edit", result.stdout)

    def test_generated_artifact_with_broken_producer_is_rejected(self) -> None:
        self.add_generated_artifact(command="make missing-docs")

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("producing command", result.stdout)
        self.assertIn("make target 'missing-docs'", result.stdout)

    def test_reference_without_source_and_retrieval_date_is_rejected(self) -> None:
        (self.root / "docs" / "references" / "protocol.md").write_text(
            "# Protocol notes\n\nSummary only.\n", encoding="utf-8"
        )
        index = self.root / "docs" / "references" / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8") + "| [Protocol](protocol.md) | — |\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.provenance", result.stdout)
        self.assertIn("Source:, Retrieved:", result.stdout)

    def test_reference_provenance_may_use_markdown_emphasis(self) -> None:
        (self.root / "docs" / "references" / "protocol.md").write_text(
            "# Protocol notes\n\n- **Source**: [Spec](https://example.invalid/spec)\n"
            "- **Retrieved**: 2026-08-14\n",
            encoding="utf-8",
        )
        index = self.root / "docs" / "references" / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8")
            + "| [Protocol](protocol.md) | Source | 2026-08-14 |\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_plan_in_two_lifecycle_states_is_rejected(self) -> None:
        plans = self.root / "docs" / "exec-plans"
        body = "# Plan\n"
        for lifecycle in ("active", "completed"):
            (plans / lifecycle / "2026-08-14-tracer.md").write_text(
                body, encoding="utf-8"
            )
        index = plans / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8")
            + "- [Active](active/2026-08-14-tracer.md)\n"
            + "- [Completed](completed/2026-08-14-tracer.md)\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.lifecycle-duplicate", result.stdout)

    def test_plan_outside_a_lifecycle_directory_is_rejected(self) -> None:
        plans = self.root / "docs" / "exec-plans"
        (plans / "2026-08-14-tracer.md").write_text("# Plan\n", encoding="utf-8")
        index = plans / "index.md"
        index.write_text(
            index.read_text(encoding="utf-8") + "- [Plan](2026-08-14-tracer.md)\n",
            encoding="utf-8",
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.location", result.stdout)

    def test_missing_lifecycle_directory_and_debt_tracker_are_rejected(self) -> None:
        shutil.rmtree(self.root / "docs" / "exec-plans" / "completed")
        (self.root / "docs" / "exec-plans" / "tech-debt-tracker.md").unlink()

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("store.missing-directory", result.stdout)
        self.assertIn("store.missing-file", result.stdout)


if __name__ == "__main__":
    unittest.main()
