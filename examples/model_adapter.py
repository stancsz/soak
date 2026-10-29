"""OpenAI-compatible chat adapter. Credentials and routing come from environment."""
import json
import os
import sys
import urllib.request

case = json.load(sys.stdin)
base = os.environ["SOAK_BASE_URL"].rstrip("/")
model = os.environ["SOAK_MODEL"]
headers = {"Content-Type": "application/json"}
key = os.environ.get("SOAK_API_KEY")
if key:
    headers["Authorization"] = "Bearer " + key
payload = {"model": model, "messages": case["messages"], "max_tokens": 128}
request = urllib.request.Request(base + "/chat/completions", data=json.dumps(payload).encode(), headers=headers)
with urllib.request.urlopen(request, timeout=float(os.environ.get("SOAK_HTTP_TIMEOUT", "30"))) as response:
    result = json.load(response)
content = result["choices"][0]["message"]["content"]
expected = case["expected_contains"]
print(json.dumps({"passed": isinstance(content, str) and expected in content,
                  "detail": "expected text present" if isinstance(content, str) and expected in content else "expected text absent"}))
