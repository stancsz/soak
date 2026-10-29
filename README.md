# Soak â€” Soak Testing Framework

Soak repeatedly exercises an agent harness and its model over a bounded period, recording each outcome and a summary. It is a small starting point for finding failures and latency changes that short tests can miss. The included adapter is synthetic; it does not test a real model.

## Run the example

Requires Python 3.11 or newer; no runtime dependencies.

```sh
python -m soak.cli examples/synthetic.json --output runs/example
```

The output directory must not already exist. `events.jsonl` is flushed after each iteration, and `summary.json` records the final counts. Exit codes: 0 acceptance gates passed, 1 acceptance failed or no iterations, 2 configuration or filesystem error. A caught keyboard interrupt writes a failed summary; forced termination or filesystem failure may still leave an incomplete run. Manifests record configuration and framework implementation hashes.

## Test a harness and model

Implement an adapter executable that reads one JSON case from stdin and writes one JSON object to stdout: `{"passed": true, "detail": "optional explanation"}`. The adapter invokes the actual harness and model, evaluates the result, and returns a boolean. Use stderr for diagnostics; Soak deliberately does not save stdout or stderr. Case IDs must be unique. Set `command` to an argument array, not a shell command; it runs from the current working directory. Each iteration launches a fresh process. For persistent-session or memory-leak testing, the adapter must connect to a separately managed persistent harness.

Configure duration, per-iteration timeout, interval, and optionally max_runs in JSON. Iterations run sequentially. `duration_seconds` stops scheduling; optional `drain_seconds` gives the final iteration a bounded completion window. Per-iteration timeout still applies. Cleanup can add a small overhead. Process descendants may survive a timeout depending on the operating system, so adapters must manage their own children. The framework does not enforce model spend or token budgets: use provider-side limits and an explicit bounded test budget. Never place credentials in configuration, cases, or adapter details. Events and summaries may contain case IDs and adapter details; store them appropriately.

A passing run means only that the adapter reported success on every completed iteration. Design cases and checks for your workload, record model/harness versions and environment separately, and compare latency and failure patterns over time. See [the soak-testing skill](skills/soak-testing/SKILL.md).

## Model endpoint example

`examples/model_adapter.py` calls an OpenAI-compatible chat endpoint using only the standard library. Set `SOAK_BASE_URL` (including `/v1`), `SOAK_MODEL`, and optionally `SOAK_API_KEY` in the environment, then run:

```sh
python -m soak.cli examples/model.json --output runs/model-smoke
```

This configuration permits at most five requests over 60 seconds. Its check only tests whether the expected marker appears; replace cases and evaluation for meaningful acceptance. The endpoint may be a model server or an agent harness exposing this protocol. For CLI harnesses, implement the same JSON adapter contract described above. Model endpoint testing alone does not exercise an agent's tools, persistent state, or recovery behavior.

## Acceptance gates

Optional `gates` configuration supports `min_iterations`, `min_elapsed_seconds`, `max_failure_rate` (0ï¿½1), and `max_p95_seconds`. Missing failure-rate gates default to zero tolerated failures. Set minimum exposure explicitly for a real soak; a short smoke run proves only its observed exposure. Summaries include failure rate, nearest-rank p95 iteration latency and gate violations. See [the design and remaining acceptance work](docs/DESIGN.md).

## Self-test and real artifacts

```sh
python scripts/self_soak.py --duration 60 --output runs/self-soak
```

This injects pass, evaluation failure, malformed JSON, noisy output and timeout cases. The injected run should fail; the self-test receipt passes only if classifications and counts reconcile. It does not establish live-model or multi-hour reliability.

Adapter stdout and stderr are each limited by `output_limit_bytes` (default 65536). Oversized output fails the iteration. Timeout cleanup targets POSIX process groups or a live Windows parent tree; Windows descendants may escape when their parent has already exited. Adapters must manage their own persistent services. Exact p95 storage currently grows with iteration count.

For real artifact regression, see [the clinic subject](docs/clinic-subject.md). Set `SOAK_SUBJECT_ROOT` and run the provided clinic configuration. This checks existing sources and PDF headers; it does not render PDFs, evaluate visuals, verify research claims or regenerate the product. Missing files and paths outside the subject root fail the adapter.

## Isolated generation and validation trials

Run `python -m soak.trial examples/clinic-trial.json --output runs/clinic-trial` for one fresh synthetic clinic trial, or `python -m soak.cli examples/clinic-workflow.json --output runs/clinic-workflow` for three isolated iterations. Receipts distinguish generation and validation, record revision labels and source/artifact fingerprints, and leave missing validation unverified. See [configuration, failures and real-harness substitution](docs/isolated-trials.md).
