#!/usr/bin/env python3
"""Tests for bootstrap_orchestration.py."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("bootstrap_orchestration.py")
SPEC = importlib.util.spec_from_file_location("bootstrap_orchestration", SCRIPT)
bootstrap = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["bootstrap_orchestration"] = bootstrap
SPEC.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def run_bootstrap(self, repo: Path, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = bootstrap.main(["--repo", str(repo), *args])
        return code, stdout.getvalue()

    def test_empty_repo_creates_ai_workflow_and_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".git").mkdir()
            (repo / "package.json").write_text(
                '{"scripts":{"build":"tsc","test":"jest","dev":"vite"}}',
                encoding="utf-8",
            )

            code, output = self.run_bootstrap(repo)

            self.assertEqual(code, 0, output)
            self.assertTrue((repo / "ai" / "PLAN.md").exists())
            self.assertTrue((repo / "ai" / "AGENTS.md").exists())
            self.assertTrue((repo / "ai" / "LEARNINGS.md").exists())
            self.assertTrue((repo / "ai" / "ARCHITECTURE.md").exists())
            self.assertTrue((repo / "ai" / "orchestration" / "README.md").exists())
            self.assertEqual(
                (repo / "AGENTS.md").read_text(encoding="utf-8"),
                bootstrap.ROOT_BRIDGE,
            )
            self.assertIn("claude.*.input.md", (repo / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn("Created:", output)
            self.assertNotIn("@@", (repo / "ai" / "PLAN.md").read_text(encoding="utf-8"))

    def test_existing_ai_plan_creates_candidate_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("# App\n", encoding="utf-8")
            ai = repo / "ai"
            ai.mkdir()
            plan = ai / "PLAN.md"
            plan.write_text("existing plan\n", encoding="utf-8")

            code, _ = self.run_bootstrap(repo)

            self.assertEqual(code, 0)
            self.assertEqual(plan.read_text(encoding="utf-8"), "existing plan\n")
            self.assertTrue((ai / "PLAN.md.candidate.md").exists())
            self.assertTrue((ai / "orchestration" / "BOOTSTRAP_REPORT.md").exists())

    def test_force_overwrites_ai_workflow_and_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "README.md").write_text("# App\n", encoding="utf-8")
            ai = repo / "ai"
            ai.mkdir()
            plan = ai / "PLAN.md"
            plan.write_text("stale\n", encoding="utf-8")

            code, output = self.run_bootstrap(repo, "--force")

            self.assertEqual(code, 0, output)
            self.assertNotEqual(plan.read_text(encoding="utf-8"), "stale\n")
            report = ai / "orchestration" / "BOOTSTRAP_REPORT.md"
            self.assertTrue(report.exists())
            self.assertIn("PLAN.md", report.read_text(encoding="utf-8"))
            self.assertIn("Overwritten:", output)

    def test_substantive_root_agents_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            root_agents = repo / "AGENTS.md"
            root_agents.write_text("# Existing\n\nDo not replace.\n", encoding="utf-8")
            (repo / "README.md").write_text("# App\n", encoding="utf-8")

            code, _ = self.run_bootstrap(repo, "--force")

            self.assertEqual(code, 0)
            self.assertEqual(root_agents.read_text(encoding="utf-8"), "# Existing\n\nDo not replace.\n")
            self.assertTrue((repo / "AGENTS.md.candidate.md").exists())

    def test_unrelated_root_docs_do_not_block_ai_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "PLAN.md").write_text("# Product Plan\n", encoding="utf-8")
            (repo / "LEARNINGS.md").write_text("# Human Notes\n", encoding="utf-8")
            (repo / "ARCHITECTURE.md").write_text("# System Design\n", encoding="utf-8")

            code, output = self.run_bootstrap(repo)

            self.assertEqual(code, 0, output)
            self.assertTrue((repo / "ai" / "PLAN.md").exists())
            self.assertEqual((repo / "PLAN.md").read_text(encoding="utf-8"), "# Product Plan\n")

    def test_root_workflow_is_preserved_in_root_location(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "PLAN.md").write_text(
                "# Plan\n\n## HOW TO PLAN A MILESTONE\n\n## HOW TO EXECUTE A MILESTONE\n",
                encoding="utf-8",
            )

            code, _ = self.run_bootstrap(repo)

            self.assertEqual(code, 0)
            self.assertFalse((repo / "ai" / "PLAN.md").exists())
            self.assertTrue((repo / "PLAN.md.candidate.md").exists())
            self.assertTrue((repo / "orchestration" / "README.md").exists())

    def test_existing_gitignore_appended_outside_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".gitignore").write_text("node_modules\n", encoding="utf-8")

            code, _ = self.run_bootstrap(repo)

            self.assertEqual(code, 0)
            text = (repo / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("node_modules", text)
            self.assertIn("claude.*.output.md", text)

    def test_missing_gitignore_created_only_when_git_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            code, _ = self.run_bootstrap(repo)
            self.assertEqual(code, 0)
            self.assertFalse((repo / ".gitignore").exists())

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".git").mkdir()
            code, _ = self.run_bootstrap(repo)
            self.assertEqual(code, 0)
            self.assertTrue((repo / ".gitignore").exists())

    def test_hyphen_milestone_style_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ai = repo / "ai"
            ai.mkdir()
            (ai / "PLAN-M1.md").write_text("# M1\n", encoding="utf-8")

            code, _ = self.run_bootstrap(repo)

            self.assertEqual(code, 0)
            self.assertEqual(bootstrap.detect_milestone_style(repo, ai, "auto"), "hyphen")

    def test_validation_fails_on_unresolved_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            code, _ = self.run_bootstrap(repo)
            self.assertEqual(code, 0)
            plan = repo / "ai" / "PLAN.md"
            plan.write_text(plan.read_text(encoding="utf-8") + "\n@@BROKEN@@\n", encoding="utf-8")

            state = bootstrap.OperationState()
            bootstrap.validate(repo, repo / "ai", False, state)

            self.assertTrue(any("unresolved placeholders" in err for err in state.validation_errors))

    def test_todo_section_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            code, _ = self.run_bootstrap(repo)
            self.assertEqual(code, 0)

            state = bootstrap.OperationState()
            bootstrap.validate(repo, repo / "ai", False, state)
            self.assertFalse(state.validation_errors)

            readme = repo / "ai" / "orchestration" / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nTODO(repo): bad\n", encoding="utf-8")
            state = bootstrap.OperationState()
            bootstrap.validate(repo, repo / "ai", False, state)
            self.assertTrue(any("illegal TODO" in err for err in state.validation_errors))

            readme.write_text(readme.read_text(encoding="utf-8").replace("\nTODO(repo): bad\n", "\n"), encoding="utf-8")
            plan = repo / "ai" / "PLAN.md"
            text = plan.read_text(encoding="utf-8").replace(
                "Please include this section verbatim when you write a milestone plan file.",
                "TODO(repo): bad\n\nPlease include this section verbatim when you write a milestone plan file.",
            )
            plan.write_text(text, encoding="utf-8")
            state = bootstrap.OperationState()
            bootstrap.validate(repo, repo / "ai", False, state)
            self.assertTrue(any("illegal TODO" in err for err in state.validation_errors))

    def test_generated_guidance_includes_expanded_orchestration_rules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "package.json").write_text(
                '{"scripts":{"build":"tsc","test":"jest","dev":"vite"}}',
                encoding="utf-8",
            )

            code, output = self.run_bootstrap(repo)

            self.assertEqual(code, 0, output)
            plan = (repo / "ai" / "PLAN.md").read_text(encoding="utf-8")
            agents = (repo / "ai" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Discoverable facts (repo/system truth): explore first.", plan)
            self.assertIn("Please include this section verbatim when you write a milestone plan file.", plan)
            self.assertIn("Do not reference previous rounds when you invoke Claude.", plan)
            self.assertIn("Close The Loop, Autonomy", agents)
            self.assertIn("Address prerequisites cleanly, do not hack around them.", agents)
            self.assertIn("Please read", agents)

    def test_python_makefile_commands_and_generated_surfaces_are_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "pyproject.toml").write_text("[project]\nname = 'app'\n", encoding="utf-8")
            (repo / "Makefile").write_text("test:\n\tpytest\n\nlint:\n\truff check .\n\nrun:\n\tpython -m app\n", encoding="utf-8")
            (repo / "app" / "admin" / "static" / "css").mkdir(parents=True)
            (repo / "app" / "admin" / "static" / "css" / "app.css.in").write_text("/* css */\n", encoding="utf-8")
            (repo / "bigquery" / "scheduled_queries").mkdir(parents=True)

            code, output = self.run_bootstrap(repo)

            self.assertEqual(code, 0, output)
            agents = (repo / "ai" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("`make test`", agents)
            self.assertIn("`make lint`", agents)
            self.assertIn("`make run`", agents)
            self.assertIn("app/admin/static/css/app.css", agents)
            self.assertIn("bigquery/scheduled_queries/", agents)

    def test_no_dry_run_argument(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                self.run_bootstrap(repo, "--dry-run")


if __name__ == "__main__":
    unittest.main()
