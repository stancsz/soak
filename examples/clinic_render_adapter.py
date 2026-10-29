"""Render approved synthetic clinic drafts as real Marp PDFs in a trial workspace."""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soak.process import invoke

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "deck-en.md": ROOT / "docs/evidence/clinic-source-trial/deck-en.md",
    "deck-zh.md": ROOT / "docs/evidence/clinic-source-trial/deck-zh.md",
    "ledger.json": ROOT / "docs/evidence/clinic-source-trial/ledger.json",
}
MAX_PAGES = 40
THEME = """
<style>
:root { --marquee: #174c45; --paper: #fbfaf6; --ink: #182825; }
section {
  box-sizing: border-box; width: 1280px; height: 720px; padding: 58px 76px;
  background: var(--paper); color: var(--ink); font-family: "Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif;
  font-size: 27px; line-height: 1.34; overflow: hidden;
}
h1 { color: var(--marquee); font-size: 46px; line-height: 1.12; }
h2 { color: var(--marquee); font-size: 35px; line-height: 1.16; }
h3 { font-size: 27px; }
table { font-size: 22px; }
blockquote { font-size: 23px; }
</style>
"""


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _which(name):
    path = shutil.which(name)
    return str(Path(path).resolve()) if path else None


def _renderer():
    node = os.environ.get("SOAK_NODE_BIN") or _which("node")
    override = os.environ.get("SOAK_MARP_CLI")
    candidates = [Path(override)] if override else sorted(
        Path(os.environ.get("LOCALAPPDATA", ""), "npm-cache", "_npx").glob("*/node_modules/@marp-team/marp-cli/marp-cli.js")
    )
    entry = next((p.resolve() for p in candidates if p.is_file()), None)
    return node, entry


def _version(command):
    try:
        result = subprocess.run(command if isinstance(command, list) else [command, "--version"], capture_output=True, text=True, timeout=5, check=False)
        return (result.stdout or result.stderr).strip().splitlines()[0] if result.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError, IndexError):
        return "unknown"


