import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("artifact_adapter", Path(__file__).resolve().parents[1]/"examples/artifact_adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class ArtifactTests(unittest.TestCase):
    def test_real_file_contract_and_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/"a.png").write_bytes(b"a")
            (root/"b.png").write_bytes(b"b")
            text = "marp: true\nRequired text\n![a](a.png) ![b](b.png)"
            for name in ("en", "zh"):
                (root/f"{name}.md").write_text(text)
                (root/f"{name}.pdf").write_bytes(b"%PDF-1.7")
            case = {"documents":["en.md", "zh.md"], "required_text":{"en.md":["Required text"]}}
            self.assertTrue(adapter.audit(case, root)["passed"])
            (root/"zh.md").write_text("marp: true\n![b](b.png) ![a](a.png)")
            self.assertFalse(adapter.audit(case, root)["passed"])
            (root/"zh.md").write_text(text)
            case["required_text"]["en.md"] = ["Absent text"]
            self.assertFalse(adapter.audit(case, root)["passed"])
            case["documents"] = ["../outside.md"]
            with self.assertRaises(ValueError):
                adapter.audit(case, root)
            case["documents"] = ["en.md"]
            (root/"en.md").write_text("marp: true\n![escape](../outside.png)")
            with self.assertRaises(ValueError):
                adapter.audit(case, root)
            (root/"en.md").write_text("marp: true\n![missing](missing.png)")
            with self.assertRaises(FileNotFoundError):
                adapter.audit(case, root)
