from __future__ import annotations

import unittest

from src.status_summary import CheckResult, parse_check_results, summarize


class StatusSummaryTests(unittest.TestCase):
    def test_all_pass_is_healthy(self) -> None:
        result = summarize((CheckResult("build", "pass"), CheckResult("test", "pass")))
        self.assertEqual("healthy", result.aggregate_state)
        self.assertEqual(2, result.passed)
        self.assertEqual([], result.to_dict()["failed_checks"])

    def test_failure_takes_precedence_over_unknown(self) -> None:
        result = summarize(
            (
                CheckResult("build", "unknown"),
                CheckResult("test", "fail"),
            )
        )
        self.assertEqual("degraded", result.aggregate_state)
        self.assertEqual(("test",), result.failed_checks)
        self.assertEqual(("build",), result.unknown_checks)

    def test_unknown_without_failure_is_unknown(self) -> None:
        result = summarize((CheckResult("release", "unknown"),))
        self.assertEqual("unknown", result.aggregate_state)

    def test_empty_is_unknown(self) -> None:
        result = summarize(())
        self.assertEqual("unknown", result.aggregate_state)
        self.assertEqual(0, result.total)

    def test_input_order_is_preserved(self) -> None:
        result = summarize(
            (
                CheckResult("second", "fail"),
                CheckResult("first", "fail"),
                CheckResult("later", "unknown"),
            )
        )
        self.assertEqual(("second", "first"), result.failed_checks)
        self.assertEqual(("later",), result.unknown_checks)

    def test_invalid_state_names_accepted_states(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected one of"):
            parse_check_results(({"name": "build", "state": "maybe"},))

    def test_blank_name_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "name must be non-empty"):
            CheckResult(" ", "pass")


if __name__ == "__main__":
    unittest.main()
