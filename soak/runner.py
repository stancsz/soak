"""Sequential, bounded runner; adapters own interaction with the system under test."""
import json
import hashlib
import platform
from datetime import datetime, timezone
from .process import invoke
import math
import subprocess
import time
from pathlib import Path


def run(config, output):
    duration = float(config["duration_seconds"])
    timeout = float(config["timeout_seconds"])
    interval = float(config.get("interval_seconds", 0))
    drain = float(config.get("drain_seconds", 0))
    max_runs = config.get("max_runs", 0)
    if isinstance(max_runs, bool) or not isinstance(max_runs, int):
        raise ValueError("max_runs must be a nonnegative integer")
    command = config["command"]
    cases = config["cases"]
    if (not all(math.isfinite(v) for v in (duration, timeout, interval, drain)) or
            duration <= 0 or timeout <= 0 or interval < 0 or drain < 0 or max_runs < 0 or
            not isinstance(command, list) or not command or
            not all(isinstance(x, str) and x for x in command) or
            not isinstance(cases, list) or not cases or
            not all(isinstance(c, dict) and isinstance(c.get("id"), str) and c["id"] for c in cases)):
        raise ValueError("Invalid duration, timeout, interval, max_runs, command, or cases")
    if len({c["id"] for c in cases}) != len(cases):
        raise ValueError("Case IDs must be unique")
    gates = config.get("gates", {})
    allowed = {"min_iterations", "min_elapsed_seconds", "max_failure_rate", "max_p95_seconds"}
    if not isinstance(gates, dict) or set(gates) - allowed:
        raise ValueError("Unknown acceptance gate")
    for name, value in gates.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid gate: {name}")
    if "min_iterations" in gates and not isinstance(gates["min_iterations"], int):
        raise ValueError("min_iterations must be an integer")
    if gates.get("max_failure_rate", 1) > 1:
        raise ValueError("max_failure_rate must be between 0 and 1")
    output_limit = config.get("output_limit_bytes", 65536)
    if isinstance(output_limit, bool) or not isinstance(output_limit, int) or output_limit < 1024:
        raise ValueError("output_limit_bytes must be an integer >= 1024")
    latencies = []
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    implementation = hashlib.sha256()
    for source in sorted(Path(__file__).parent.glob("*.py")):
        implementation.update(source.name.encode())
        implementation.update(source.read_bytes())
    identity = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    (output / "manifest.json").write_text(json.dumps({"schema_version": 1,
        "config_sha256": identity, "implementation_sha256": implementation.hexdigest(),
        "python_version": platform.python_version(), "started_at": datetime.now(timezone.utc).isoformat(),
        "case_ids": [c["id"] for c in cases]}, indent=2), encoding="utf-8")
    interrupted = False
    start = time.monotonic()
    deadline = start + duration
    count = failures = 0
    try:
        with (output / "events.jsonl").open("x", encoding="utf-8") as events:
            while time.monotonic() < deadline and (not max_runs or count < max_runs):
                case = cases[count % len(cases)]
                started = time.monotonic()
                status, detail = "error", ""
                try:
                    result = invoke(command, json.dumps(case),
                                    min(timeout, max(0.001, deadline + drain - started)), output_limit)
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
                latencies.append(elapsed)
                count += 1
                failures += status != "pass"
                event = {"iteration": count, "case_id": case["id"], "status": status,
                         "elapsed_seconds": round(elapsed, 4), "detail": detail,
                         "timestamp": datetime.now(timezone.utc).isoformat()}
                events.write(json.dumps(event, ensure_ascii=False) + "\n")
                events.flush()
                if interval:
                    time.sleep(min(interval, max(0, deadline-time.monotonic())))
    except KeyboardInterrupt:
        interrupted = True
    total_elapsed = time.monotonic()-start
    summary = {"iterations": count, "failures": failures, "elapsed_seconds": round(total_elapsed, 4),
               "outcome": "pass" if count and not failures else "fail"}
    summary["termination"] = "interrupted" if interrupted else ("max_runs" if max_runs and count >= max_runs else "duration")
    ordered = sorted(latencies)
    p95 = ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)] if ordered else None
    rate = failures / count if count else 1
    violations = []
    if interrupted:
        violations.append("interrupted")
    if count < gates.get("min_iterations", 1):
        violations.append("min_iterations")
    if total_elapsed < gates.get("min_elapsed_seconds", 0):
        violations.append("min_elapsed_seconds")
    if rate > gates.get("max_failure_rate", 0):
        violations.append("max_failure_rate")
    if "max_p95_seconds" in gates and (p95 is None or p95 > gates["max_p95_seconds"]):
        violations.append("max_p95_seconds")
    summary.update(p95_seconds=p95, failure_rate=rate, gate_violations=violations,
                   outcome="pass" if count and not violations else "fail")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary
