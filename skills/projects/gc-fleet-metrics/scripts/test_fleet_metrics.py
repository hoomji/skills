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


class OrderSkippedTest(unittest.TestCase):
    def test_order_skipped_counts_as_a_stall_by_order_name(self):
        # gc 1.5.0 emits order.skipped when an order exits 0 but skipped scopes or steps.
        with tempfile.TemporaryDirectory() as d:
            ev = Path(d) / ".gc/events.jsonl"
            ev.parent.mkdir(parents=True)
            ev.write_text('{"type": "order.skipped", "ts": "2026-10-26T10:00:00Z", "subject": "memory-dream",'
                          ' "actor": "controller", "payload": {"outcome": "skipped"}}\n')
            m = load(d)
            out = m.events(0, 2e9)
            self.assertEqual(out["counts"], {"order.skipped": 1})
            self.assertEqual(list(out["by_agent"]["order.skipped"]), [m.agent_type("memory-dream")])


class HostRenameTest(unittest.TestCase):
    def test_launches_on_hailey_count_as_hdell(self):
        # The host was renamed hdell on 2026-10-26; older route.log lines still say hailey.
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / ".gc/runtime/route.log"
            log.parent.mkdir(parents=True)
            log.write_text("2026-10-20T04:40:20Z ROUTED gl-a -> hailey/x-run0123456789abcdef0123 ok\n")
            m = load(d)
            launch, _, _ = m.parse_route(0, 2e9, {})
            self.assertEqual(launch["0123456789abcdef0123"][1], "hdell")


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
