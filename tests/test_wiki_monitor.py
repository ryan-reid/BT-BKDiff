import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "wiki_monitor", Path(__file__).resolve().parents[1] / "scripts/homelab/wiki_monitor.py")
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
REVISIONS = {"repository": "a" * 40, "BKDiablo": "b" * 40, "BTDiablo": "c" * 40}


class FakeClient:
    def __init__(self, deployed=REVISIONS, busy=None):
        self.deployed = deployed
        self.busy = busy
        self.dispatches = []

    def request(self, url, **kwargs):
        return self.deployed

    def api(self, path, **kwargs):
        if "/contents/.gitmodules" in path:
            return ('[submodule "bkdiablo.mpq"]\nurl=https://github.com/example/bk\nbranch=bk/main\n'
                    '[submodule "BTDiablo"]\nurl=https://github.com/example/bt.git\nbranch=bt\n')
        if "/commits/" in path:
            source = "BKDiablo" if path.startswith("example/bk/") else "BTDiablo" if path.startswith("example/bt/") else "repository"
            return {"sha": REVISIONS[source]}
        if "/runs?" in path:
            return {"total_count": int(self.busy is not None and f"status={self.busy}&" in path)}
        if path.endswith("/dispatches"):
            self.dispatches.append(kwargs["payload"])
            return None
        raise AssertionError(path)


class TestWikiMonitor(unittest.TestCase):
    def test_unchanged_sources_do_not_dispatch(self):
        client = FakeClient()
        self.assertEqual("current", monitor.check(client))
        self.assertEqual([], client.dispatches)

    def test_each_changed_source_dispatches_and_remains_retryable(self):
        for source in REVISIONS:
            with self.subTest(source=source):
                client = FakeClient({**REVISIONS, source: "d" * 40})
                self.assertEqual("dispatched", monitor.check(client))
                self.assertEqual({"ref": "main"}, client.dispatches[0])
                self.assertEqual("dispatched", monitor.check(client))

    def test_active_runs_prevent_duplicate_dispatches(self):
        for status in ("queued", "in_progress", "waiting", "pending", "requested"):
            with self.subTest(status=status):
                client = FakeClient(None, busy=status)
                self.assertEqual("busy", monitor.check(client))
                self.assertEqual([], client.dispatches)

    def test_missing_marker_bootstraps(self):
        self.assertEqual("dispatched", monitor.check(FakeClient(None)))

    def test_bad_marker_does_not_dispatch(self):
        for marker in ([], {}, {**REVISIONS, "repository": "invalid"}):
            client = FakeClient(marker)
            with self.assertRaises(ValueError):
                monitor.check(client)
            self.assertEqual([], client.dispatches)

    def test_dry_run_does_not_dispatch(self):
        client = FakeClient(None)
        self.assertEqual("dry-run", monitor.check(client, dry_run=True))
        self.assertEqual([], client.dispatches)

    def test_network_failure_does_not_dispatch(self):
        client = FakeClient()
        def unavailable(*args, **kwargs):
            raise RuntimeError("HTTP 503")
        client.request = unavailable
        with self.assertRaisesRegex(RuntimeError, "503"):
            monitor.check(client)
        self.assertEqual([], client.dispatches)


if __name__ == "__main__":
    unittest.main()
