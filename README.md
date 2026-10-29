# Soak — Soak Testing Framework

Soak repeatedly exercises an agent harness and its model over a bounded period, recording each outcome and a summary. It is a small starting point for finding failures and latency changes that short tests can miss. The included adapter is synthetic; it does not test a real model.

## Run the example

Requires Python 3.11 or newer; no runtime dependencies.

```sh
python -m soak.cli examples/synthetic.json --output runs/example
```

The output directory must not already exist. `events.jsonl` is flushed after each iteration, and `summary.json` records the final counts. Exit codes: 0 all passed, 1 failures or no iterations, 2 configuration or filesystem error. Interrupting a run can leave events without a summary.

## Test a harness and model

Implement an adapter executable that reads one JSON case from stdin and writes one JSON object to stdout: `{"passed": true, "detail": "optional explanation"}`. The adapter invokes the actual harness and model, evaluates the result, and returns a boolean. Use stderr for diagnostics; Soak deliberately does not save stdout or stderr. Case IDs must be unique. Set `command` to an argument array, not a shell command; it runs from the current working directory. Each iteration launches a fresh process. For persistent-session or memory-leak testing, the adapter must connect to a separately managed persistent harness.

Configure duration, per-iteration timeout, interval, and optionally max_runs in JSON. Iterations run sequentially; a deadline bounds the current process timeout. Process descendants may survive a timeout depending on the operating system, so adapters must manage their own children. The framework does not enforce model spend or token budgets: use provider-side limits and an explicit bounded test budget. Never place credentials in configuration, cases, or adapter details. Events and summaries may contain case IDs and adapter details; store them appropriately.

A passing run means only that the adapter reported success on every completed iteration. Design cases and checks for your workload, record model/harness versions and environment separately, and compare latency and failure patterns over time. See [the soak-testing skill](skills/soak-testing/SKILL.md).

## Model endpoint example

`examples/model_adapter.py` calls an OpenAI-compatible chat endpoint using only the standard library. Set `SOAK_BASE_URL` (including `/v1`), `SOAK_MODEL`, and optionally `SOAK_API_KEY` in the environment, then run:

```sh
python -m soak.cli examples/model.json --output runs/model-smoke
```

This configuration permits at most five requests over 60 seconds. Its check only tests whether the expected marker appears; replace cases and evaluation for meaningful acceptance. The endpoint may be a model server or an agent harness exposing this protocol. For CLI harnesses, implement the same JSON adapter contract described above. Model endpoint testing alone does not exercise an agent's tools, persistent state, or recovery behavior.
