import json
import sys
import tempfile
import unittest
from pathlib import Path
from soak.runner import run


class RunnerTests(unittest.TestCase):
    def config(self, code):
        return {"duration_seconds": 2, "timeout_seconds": 1, "max_runs": 2,
                "command": [sys.executable, "-c", code], "cases": [{"id": "a"}]}

    def execute(self, config):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            summary = run(config, out)
            events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
            self.assertEqual(json.loads((out / "summary.json").read_text()), summary)
            return summary, events

    def test_success_and_failure(self):
        summary, events = self.execute(self.config('import json; print(json.dumps(dict(passed=True)))'))
        self.assertEqual((summary["iterations"], summary["failures"]), (2, 0))
        self.assertEqual(events[0]["status"], "pass")
        summary, events = self.execute(self.config('import json; print(json.dumps(dict(passed=False)))'))
        self.assertEqual((summary["outcome"], events[0]["status"]), ("fail", "fail"))

    def test_malformed_response_and_timeout(self):
        _, events = self.execute(self.config('print("bad")'))
        self.assertEqual(events[0]["status"], "error")
        config = self.config('import time; time.sleep(2)')
        config.update(timeout_seconds=0.05, max_runs=1)
        _, events = self.execute(config)
        self.assertEqual(events[0]["status"], "timeout")

    def test_rejects_duplicate_cases(self):
        config = self.config('pass')
        config["cases"] *= 2
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            run(config, Path(tmp) / "run")


if __name__ == "__main__":
    unittest.main()

