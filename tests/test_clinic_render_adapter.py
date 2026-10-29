import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from examples import clinic_render_adapter as adapter


class ClinicRenderAdapterTests(unittest.TestCase):
    def test_cjk_emphasis_and_source_structure(self):
        text = "---\nmarp: true\n---\n**现有：**仅有合成简报。\n86 62 41 USD 16400\n"
        styled = adapter.style_source(text)
        self.assertIn("<strong>现有：</strong>仅有", styled)
        self.assertNotIn("**", styled)
        self.assertIn("86 62 41 USD 16400", styled)
        with self.assertRaises(ValueError):
            adapter.style_source("missing metadata")

    def test_cli_protocol_reports_missing_renderer(self):
        import os, subprocess, sys
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, SOAK_MARP_CLI=str(Path(directory)/"missing.js"))
            result = subprocess.run([sys.executable, str(Path(adapter.__file__).resolve()), "generate"], input="{}", text=True, capture_output=True, cwd=directory, env=env, timeout=15)
            self.assertEqual(result.returncode, 1)
            receipt = json.loads((Path(directory)/"render.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["failure_category"], "renderer_unavailable")
            self.assertFalse(json.loads(result.stdout)["passed"])

    def test_missing_renderer_writes_explicit_receipt(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(adapter, "_renderer", return_value=(None, None)):
            result = adapter.generate(Path(directory))
            receipt = json.loads((Path(directory) / "render.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual("renderer_unavailable", receipt["failure_category"])
            self.assertEqual("unverified", receipt["visual_review"])

    def test_render_error_is_receipted_and_fails(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(adapter, "_renderer", return_value=("node", Path("marp-cli.js"))), patch.object(adapter, "_which", side_effect=lambda name: "/bin/" + name), patch.object(adapter, "_version", return_value="test-version"), patch.object(adapter, "invoke", side_effect=RuntimeError("mock process failure")):
            result = adapter.generate(Path(directory))
            receipt = json.loads((Path(directory) / "render.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual("render_error", receipt["failure_category"])
            self.assertIn("mock process failure", receipt["error"])

    def test_nonzero_marp_exit_has_render_failure_category(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(adapter, "_renderer", return_value=("node", Path("marp-cli.js"))), patch.object(adapter, "_which", side_effect=lambda name: "/bin/" + name), patch.object(adapter, "_version", return_value="test-version"), patch.object(adapter, "invoke", return_value=type("Result", (), {"returncode": 2})()):
            result = adapter.generate(Path(directory))
            receipt = json.loads((Path(directory)/"render.json").read_text(encoding="utf-8"))
            self.assertFalse(result["passed"])
            self.assertEqual(receipt["failure_category"], "marp_render_failed")
            self.assertFalse((Path(directory)/"deck-en.pdf").exists())

    def test_validation_rejects_incomplete_mechanical_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "ledger.json").write_text('{"ok": true}', encoding="utf-8")
            (workspace / "render.json").write_text(json.dumps({"status": "passed", "page_counts": {"deck-en.pdf": 2, "deck-zh.pdf": 2}}), encoding="utf-8")
            for name in ("deck-en.pdf", "deck-zh.pdf"):
                (workspace / name).write_bytes(b"pdf")
            (workspace / "deck-en-page-1.png").write_bytes(b"png")
            result = adapter.validate(workspace, '{"ok": true}')
            self.assertFalse(result["passed"])
            self.assertFalse(result["checks"]["deck-en_all_page_images"])
            self.assertFalse(result["checks"]["deck-zh_all_page_images"])
            self.assertEqual("unverified", result["visual_review"])


if __name__ == "__main__":
    unittest.main()
