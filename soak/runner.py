"""Sequential, bounded runner; adapters own interaction with the system under test."""
import json
import math
import subprocess
import time
from pathlib import Path


def run(config, output):
    duration = float(config["duration_seconds"])
    timeout = float(config["timeout_seconds"])
    interval = float(config.get("interval_seconds", 0))
    max_runs = int(config.get("max_runs", 0))
    command = config["command"]
    cases = config["cases"]
    if (not all(math.isfinite(v) for v in (duration, timeout, interval)) or
            duration <= 0 or timeout <= 0 or interval < 0 or max_runs < 0 or
            not isinstance(command, list) or not command or
            not all(isinstance(x, str) and x for x in command) or
            not isinstance(cases, list) or not cases or
            not all(isinstance(c, dict) and isinstance(c.get("id"), str) and c["id"] for c in cases)):
        raise ValueError("Invalid duration, timeout, interval, max_runs, command, or cases")
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Case IDs must be unique")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    deadline = start + duration
    count = failures = 0
    with (output / "events.jsonl").open("x", encoding="utf-8") as events:
        while time.monotonic() < deadline and (not max_runs or count < max_runs):
            case = cases[count % len(cases)]
            started = time.monotonic()
            status, detail = "error", ""
            try:
                result = subprocess.run(command, input=json.dumps(case), text=True,
                                        capture_output=True, timeout=min(timeout, max(0.001, deadline-started)),
                                        check=False, encoding="utf-8")
                if result.returncode:
                    detail = f"adapter exited {result.returncode}"
                else:
                    response = json.loads(result.stdout)
                    if not isinstance(response, dict) or not isinstance(response.get("passed"), bool):
                        raise ValueError("response must contain boolean passed")
                    status = "pass" if response["passed"] else "fail"
                    detail = str(response.get("detail", ""))[:1000]
            except subprocess.TimeoutExpired:
                status, detail = "timeout", "adapter exceeded timeout or run deadline"
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                detail = f"adapter error: {type(exc).__name__}"
            elapsed = time.monotonic() - started
            count += 1
            failures += status != "pass"
            event = {"iteration": count, "case_id": case["id"], "status": status,
                     "elapsed_seconds": round(elapsed, 4), "detail": detail}
            events.write(json.dumps(event, ensure_ascii=False) + "\n")
            events.flush()
            if interval:
                time.sleep(min(interval, max(0, deadline-time.monotonic())))
    summary = {"iterations": count, "failures": failures, "elapsed_seconds": round(time.monotonic()-start, 4),
               "outcome": "pass" if count and not failures else "fail"}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
