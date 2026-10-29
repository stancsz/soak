# Soak design and current acceptance

## Owner request

Build a useful, practical soak-testing framework for agent harnesses and models, a companion skill that drives testing and continuous improvement, and careful complementary integration with Northstar. Use the owner-selected clinic research/demo chat as a real test subject. The stated top-1% quality ambition has not been demonstrated and is not presented as a measured ranking.

## Responsibilities

Soak keeps a small reusable Python core and explicit subprocess adapter boundary. It owns workload execution, bounded capture/timeouts, acceptance gates, per-iteration evidence and isolated trial receipts. Target-specific generation, evaluation and rendering stay in adapters. Northstar should own the objective, authority, repair priority and final delivery decision; Soak should provide experiments and evidence when sustained/repeated behavior affects that objective. This skills interoperability is designed but unapplied under the denied edit boundary.

## Delivered evidence

| Outcome | Current evidence and limits |
| --- | --- |
| Independent framework repository/package | Private GitHub repository, standard-library runtime, wheel build/install and installed-runner smoke; checkout examples remain separate |
| Practical execution and gates | Duration/iteration limits, bounded per-stream output, drain window, failure/latency/exposure gates, interruption and version receipts |
| Soak the framework | Reusable fault-injection self-test; historical 60-second campaign reconciled all injected outcomes; no endurance qualification claimed |
| Selected real subject | Actual clinic artifacts, real Codex source generation and a fresh integrated source-validation/rendering trial using approved synthetic inputs |
| Traceable integrated result | Nested trial receipts, original source hashes, deterministic styled derivatives, matching ledgers, actual PDFs and every page PNG |
| Functional and visual checks | 42 current regressions; one integrated trial; all 18 pages inspected by parent; no visible clipping/glyph/numeric fault found in those artifacts |
| Nonauthor implementation acceptance | READY for integrated code plus saved-receipt replay repair: eight focused regressions and unmocked 23-check replay independently passed |
| Companion skill improvement and Northstar changes | Existing minimal skill source; requested improvements unapplied because the editing operation was policy-denied |

Current acceptance chain: [acceptance review](acceptance-review-2026-10-29.md). The original live trial and page checks remain under [integrated evidence](evidence/clinic-integrated-trial); its producer fingerprints identify the historical producer, while the replay-validator repair is separately reviewed. Previous receipts describe their own revisions and environments.

## Required remaining work

Complete the companion skill's verified framework usage and bounded test/repair/retest guidance, and the requested Northstar interoperability. The earlier operation editing both repository SKILL.md files returned only `blocked by policy`; those edits remain unapplied and the operation has not been rerouted. The next required step depends on that execution boundary changing.

## Capability limits, not newly imposed acceptance gates

The runner is sequential and uses fresh adapter processes. Persistent-session lifecycle, richer load/concurrency, bounded percentile storage at extreme iteration counts, provider token/spend enforcement and additional trend/replay capabilities are not implemented. Windows descendant cleanup is best-effort if the adapter parent exits first. The framework may exercise separately managed persistent targets through an adapter.

A smoke test, injected fault campaign, reviewed synthetic PDF, or recorded plan supports only its observed scope. Endurance needs an explicitly selected duration/exposure and evidence; no new budget is invented here. Generated UI mockups, actual market research, buyer validation and peer ranking are not proved by this clinic trial and are not added as mandatory gates for the accepted code increment.

## Reference inputs

- https://grafana.com/docs/k6/latest/testing-guides/automated-performance-testing/ - explicit automated thresholds.
- https://docs.locust.io/en/latest/ - workload extensibility and load-generation reference.

These informed design decisions; they do not establish parity or a percentile ranking.
