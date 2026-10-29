"""Synthetic contract example; replace with an adapter invoking your harness."""
import json
import sys
case = json.load(sys.stdin)
print(json.dumps({"passed": case.get("expected") == "ok", "detail": "synthetic example"}))
