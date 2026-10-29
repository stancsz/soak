import json
import sys
from pathlib import Path

from soak.trial import run_trial


def config(tmp_path, gen, val=None):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "target_revision": "t1", "harness_revision": "h1", "model_revision": "m1", "skill_revision": "s1",
        "brief": {"clinic_hypothesis": "synthetic"},
        "generation_command": gen, "validation_command": val,
        "generation_timeout": 10, "validation_timeout": 10,
    }), encoding="utf-8")
    return path


def test_success_is_isolated_and_recorded(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg = config(tmp_path, [sys.executable, str(repo / "examples/clinic_trial_fixture.py"), "generate"],
                 [sys.executable, str(repo / "examples/clinic_trial_fixture.py"), "validate"])
    result = run_trial(cfg, tmp_path / "out")
    assert result["outcome"] == "passed"
    assert result["generation_status"] == result["validation_status"] == "passed"
    assert all((tmp_path / "out/workspace" / p).is_file() for p in result["artifacts"])
    assert (tmp_path / "out/trial.json").is_file()
    assert len(result["artifact_sha256"]) == len(result["artifacts"])
    assert "examples/clinic_trial_fixture.py" in result["local_command_sources_sha256"]


def test_failed_generation_is_recorded(tmp_path):
    cfg = config(tmp_path, [sys.executable, "-c", "raise SystemExit(3)"])
    result = run_trial(cfg, tmp_path / "out")
    assert result["generation_status"] == "failed"
    assert result["validation_status"] == "unverified"
    assert result["outcome"] == "failed"


def test_failed_validator_is_recorded(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    cfg = config(tmp_path, [sys.executable, str(repo / "examples/clinic_trial_fixture.py"), "generate"],
                 [sys.executable, "-c", "print('{\"passed\":false}')"])
    result = run_trial(cfg, tmp_path / "out")
    assert result["generation_status"] == "passed"
    assert result["validation_status"] == "failed"
    assert result["outcome"] == "failed"


def test_traversal_artifact_rejected(tmp_path):
    cfg = config(tmp_path, [sys.executable, "-c", "import json; print(json.dumps({'artifacts':['../escape']}))"])
    result = run_trial(cfg, tmp_path / "out")
    assert result["generation_status"] == "failed"
    assert result["outcome"] == "failed"


# Keep these regressions in the dependency-free unittest command used by CI.
import tempfile
import unittest


class TrialTests(unittest.TestCase):
    def exercise(self, function):
        with tempfile.TemporaryDirectory() as tmp:
            function(Path(tmp))

    def test_success(self):
        self.exercise(test_success_is_isolated_and_recorded)

    def test_generation_failure(self):
        self.exercise(test_failed_generation_is_recorded)

    def test_validation_failure(self):
        self.exercise(test_failed_validator_is_recorded)

    def test_traversal_rejected(self):
        self.exercise(test_traversal_artifact_rejected)

    def test_missing_validator_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = config(root, [sys.executable, str(Path(__file__).resolve().parents[1]/"examples/clinic_trial_fixture.py"), "generate"])
            record = run_trial(cfg, root/"out")
            self.assertEqual(record["generation_status"], "passed")
            self.assertEqual(record["validation_status"], "unverified")
            self.assertEqual(record["outcome"], "unverified")

    def test_timeout_receipt_does_not_echo_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = config(root, [sys.executable, "-c", "import time;time.sleep(3)", "PRIVATE_COMMAND_MARKER"])
            data = json.loads(cfg.read_text())
            data["generation_timeout"] = 0.05
            cfg.write_text(json.dumps(data))
            result = run_trial(cfg, root/"out")
            self.assertEqual(result["outcome"], "failed")
            self.assertNotIn("PRIVATE_COMMAND_MARKER", (root/"out/trial.json").read_text())
