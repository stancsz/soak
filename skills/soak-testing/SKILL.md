---
name: soak-testing
description: Plan, run, and evaluate bounded soak tests for agent harnesses and models.
---

# Soak testing

1. Identify the actual harness, model, workload, environment, and what failure means. Establish authorized duration, request rate, concurrency, and spend before invoking a paid or shared service. Never treat synthetic results as real-system evidence.
2. Create representative cases with stable unique IDs and explicit checks. Include tool use, state or multi-turn cases only when relevant. Avoid sensitive data in cases and output.
3. Implement an adapter to the framework's stdin/stdout contract in the repository README. Verify a short smoke run against the actual target before the long run; distinguish model failures, harness failures, adapter errors, and timeouts where evidence permits.
4. Run with explicit duration, timeout, interval and maximum iterations. Monitor the process and provider budget; retain run configuration, target versions, and environment alongside results without secrets. Stop on unexpected cost, damage, or loss of control.
5. Inspect events for failure clusters and latency changes over time, compare against agreed thresholds, and report counts, elapsed time, versions, limits, and any gaps. A clean short run does not establish long-duration reliability. State whether a persistent harness was actually exercised.
