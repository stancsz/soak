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

    def test_insufficient_exposure_cannot_pass(self):
        config = self.config('import json; print(json.dumps(dict(passed=True)))')
        config["gates"] = {"min_iterations": 3, "min_elapsed_seconds": 10}
        summary, _ = self.execute(config)
        self.assertEqual(summary["outcome"], "fail")
        self.assertEqual(summary["gate_violations"], ["min_iterations", "min_elapsed_seconds"])

    def test_latency_gate(self):
        config = self.config('import json; print(json.dumps(dict(passed=True)))')
        config["gates"] = {"max_p95_seconds": 0}
        summary, _ = self.execute(config)
        self.assertIn("max_p95_seconds", summary["gate_violations"])

    def test_noisy_adapter_is_bounded(self):
        config = self.config('import sys; sys.stdout.write("x" * 1000000)')
        config.update(max_runs=1, output_limit_bytes=1024)
        summary, events = self.execute(config)
        self.assertEqual(summary["outcome"], "fail")
        self.assertEqual(events[0]["status"], "error")

    def test_interrupted_run_has_failed_summary(self):
        from unittest.mock import patch
        with patch("soak.runner.invoke", side_effect=KeyboardInterrupt):
            summary, events = self.execute(self.config('pass'))
        self.assertEqual(summary["termination"], "interrupted")
        self.assertIn("interrupted", summary["gate_violations"])
        self.assertEqual(events, [])

    def test_rejects_fractional_iteration_limits(self):
        config = self.config('pass')
        for value in (True, 1.5, "2"):
            config["max_runs"] = value
            with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
                run(config, Path(tmp) / "run")

    def test_bounded_drain_finishes_inflight_iteration(self):
        config = self.config('import time,json; time.sleep(0.15); print(json.dumps(dict(passed=True)))')
        config.update(duration_seconds=0.1, drain_seconds=0.5, max_runs=1)
        summary, events = self.execute(config)
        self.assertEqual(events[0]["status"], "pass")
        self.assertEqual(summary["outcome"], "pass")

    def test_rejects_duplicate_cases(self):
        config = self.config('pass')
        config["cases"] *= 2
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(ValueError):
            run(config, Path(tmp) / "run")


if __name__ == "__main__":
    unittest.main()

