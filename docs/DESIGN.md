# Practical reliability design

## Ask
Build a demanding agent-harness and model soak framework and a skill that continuously improves the tested product, complementary to Northstar. “Top 1%” is an ambition, not a verified ranking. No percentile claim is permitted without a defined comparison population and reproducible evaluation.

## Acceptance bar
- Explicit exposure: elapsed duration, completed iterations, per-case coverage, and load profile; early termination must not silently pass.
- Objective gates: failure rate, latency percentiles, minimum exposure and eventual resource/cost limits.
- Reliable execution: bounded output, process-tree cleanup, interruption receipts, persistent sessions, concurrency, recovery and replay.
- Evidence: target and workload identity, timestamps, configuration hashes, reproducible reports, failure categories and trends.
- Agent workloads: multi-turn state, tool failures, provider throttling, malformed output, context growth, recovery and resource leakage.
- Self-test: sustained runs of Soak with controlled faults and independently checked accounting; no mock result establishes model reliability.
- Northstar owns objective, authority, delivery and acceptance. Soak owns workload, experiment execution and evidence. Failed gates feed a bounded repair and rerun; neither skill may certify its own unverifiable quality claim.

## Comparison sources
- https://grafana.com/docs/k6/latest/testing-guides/automated-performance-testing/ — executable thresholds and automated gates.
- https://docs.locust.io/en/latest/ — extensible workload and distributed load capabilities.

## Remaining
Implement the acceptance bar in verified increments. Current runner is sequential and starts a fresh adapter per iteration. HTTP contract tests exercise a local fixture, not a live model. Independent review, sustained self-soak and Northstar integration remain required.

## Current acceptance checkpoint

Implemented: exposure/failure/latency gates; bounded per-stream subprocess capture; timeout cleanup attempts; interruption summaries; config and implementation fingerprints; a real-subject artifact adapter; a reusable fault-injection self-test command.

Remaining: persistent sessions, concurrency/load profiles, bounded long-run percentile storage, resource/token/cost limits, failure trends/replay, representative live agent trials, visual/generation checks, independent core acceptance and reproducible peer comparison. Windows descendant cleanup is best-effort if the adapter parent exits first. Short fault campaigns cannot prove multi-hour endurance.

Northstar/Soak skill integration edits were rejected by automatic approval with only 'blocked by policy'. Those skill changes remain unapplied; do not reroute the denied action. Independent framework/testing work remains authorized.

## Isolated workflow increment

One bounded codex-luna CLI worker through the configured local gateway authored the initial trial runner, offline fixture, guide and tests. Parent review added unittest discovery, safe exception recording, fingerprints and repeated-trial integration. Twenty regressions plus explicit successful and failed trial executions passed their scoped checks; see isolated-trial-validation.json. Fresh synthetic files do not establish live-agent generation quality. Original remaining criteria and the denied skill-edit boundary stay open.
