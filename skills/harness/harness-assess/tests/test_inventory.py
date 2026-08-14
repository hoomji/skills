from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


INVENTORY = Path(__file__).parents[1] / "scripts" / "inventory.py"


class InventoryTests(unittest.TestCase):
    def test_reports_local_default_ref_and_head_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "-b", "main")
            self.git(root, "config", "user.email", "test@example.com")
            self.git(root, "config", "user.name", "Test User")
            (root / "README.md").write_text("# Test\n", encoding="utf-8")
            self.git(root, "add", "README.md")
            self.git(root, "commit", "-m", "initial")
            self.git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
            self.git(
                root,
                "symbolic-ref",
                "refs/remotes/origin/HEAD",
                "refs/remotes/origin/main",
            )
            self.git(root, "switch", "-c", "feature")
            (root / "AGENTS.md").write_text("# Agent map\n", encoding="utf-8")
            self.git(root, "add", "AGENTS.md")
            self.git(root, "commit", "-m", "branch harness")

            result = subprocess.run(
                [sys.executable, str(INVENTORY), str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(payload["git"]["branch"], "feature")
            self.assertEqual(payload["git"]["default_remote_ref"], "origin/main")
            self.assertEqual(
                payload["git"]["head_vs_default"],
                {"ahead": 1, "behind": 0, "relation": "ahead"},
            )
            self.assertEqual(payload["git"]["worktree_count"], 1)

    def test_reports_context_map_as_domain_architecture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CONTEXT-MAP.md").write_text(
                "# Context Map\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, str(INVENTORY), str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)

            self.assertIn(
                "CONTEXT-MAP.md", payload["architecture_and_domain_docs"]
            )

    @staticmethod
    def git(root: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
