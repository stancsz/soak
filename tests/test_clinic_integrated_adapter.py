import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from examples import clinic_integrated_adapter as adapter


class IntegratedClinicTests(unittest.TestCase):
    def setup_fixture(self, root):
        source = root / "source-trial/workspace"
        source.mkdir(parents=True)
        for name, text in (("deck-en.md", "---\nmarp: true\n---\nEnglish"), ("deck-zh.md", "---\nmarp: true\n---\n中文"), ("ledger.json", '{"sample":true}')):
            (source / name).write_text(text, encoding="utf-8")
        (source / "runtime.json").write_text("{}", encoding="utf-8")
        receipt = {"generation_status": "passed", "validation_status": "passed", "outcome": "passed",
                   "artifact_sha256": {name: adapter.digest(source / name) for name in adapter.SOURCE_NAMES}}
        (root / "source-trial/trial.json").write_text(json.dumps(receipt), encoding="utf-8")

    def test_fresh_paths_and_ordered_stages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            calls = []
            def render(path, sources=None):
                calls.append(("render", sources))
                for name, source in sources.items():
                    (path / name).write_bytes(Path(source).read_bytes()) if name == "ledger.json" else (path / name).write_text(adapter.renderer.style_source(Path(source).read_text(encoding="utf-8")),encoding="utf-8")
                (path / "render.json").write_text(json.dumps({"status": "passed", "source_sha256": {name: adapter.digest(source) for name,source in sources.items()}, "page_counts": {"deck-en.pdf": 1, "deck-zh.pdf": 1}}))
                for name in ("deck-en.pdf", "deck-zh.pdf", "deck-en-page-1.png", "deck-zh-page-1.png"):
                    (path / name).write_bytes(b"artifact")
                return {"passed": True, "receipt": {"failure_category": None}}
            with patch.object(adapter, "run_trial", return_value=json.loads((root / "source-trial/trial.json").read_text())), patch.object(adapter.renderer, "generate", side_effect=render), patch.object(adapter.renderer, "validate", return_value={"passed": True, "checks": {"coverage": True}}):
                result = adapter.generate(root)
            self.assertTrue(result["passed"])
            self.assertTrue(calls)
            sources = calls[0][1]
            self.assertEqual({name: Path(path).resolve() for name, path in sources.items()}, {name: (root / "source-trial/workspace" / name).resolve() for name in adapter.SOURCE_NAMES})
            stages = json.loads((root / "stages.json").read_text())
            self.assertEqual(stages["evidence_category"], "fresh_integrated_agent_and_render")
            self.assertEqual(stages["endurance"], "unverified")
            with patch.object(adapter.renderer, "validate", return_value={"passed": True}):
                verified = adapter.validate(root, result)
            self.assertTrue(verified["passed"], verified)
            self.assertTrue(verified["checks"]["generated_manifest_matches_actual"])

    def prepare_valid_validation_stages(self, root):
        trial = json.loads((root / "source-trial/trial.json").read_text(encoding="utf-8"))
        hashes = trial["artifact_sha256"]
        stages = {"generation": {"status": "passed"}, "source_validation": {"status": "passed"},
                  "render": {"status": "passed"}, "mechanical_validation": {"status": "passed"},
                  "source_to_render_sha256": hashes}
        rendered = root / "rendered"
        rendered.mkdir(parents=True, exist_ok=True)
        for name in adapter.SOURCE_NAMES:
            source = root / "source-trial/workspace" / name
            target = rendered / name
            if name == "ledger.json":
                target.write_bytes(source.read_bytes())
            else:
                target.write_text(adapter.renderer.style_source(source.read_text(encoding="utf-8")), encoding="utf-8")
        (rendered / "render.json").write_text(json.dumps({"source_sha256": hashes, "page_counts": {"deck-en.pdf": 1, "deck-zh.pdf": 1}}), encoding="utf-8")
        for name in ("deck-en.pdf", "deck-zh.pdf", "deck-en-page-1.png", "deck-zh-page-1.png"):
            (rendered / name).write_bytes(b"artifact")
        (root / "stages.json").write_text(json.dumps(stages), encoding="utf-8")

    def test_committed_successful_receipt_revalidates_without_mutation(self):
        root = Path(__file__).resolve().parents[1] / "docs/evidence/clinic-integrated-trial"
        receipt_path = root / "trial.json"
        before = adapter.digest(receipt_path)
        generated = json.loads(receipt_path.read_text(encoding="utf-8"))
        with patch.object(adapter.renderer, "validate", return_value={"passed": True}):
            result = adapter.validate(root, generated)
        self.assertTrue(result["checks"]["successful_trial_required"], result)
        self.assertTrue(result["passed"], result)
        self.assertEqual(adapter.digest(receipt_path), before)

    def test_live_passed_manifest_still_validates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            self.prepare_valid_validation_stages(root)
            generated = {"passed": True, "artifacts": adapter._artifact_paths(root) + ["stages.json"],
                         "generation_status": "passed", "validation_status": "passed", "outcome": "passed"}
            with patch.object(adapter.renderer, "validate", return_value={"passed": True}):
                result = adapter.validate(root, generated)
            self.assertTrue(result["checks"]["successful_trial_required"], result)

    def test_unsuccessful_or_contradictory_receipts_fail_closed(self):
        receipts = (
            {"generation_status": "failed", "validation_status": "passed", "outcome": "passed"},
            {"generation_status": "passed", "validation_status": "unverified", "outcome": "passed"},
            {"generation_status": "passed", "validation_status": "passed", "outcome": "failed"},
            {"generation_status": "passed", "validation_status": "passed", "outcome": "passed", "passed": False},
            {"passed": True, "generation_status": "failed", "validation_status": "passed", "outcome": "passed"},
            {"passed": "true"},
        )
        for receipt in receipts:
            with self.subTest(receipt=receipt), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.setup_fixture(root)
                self.prepare_valid_validation_stages(root)
                generated = {"passed": True, "artifacts": adapter._artifact_paths(root) + ["stages.json"], **receipt}
                (root / "source-trial/trial.json").write_text(json.dumps({
                    **receipt,
                    "artifact_sha256": json.loads((root / "source-trial/trial.json").read_text())["artifact_sha256"],
                }), encoding="utf-8")
                with patch.object(adapter.renderer, "validate", return_value={"passed": True}):
                    result = adapter.validate(root, generated)
                self.assertFalse(result["checks"]["successful_trial_required"], result)
                self.assertFalse(result["passed"], result)

    def test_live_manifest_rejects_partial_contradictory_statuses(self):
        root = Path(__file__).resolve().parents[1] / "docs/evidence/clinic-integrated-trial"
        receipt = json.loads((root/"trial.json").read_text(encoding="utf-8"))
        for field in ("generation_status", "validation_status", "outcome"):
            for value in ("failed", "unverified", None):
                with self.subTest(field=field, value=value):
                    payload = {"passed": True, "artifacts": receipt["artifacts"], field: value}
                    result = adapter.validate(root, payload)
                    self.assertFalse(result["passed"], result)
                    self.assertFalse(result["checks"]["successful_trial_required"], result)

    def test_source_failure_prevents_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            failure = {"generation_status": "passed", "validation_status": "failed", "outcome": "failed"}
            with patch.object(adapter, "run_trial", return_value=failure), patch.object(adapter.renderer, "generate") as render:
                result = adapter.generate(root)
            render.assert_not_called()
            self.assertFalse(result["passed"])
            stages = json.loads((root / "stages.json").read_text())
            self.assertEqual(stages["failure_category"], "source_validation_failed")

    def test_render_failure_is_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            trial = json.loads((root / "source-trial/trial.json").read_text())
            def failed_render(path, sources=None):
                path.mkdir(parents=True, exist_ok=True)
                (path / "render.json").write_text(json.dumps({"status": "failed", "failure_category": "renderer_unavailable"}))
                return {"passed": False, "receipt": {"failure_category": "renderer_unavailable"}}
            with patch.object(adapter, "run_trial", return_value=trial), patch.object(adapter.renderer, "generate", side_effect=failed_render):
                result = adapter.generate(root)
            self.assertFalse(result["passed"])
            self.assertTrue((root / "rendered/render.json").exists())
            stages = json.loads((root / "stages.json").read_text())
            self.assertEqual(stages["failure_category"], "render_failed")

    def test_provenance_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.setup_fixture(root)
            trial = json.loads((root / "source-trial/trial.json").read_text())
            def render_copy(path, sources=None):
                for name, source in sources.items():
                    (path / name).write_bytes(Path(source).read_bytes()) if name == "ledger.json" else (path / name).write_text(adapter.renderer.style_source(Path(source).read_text(encoding="utf-8")),encoding="utf-8")
                (path / "render.json").write_text("{}")
                return {"passed": True, "receipt": {}}
            with patch.object(adapter, "run_trial", return_value=trial), patch.object(adapter.renderer, "generate", side_effect=render_copy):
                result = adapter.generate(root)
            (root / "source-trial/workspace/deck-en.md").write_text("tampered", encoding="utf-8")
            validation = adapter.validate(root, result)
            self.assertFalse(validation["passed"])
            self.assertFalse(validation["checks"]["deck-en.md_fresh_source_hash"])


if __name__ == "__main__":
    unittest.main()
