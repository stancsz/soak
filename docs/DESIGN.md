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

## Real-agent source workflow acceptance

The configured codex-luna gateway route now has a real CLI generator, separate deterministic validator, isolated live-trial configuration and repeatability preset. The parent independently inspected a passing fresh live trial and reconciled framework, adapter and artifact hashes; selected synthetic source outputs and the original receipt are retained under docs/evidence/clinic-source-trial. Earlier grader failures and one cancelled attempt remain in the history. Current evidence: real-agent-validation.json (28 regressions and an offline installed-wheel smoke test). This accepts source generation only; image generation, rendered PDFs, actual external research, the installed demo skill, long-duration runs, peer ranking and denied Northstar/Soak skill edits remain open.

## Bilingual rendering acceptance

An isolated Marp/Poppler rendering trial produced eight pages per language, all rasterized and inspected by the parent. The initial run exposed CJK literal emphasis markers; normalization fixed them, and all 16 final pages were reinspected. Numeric/source fingerprints and actual PDF text/page counts were checked independently. Thirty-four regressions pass; actual missing-renderer failure propagates nonzero. See rendered-clinic-validation.json and evidence/clinic-rendered-trial. Generated UI images, a fresh combined generation/render loop, long-duration/resource/load acceptance, comparative ranking and denied skill integration remain open.

## Fresh generation-to-PDF integration

One live isolated trial now covers fresh real-agent sources, source validation, actual rendering of those exact inputs, mechanical validation and independent parent inspection of all 18 pages. Thirty-eight regressions pass. Input hashes, nested validated source hashes, exact ledger bytes and the deterministic styling transformation reconcile. See integrated-clinic-validation.json. A live missing-CLI failure stops before rendering; changing a copy of the live fresh ledger is rejected. Endurance, repeated integrated exposure, generated UI images, resource/load/cost qualification, peer comparison and denied skill integration remain open.
