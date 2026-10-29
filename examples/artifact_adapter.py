"""Read-only artifact regression adapter. Does not assess visual or semantic quality."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys


def audit(case, root):
    root = Path(root).resolve()
    failures = []
    refs = []
    for relative in case["documents"]:
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError("document escapes subject root")
        text = path.read_text(encoding="utf-8-sig")
        if "marp: true" not in text:
            failures.append("missing Marp metadata")
        for marker in case.get("required_text", {}).get(relative, []):
            if marker not in text:
                failures.append("required text missing")
        images = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
        digests = []
        if not images:
            failures.append("no images")
        for image in images:
            asset = (path.parent / image).resolve()
            if not asset.is_relative_to(root):
                raise ValueError("image escapes subject root")
            digests.append(hashlib.sha256(asset.read_bytes()).hexdigest())
        refs.append(digests)
        pdf = path.with_suffix(".pdf")
        with pdf.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                failures.append("invalid PDF header")
    if refs and any(ref != refs[0] for ref in refs[1:]):
        failures.append("language variants use different images or ordering")
    return {"passed": not failures, "detail": "; ".join(failures) or "artifact structure and shared assets passed; visual and semantic review required"}


if __name__ == "__main__":
    print(json.dumps(audit(json.load(sys.stdin), os.environ["SOAK_SUBJECT_ROOT"])))
