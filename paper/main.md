# Soak: A Bounded Framework for Repeated Agent-Harness Evaluation

Run accounting, acceptance gates, and limits of short-duration evidence

## Abstract

Soak repeatedly invokes an adapter that evaluates an agent harness and model over a bounded period. It records outcomes and summaries, runs iterations sequentially in fresh adapter processes, and supports duration, timeout, interval, drain, and acceptance-gate settings. Its bundled synthetic adapter does not exercise a real model. One clinic trial involving inspection of 18 rendered pages appears in the project history, but this is not an endurance or reliability study. We describe execution semantics and propose a protocol separating smoke, endurance, recovery, and persistent-session evaluations. A passing run means only that the configured adapter reported success for completed iterations.

## 1. Motivation and execution

Short checks can miss failures that emerge during repeated use, such as latency drift, intermittent errors, or state accumulation. Soak records repeated outcomes under a bounded schedule [R1], but its result is only as meaningful as the adapter and workload.

Each iteration launches a fresh adapter process and iterations run sequentially. Persistent-session or memory-leak testing requires the adapter to connect to a separately managed persistent harness. Duration controls scheduling; timeouts and drain behavior bound iteration completion.

## Product and research values

Product value is a minimal, inspectable repetition loop with durable event accounting and explicit gates for exposure and latency.

- **Bounded runs:** duration, per-iteration timeout, interval, drain window, and maximum run count are explicit.
- **Inspectable evidence:** event log and summary preserve outcomes and gate violations.
- **Honest acceptance:** a pass means the configured adapter reported success for completed iterations.
- **No unsupported endurance claims:** the 18-page clinic trial was one bounded exercise, not an endurance or reliability study.

## 2. Evidence and limitations

The bundled adapter is synthetic. An OpenAI-compatible example checks its configured marker but does not by itself establish meaningful model or agent quality. One clinic trial involved inspection of 18 rendered pages; this is one bounded exercise and not multi-hour soak evidence.

Passing means the configured adapter reported success for completed iterations. It does not prove the adapter exercised the intended model path, reliability under persistent load, or that unseen failures are rare.

## 3. Evaluation plan and conclusion

Separate smoke checks, fixed-duration repeated workloads, persistent-session studies, and fault-injection studies. Define exposure and stopping conditions before a run. Report scheduled, started, completed, failed, timed-out, and drained iterations; retain hashes and sanitized configuration.

Soak provides bounded adapter-driven repetition and event accounting. Reliability conclusions require a real persistent system, sufficient exposure, and preserved failure evidence.

## References

[R1] Chen, S. Soak repository and design documentation. URL: https://github.com/stancsz/soak