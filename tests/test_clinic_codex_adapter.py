import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from examples import clinic_codex_adapter as adapter


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old = Path.cwd()
        os.chdir(self.root)

    def tearDown(self):
        os.chdir(self.old)
        self.temp.cleanup()

    def write_valid(self):
        (self.root / "research-note.md").write_text("# 假设 / Hypothesis\n\nNo real evidence or sources gathered. Research plan only.\n## 证据与来源 / Evidence and sources\nUnavailable.\n", encoding="utf-8")
        (self.root / "deck-en.md").write_text("---\nmarp: true\n---\n\nFictional and unverified. 86 inquiries, 62 booked, 41 visited, USD 16400. What is your current workflow? What price would you pay, including zero? State currency. Staff review; clinical escalation.\n", encoding="utf-8")
        (self.root / "deck-zh.md").write_text("---\nmarp: true\n---\n\n合成演示：86 inquiries，62 booked，41 visited，USD 16400。当前流程是什么？包括零元的价格是多少？请说明货币币种。员工审核，临床问题升级。\n", encoding="utf-8")
        (self.root / "ledger.json").write_text(json.dumps(adapter.COUNTS), encoding="utf-8")

    def test_validator_accepts_exact_synthetic_fixture(self):
        self.write_valid()
        self.assertEqual(adapter.validate({}), {"passed": True, "errors": []})

    def test_validator_rejects_ledger_mismatch_and_missing_marp(self):
        self.write_valid()
        data = json.loads((self.root / "ledger.json").read_text(encoding="utf-8"))
        data["visited"] = 42
        (self.root / "ledger.json").write_text(json.dumps(data), encoding="utf-8")
        (self.root / "deck-zh.md").write_text("synthetic draft", encoding="utf-8")
        result = adapter.validate({})
        self.assertFalse(result["passed"])
        self.assertTrue(any("ledger visited" in error for error in result["errors"]))

    def test_generation_uses_required_cli_routing_and_stdin(self):
        self.write_valid()
        binary = self.root / "codex"
        binary.touch()
        calls = []
        def fake_invoke(command, payload, timeout, limit=65536, *, cwd=None):
            calls.append((command, payload, timeout, limit, cwd))
            return type("Result", (), {"returncode": 0, "stdout": "codex-cli 1.2"})()
        with patch.dict(os.environ, {"SOAK_CODEX_BIN": str(binary)}), patch.object(adapter, "invoke", side_effect=fake_invoke), patch("builtins.print"):
            adapter.generate({"generation_timeout": 180})
        command = calls[0][0]
        self.assertTrue(any("http://127.0.0.1:4000/v1" in arg for arg in command))
        self.assertIn("codex-luna", command)
        self.assertIn("subroute-subagents", command)
        self.assertIn("workspace-write", command)
        self.assertEqual(command[-1], "-")
        self.assertEqual(calls[0][1].count("APPROVED SYNTHETIC BRIEF"), 1)
        self.assertEqual(calls[0][3], 65536)
        self.assertLessEqual(calls[0][2], 180)

    def test_zero_price_wording_and_safety_checks(self):
        self.write_valid()
        path = self.root / "deck-zh.md"
        text = path.read_text(encoding="utf-8").replace("包括零元的价格是多少？", "价格为**零**是否合适？")
        path.write_text(text, encoding="utf-8")
        self.assertTrue(adapter.validate({})["passed"])
        second = text.replace("价格为**零**是否合适？", "**零**元是否才是合适价格？")
        path.write_text(second, encoding="utf-8")
        self.assertTrue(adapter.validate({})["passed"])
        third = text.replace("价格为**零**是否合适？", "您愿意支付多少？**零也是有效答案。**请说明金额和币种。")
        path.write_text(third, encoding="utf-8")
        self.assertTrue(adapter.validate({})["passed"])
        path.write_text(text.replace("价格为**零**是否合适？", "价格是多少？"), encoding="utf-8")
        self.assertFalse(adapter.validate({})["passed"])

    def test_currency_zero_in_pricing_slide(self):
        self.write_valid()
        for name in ("deck-en.md", "deck-zh.md"):
            path = self.root/name
            text = path.read_text(encoding="utf-8")
            text = text.replace("including zero", "including USD 0").replace("包括零元的价格是多少？", "愿意支付的价格是多少？USD 0 也是有效答案。")
            path.write_text(text,encoding="utf-8")
        self.assertTrue(adapter.validate({})["passed"])

    def test_boolean_sample_is_required(self):
        self.write_valid()
        data = dict(adapter.COUNTS, sample=1)
        (self.root/"ledger.json").write_text(json.dumps(data),encoding="utf-8")
        self.assertFalse(adapter.validate({})["passed"])

    def test_missing_native_binary_fails_without_invocation(self):
        with patch.dict(os.environ, {"SOAK_CODEX_BIN": str(self.root / "absent")}), patch.object(adapter, "invoke") as invoke:
            with self.assertRaises(FileNotFoundError):
                adapter.generate({})
            invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
