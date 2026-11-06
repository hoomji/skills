"""verify-city trunk-promotion ledger checks (ci-h4c9). Run: python3 -m unittest test_trunk_promotion"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trunk_promotion as tp

SHA = "3d6220bd56b82e469aca5c42bef15fc81aaa9166"


def promo_check(r):
    return tp.ISO.match(r[0]) and r[1] in tp.PROMO_STATES and r[2].isdigit() and tp.HEX40.match(r[3])


def cadence_check(r):
    return tp.ISO.match(r[0]) and r[1] in tp.CADENCE_VERDICTS and tp.HEX40.match(r[2])


class LedgerRows(unittest.TestCase):
    def test_states_the_producers_write_are_known(self):
        rows = [["2026-10-24T16:45:03Z", "NEEDS-REVIEW", "6761", SHA, "release/trunk-x", "PASS"]]
        self.assertEqual(tp.ledger_row_findings("promotion.tsv", rows, 6, promo_check, "c"), [])
        for v in ("REQUEUED", "REVIEW-FILED", "REVIEW-WAIT", "QUEUE-FAILED", "UNVERIFIED"):
            rows = [["2026-10-23T06:32:11Z", v, SHA, "-", "d"]]
            self.assertEqual(tp.ledger_row_findings("cadence.tsv", rows, 5, cadence_check, "c"), [], v)

    def test_a_right_count_with_a_bad_field_does_not_blame_the_count(self):
        rows = [["2026-10-24T16:45:03Z", "BOGUS", "6761", SHA, "b", "p"]]
        out = tp.ledger_row_findings("promotion.tsv", rows, 6, promo_check, "c")
        self.assertEqual(len(out), 1)
        self.assertIn("field check failed", out[0])
        self.assertNotIn("got 6", out[0])

    def test_a_wrong_count_names_it(self):
        out = tp.ledger_row_findings("cadence.tsv", [["gc bd: answering from the rig"]], 5, cadence_check, "c")
        self.assertIn("want 5 cols (c), got 1", out[0])


if __name__ == "__main__":
    unittest.main()
