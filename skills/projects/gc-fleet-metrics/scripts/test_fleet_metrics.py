"""Regressions for fleet-metrics.py: python3 -m unittest test_fleet_metrics (from this directory)."""
import gzip, importlib.util, os, tempfile, unittest
from pathlib import Path


def load(city):
    os.environ["GC_CITY"] = str(city)
    spec = importlib.util.spec_from_file_location("fm", Path(__file__).with_name("fleet-metrics.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class RouteLogTest(unittest.TestCase):
    def test_nul_padding_from_a_crash_is_skipped(self):
        # A host crash mid-append leaves a run of NULs before the next line (Ryzen 2026-10-15).
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / ".gc/runtime/route.log"
            log.parent.mkdir(parents=True)
            log.write_text("2026-10-15T04:40:20Z QUEUED gl-a waiting\n" + "\x00" * 512
                           + "2026-10-15T04:40:28Z QUEUED gl-b waiting\n")
            m = load(d)
            lines = list(m.route_lines())
            self.assertTrue(all("\x00" not in l for l in lines))
            m.parse_route(0, 2e9, {})


class HostsTest(unittest.TestCase):
    def test_hosts_follow_fleet_py(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "dispatch").mkdir()
            (Path(d) / "dispatch/fleet.py").write_text(
                'HOSTS = {"ryzen": {}, "dell": {}, "gtx": {}, "hailey": {"cap": 2}}\n')
            m = load(d)
            self.assertEqual(m.HOSTS, ("ryzen", "dell", "gtx", "hailey"))
            # An idle host still gets a row; an empty unplaced bucket does not.
            self.assertEqual(sorted(m.nodes_table(0, 2e9, {}, {}, {}, {})), ["dell", "gtx", "hailey", "ryzen"])


if __name__ == "__main__":
    unittest.main()