def style_source(text):
    parts = text.split("---\n", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("expected complete Marp front matter")
    body = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", parts[2])
    for dash in ("\u2011", "\u2013", "\u2014"):
        body = body.replace(dash, "-")
    return "---\nmarp: true\ntheme: default\npaginate: true\nsize: 16:9\n---\n" + THEME + "\n" + body


def _write_receipt(workspace, receipt):
    (workspace / "render.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate(workspace):
    workspace.mkdir(parents=True, exist_ok=True)
    receipt = {"status": "failed", "failure_category": None, "evidence_category": "render_of_actual_real_agent_synthetic_sources_not_new_agent_generation",
               "visual_review": "unverified", "source_sha256": {}, "versions": {}, "page_counts": {}, "resource_bounds": {"timeout_seconds_per_command": 150, "max_pages_per_pdf": MAX_PAGES, "render_dpi": 150}}
    try:
        node, marp = _renderer()
        receipt["versions"] = {"node": _version(node) if node else "unknown", "marp": "unknown", "pdfinfo": _version(_which("pdfinfo")) if _which("pdfinfo") else "unknown", "pdftoppm": _version(_which("pdftoppm")) if _which("pdftoppm") else "unknown"}
        if not node or not marp:
            receipt["failure_category"] = "renderer_unavailable"
            raise RuntimeError("Marp capability unavailable: provide node and cached Marp CLI (SOAK_NODE_BIN, SOAK_MARP_CLI)")
        pdfinfo, pdftoppm = _which("pdfinfo"), _which("pdftoppm")
        if not pdfinfo or not pdftoppm:
            receipt["failure_category"] = "poppler_unavailable"
            raise RuntimeError("Poppler pdfinfo and pdftoppm are required")
        receipt["versions"]["marp"] = _version([node, str(marp), "--version"])
        receipt["versions"]["pdfinfo"] = _version([pdfinfo, "-v"])
        receipt["versions"]["pdftoppm"] = _version([pdftoppm, "-v"])
        for name, source in SOURCES.items():
            if not source.is_file():
                receipt["failure_category"] = "approved_source_missing"
                raise RuntimeError("approved synthetic source missing: " + name)
            shutil.copyfile(source, workspace / name)
            receipt["source_sha256"][name] = digest(source)
        for name in ("deck-en.md", "deck-zh.md"):
            path = workspace / name
            text = path.read_text(encoding="utf-8")
            path.write_text(style_source(text), encoding="utf-8")
        for stem in ("deck-en", "deck-zh"):
            result = invoke([node, str(marp), "--pdf", "--allow-local-files", "--html", "--browser", "auto", "-o", stem + ".pdf", stem + ".md"], "", 150, cwd=str(workspace))
            if result.returncode:
                receipt["failure_category"] = "marp_render_failed"
                raise RuntimeError("Marp exited " + str(result.returncode))
            pdf = workspace / (stem + ".pdf")
            if not pdf.is_file() or pdf.stat().st_size == 0:
                receipt["failure_category"] = "marp_output_missing"
                raise RuntimeError("Marp did not produce a nonempty PDF: " + pdf.name)
            info = invoke([pdfinfo, str(pdf)], "", 10, cwd=str(workspace))
            if info.returncode:
                receipt["failure_category"] = "pdfinfo_failed"
                raise RuntimeError("pdfinfo failed for " + pdf.name)
            pages = next((int(line.split(":", 1)[1].strip()) for line in info.stdout.splitlines() if line.startswith("Pages:")), 0)
            if pages < 1 or pages > MAX_PAGES:
                receipt["failure_category"] = "page_limit_exceeded"
                raise RuntimeError("invalid PDF page count for " + pdf.name)
            receipt["page_counts"][pdf.name] = pages
            rendered = invoke([pdftoppm, "-png", "-r", "150", "-progress", str(pdf), stem + "-page"], "", 150, cwd=str(workspace))
            if rendered.returncode:
                receipt["failure_category"] = "page_rasterization_failed"
                raise RuntimeError("pdftoppm failed for " + pdf.name)
            images = sorted(workspace.glob(stem + "-page-*.png"))
            if len(images) != pages or any(not p.is_file() or p.stat().st_size == 0 for p in images):
                receipt["failure_category"] = "page_image_coverage_failed"
                raise RuntimeError("page image coverage incomplete for " + pdf.name)
        receipt["status"] = "passed"
        receipt["failure_category"] = None
        return {"passed": True, "artifacts": ["deck-en.md", "deck-zh.md", "ledger.json", "render.json", "deck-en.pdf", "deck-zh.pdf"] + sorted(p.name for p in workspace.glob("*-page-*.png")), "receipt": receipt}
    except Exception as exc:
        receipt["status"] = "failed"
        receipt["failure_category"] = receipt["failure_category"] or "render_error"
        receipt["error"] = str(exc)
        return {"passed": False, "artifacts": ["render.json"], "receipt": receipt, "error": str(exc)}
    finally:
        _write_receipt(workspace, receipt)


def validate(workspace, expected_ledger):
    try:
        expected = json.loads(expected_ledger)
        actual = json.loads((workspace / "ledger.json").read_text(encoding="utf-8"))
        receipts = json.loads((workspace / "render.json").read_text(encoding="utf-8"))
        counts = receipts.get("page_counts", {})
        checks = {"ledger_exact": actual == expected, "render_succeeded": receipts.get("status") == "passed",
                  "english_pdf": (workspace / "deck-en.pdf").is_file() and (workspace / "deck-en.pdf").stat().st_size > 0,
                  "chinese_pdf": (workspace / "deck-zh.pdf").is_file() and (workspace / "deck-zh.pdf").stat().st_size > 0,
                  "equal_nonzero_page_counts": counts.get("deck-en.pdf", 0) > 0 and counts.get("deck-en.pdf") == counts.get("deck-zh.pdf")}
        for stem in ("deck-en", "deck-zh"):
            count = counts.get(stem + ".pdf", 0)
            images = sorted(workspace.glob(stem + "-page-*.png"))
            checks[stem + "_all_page_images"] = count > 0 and len(images) == count and all(p.is_file() and p.stat().st_size > 0 for p in images)
        passed = all(checks.values())
        return {"passed": passed, "checks": checks, "visual_review": "unverified", "acceptance": "mechanical_only_visual_review_separate"}
    except Exception as exc:
        return {"passed": False, "checks": {"mechanical_coverage": False}, "visual_review": "unverified", "error": str(exc)}


def main():
    request = json.load(sys.stdin)
    workspace = Path.cwd().resolve()
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode == "generate":
        result = generate(workspace)
    elif mode == "validate":
        result = validate(workspace, SOURCES["ledger.json"].read_text(encoding="utf-8"))
    else:
        result = {"passed": False, "error": "mode must be generate or validate"}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
