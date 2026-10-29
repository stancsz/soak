import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer


class ModelAdapterTests(unittest.TestCase):
    def test_http_contract(self):
        requests = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                requests.append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
                payload = json.dumps({"choices": [{"message": {"content": "SOAK_OK"}}]}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            env = dict(os.environ, SOAK_BASE_URL=f"http://127.0.0.1:{server.server_port}/v1", SOAK_MODEL="test-model")
            env.pop("SOAK_API_KEY", None)
            adapter = Path(__file__).resolve().parents[1] / "examples/model_adapter.py"
            for expected, passed in [("SOAK_OK", True), ("MISSING", False)]:
                result = subprocess.run([sys.executable, str(adapter)], input=json.dumps({"messages": [{"role": "user", "content": "test"}], "expected_contains": expected}), text=True, capture_output=True, env=env, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["passed"], passed)
            self.assertEqual(requests[0][0], "/v1/chat/completions")
            self.assertEqual(requests[0][1]["model"], "test-model")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
