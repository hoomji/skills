"""verify-city trunk-promotion ledger checks (ci-h4c9). Run: python3 -m unittest test_trunk_promotion"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tempfile
from pathlib import Path
import trunk_promotion as tp

SHA = "3d6220bd56b82e469aca5c42bef15fc81aaa9166"


def promo_check(r):
    return tp.ISO.match(r[0]) and r[1] in tp.PROMO_STATES and r[2].isdigit() and tp.HEX40.match(r[3])


def cadence_check(r):
    return tp.ISO.match(r[0]) and r[1] in VERDICTS and tp.HEX40.match(r[2])


def city_with_cadence(src):
    d = Path(tempfile.mkdtemp())
    (d / "dispatch").mkdir()
    (d / "dispatch/promotion-cadence.py").write_text(src)
    return d


VERDICTS = tp.cadence_verdicts(city_with_cadence(
    'st.record("REQUEUED", a)\nst.record("REVIEW-FILED", a)\nst.record("REVIEW-WAIT", a)\nst.record("QUEUE-FAILED", a)\n'))


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


class CadenceVerdicts(unittest.TestCase):
    def test_a_verdict_the_writer_gains_is_known_without_a_doctor_edit(self):
        city = city_with_cadence('st.record("BATCH", fresh, None, "d")\n')
        self.assertIn("BATCH", tp.cadence_verdicts(city))
        self.assertIn("UNVERIFIED", tp.cadence_verdicts(city))
        self.assertNotIn("BOGUS", tp.cadence_verdicts(city))

    def test_an_absent_ledger_a_dispatch_script_names_is_not_a_missing_path(self):
        city = city_with_cadence('RECORDS = "dispatch/ledgers/feature-verification.tsv"\n')
        self.assertTrue(tp.written_by_script(city, "dispatch/ledgers/feature-verification.tsv"))
        self.assertFalse(tp.written_by_script(city, "dispatch/ledgers/nobody-writes.tsv"))


class ExecPaths(unittest.TestCase):
    def test_city_and_pack_variables_expand(self):
        o = {"exec": "bash $PACK_DIR/assets/scripts/conflict-sweep.sh", "source": "/c/packs/landing/orders/x.toml"}
        self.assertEqual(tp.exec_paths(o, "/c"), ["/c/packs/landing/assets/scripts/conflict-sweep.sh"])
        o = {"exec": "$GC_CITY_PATH/dispatch/promotion-cadence.py", "source": "/c/orders/p.toml"}
        self.assertEqual(tp.exec_paths(o, "/c"), ["/c/dispatch/promotion-cadence.py"])

    def test_an_unknown_variable_is_not_reported_as_a_path(self):
        self.assertEqual(tp.exec_paths({"exec": "$OTHER/x.sh"}, "/c"), [])


if __name__ == "__main__":
    unittest.main()
