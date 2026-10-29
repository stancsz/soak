import hashlib
import json
import os
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soak.process import invoke

ENDPOINT = "http://127.0.0.1:4000/v1"
MODEL = "codex-luna"
PROFILE = "subroute-subagents"
ARTIFACTS = ["research-note.md", "deck-en.md", "deck-zh.md", "ledger.json"]
COUNTS = {"inquiries": 86, "booked": 62, "visited": 41, "associated_revenue": 16400, "currency": "USD", "period": "same synthetic reporting period", "sample": True}


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate(manifest, cwd=None):
    root = Path(cwd or os.getcwd()).resolve()
    errors = []
    for name in ARTIFACTS:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f"missing or out-of-workspace artifact: {name}")
    if errors:
        return {"passed": False, "errors": errors}
    try:
        ledger = json.loads((root / "ledger.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {"passed": False, "errors": ["ledger.json is not valid UTF-8 JSON"]}
    if not isinstance(ledger, dict):
        return {"passed": False, "errors": ["ledger must be an object"]}
    for key, expected in COUNTS.items():
        if type(ledger.get(key)) is not type(expected) or ledger.get(key) != expected:
            errors.append(f"ledger {key} does not match approved synthetic brief")
    english = (root / "deck-en.md").read_text(encoding="utf-8")
    chinese = (root / "deck-zh.md").read_text(encoding="utf-8")
    note = (root / "research-note.md").read_text(encoding="utf-8")
    for filename, text in (("deck-en.md", english), ("deck-zh.md", chinese)):
        if not text.lstrip().startswith("---") or "marp: true" not in text:
            errors.append(f"{filename} missing Marp metadata")
        if not all(str(value) in text for value in (86, 62, 41, 16400, "USD")):
            errors.append(f"{filename} missing expected figures")
        if not any(word in text.lower() for word in ("price", "pricing", "pay", "价格", "金额", "支付", "付费", "报价")):
            errors.append(f"{filename} missing pricing question")
        plain = text.replace("*", "").replace("_", "")
        zero_price = any(("零" in slide or re.search(r"(?<![0-9])0(?![0-9])", slide)) and any(word in slide.lower() for word in ("价格", "金额", "支付", "付费", "报价", "price", "pricing", "pay"))
                         for slide in re.split(r"\n---\s*\n", plain))
        if not zero_price and not any(marker in plain.lower() for marker in ("zero", "$0", "0 usd", "包括零", "零元", "0 美元")):
            errors.append(f"{filename} does not ask about zero pricing")
        if not any(marker in text.lower() for marker in ("currency", "usd", "货币", "币种")):
            errors.append(f"{filename} does not ask/specify currency")
    if not any(word in english.lower() for word in ("fictional", "unverified", "synthetic")):
        errors.append("English deck lacks fictional/unverified marker")
    if not any(word in chinese for word in ("合成", "虚构", "未经核实")):
        errors.append("Chinese deck lacks synthetic-language marker")
    if not any(word in note.lower() for word in ("hypothesis", "hypotheses")) or not any(word in note.lower() for word in ("evidence", "source")):
        errors.append("research note must separate hypotheses from evidence/sources")
    if not any("假设" in line for line in note.splitlines()) or not any("证据" in line or "来源" in line for line in note.splitlines()):
        errors.append("research note needs distinct Chinese hypothesis and evidence/source text")
    if not any("\u5047\u8bbe" in line or "\u8bca\u6240" in line or "\u5408\u6210" in line for line in chinese.splitlines()):
        errors.append("Chinese deck lacks meaningful Chinese text")
    if not ("staff" in english.lower() and "review" in english.lower() and "clinical" in english.lower() and "escalat" in english.lower()):
        errors.append("English deck lacks staff review and clinical escalation")
    if not (any(x in chinese for x in ("员工", "人工", "团队", "工作人员")) and any(x in chinese for x in ("审核", "审阅", "确认")) and any(x in chinese for x in ("临床", "医疗")) and any(x in chinese for x in ("升级", "转交", "转介"))):
        errors.append("Chinese deck lacks staff review and clinical escalation")
    return {"passed": not errors, "errors": errors}


def prompt_for(brief):
    return """You are creating source materials for a buyer-hypothesis exercise for a clinic. Treat ONLY the JSON brief below as authorized facts; all its metrics are synthetic. Do not browse, use network, contact prospects, make up citations or sources, edit skills/configuration, or claim real research, clinical outcomes, generated visuals/PDFs, or buyer validation. Use native shell tools to create exactly these four files in the current directory: research-note.md, deck-en.md, deck-zh.md, ledger.json. Do not satisfy this by printing files or copying a template. Make the research note a useful buyer hypothesis and a concrete research plan, clearly separate hypothesis from evidence/sources, and label evidence unavailable rather than inventing sources. Create useful bilingual Marp sales-source drafts (metadata marp: true) with clear narrative, staff review and clinical escalation, current workflow, and unaided pricing questions explicitly including zero and currency. Preserve the four metrics, USD and period exactly in both decks and ledger; ledger must set sample true. Include conspicuous English fictional/unverified wording and Chinese synthetic wording. Keep all claims cautious, no patient data. The note must include distinct bilingual headings for Hypothesis / 假设 and Evidence and sources / 证据与来源. The Chinese deck must be written in Chinese, including 诊所 or 假设, not a translated title over English body. Write 16400 without comma so machine-read figures match the JSON. Use the exact ledger fields in the brief: inquiries, booked, visited, associated_revenue, currency, period, sample. Use UTF-8 files. For the source-draft protocol, label the unaided pricing section explicitly and state that zero / 零 / USD 0 are valid answers; include explicit staff-review and clinical-escalation sections in each language. Do not modify installed skills or configuration or read other chat workspaces. Use native file tools directly, or write files using Python; do not invoke apply_patch through PowerShell shell command strings. Reply only with a concise JSON object listing the four filenames under artifacts; create files first.\n\nAPPROVED SYNTHETIC BRIEF:\n""" + json.dumps(brief, ensure_ascii=False, sort_keys=True)


def generate(brief):
    binary = os.environ.get("SOAK_CODEX_BIN")
    if not binary:
        raise RuntimeError("SOAK_CODEX_BIN is required")
    binary_path = Path(binary)
    if not binary_path.is_absolute() or not binary_path.is_file():
        raise FileNotFoundError("SOAK_CODEX_BIN must name an existing native Codex executable")
    prompt = prompt_for(brief)
    timeout = min(180, max(1, int(brief.get("generation_timeout", 180))))
    command = [str(binary_path), "exec", "--ephemeral", "--skip-git-repo-check", "--sandbox", "workspace-write", "--profile", PROFILE, "--model", MODEL,
               "-c", f"model_provider=\"subroute\"", "-c", f"model_providers.subroute.base_url=\"{ENDPOINT}\"",
               "-c", "model_providers.subroute.wire_api=\"responses\"", "-c", "features.plugins=false", "-c", "features.apps=false",
               "-c", "features.remote_plugin=false", "-c", "features.multi_agent=false", "-c", "features.shell_tool=true",
               "-c", "mcp_servers.browseros-neo.transport=\"streamable_http\"",
               "-c", "mcp_servers.browseros-neo.enabled=false", "-"]
    result = invoke(command, prompt, timeout, limit=65536, cwd=os.getcwd())
    if result.returncode != 0:
        raise RuntimeError("Codex CLI exited unsuccessfully")
    for name in ARTIFACTS:
        path = Path(name).resolve()
        if not path.is_relative_to(Path.cwd().resolve()) or not path.is_file():
            raise RuntimeError("agent did not create required artifact: " + name)
    version = invoke([str(binary_path), "--version"], "", 10, limit=4096, cwd=os.getcwd())
    if version.returncode:
        raise RuntimeError("Codex CLI version query failed")
    runtime = {"codex_cli_version": version.stdout.strip(), "model_alias": MODEL, "provider_profile": PROFILE, "provider": "subroute", "endpoint": ENDPOINT,
               "task_brief_sha256": digest(json.dumps(brief, ensure_ascii=False, sort_keys=True)), "prompt_sha256": digest(prompt),
               "evidence_category": "real-agent-source-generation", "visual_limits": "source drafts only; no PDF or image generation or validation",
               "research_limits": "synthetic brief only; no browsing, external research, contacts, or buyer outcome claims"}
    Path("runtime.json").write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifacts": ARTIFACTS + ["runtime.json"]}, ensure_ascii=False))


def main():
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    try:
        payload = json.load(sys.stdin)
        if mode == "generate":
            generate(payload)
            return 0
        if mode == "validate":
            result = validate(payload)
            print(json.dumps(result, ensure_ascii=False))
            return 0 if result["passed"] else 1
        raise ValueError("mode must be generate or validate")
    except Exception as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}))
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
