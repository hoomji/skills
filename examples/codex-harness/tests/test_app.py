from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def test_start_emits_structured_task_local_event(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/start.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        event = json.loads(completed.stdout.strip())
        self.assertEqual("status_summary.completed", event["event"])
        self.assertTrue(event["task_namespace"].startswith("codex-harness-"))
        self.assertEqual("unknown", event["summary"]["aggregate_state"])


if __name__ == "__main__":
    unittest.main()
