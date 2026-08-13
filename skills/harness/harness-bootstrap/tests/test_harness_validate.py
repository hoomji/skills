from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).parents[1] / "assets" / "harness-validate.py"


class HarnessValidateTests(unittest.TestCase):
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
- Designs: [design docs](docs/design-docs/index.md)

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
        (self.root / "docs" / "design-docs").mkdir()
        (self.root / "docs" / "design-docs" / "index.md").write_text(
            "# Design documentation\n\n"
            "| Design | State | Owner | Last verified | Evidence |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| None yet | Proposed | platform-team | Unverified | None |\n",
            encoding="utf-8",
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
            "setup:\n\t@true\n\nstart:\n\t@true\n\ncheck:\n\t@true\n\ntest:\n\t@true\n",
            encoding="utf-8",
        )
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
  design: "docs/design-docs/index.md"
commands:
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

    def test_design_index_requires_lifecycle_and_verification_metadata(self) -> None:
        (self.root / "docs" / "design-docs" / "index.md").write_text(
            "# Design documentation\n", encoding="utf-8"
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("design-index.contract", result.stdout)
        self.assertIn("last verified", result.stdout)

    def test_design_entrypoint_is_required_separately_from_architecture(self) -> None:
        manifest = self.root / "docs" / "harness" / "manifest.yaml"
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace(
                '  design: "docs/design-docs/index.md"\n', ""
            ),
            encoding="utf-8",
        )
        self.assertIn("entrypoints.design", self.run_validator().stdout)
if __name__ == "__main__":


    unittest.main()
