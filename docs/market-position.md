# Soak: market position and maturity

**Reviewed:** 2026-11-23<br>
**Product readiness:** framework prototype. The runner has bounded iteration accounting and gate checks; its bundled adapter is synthetic. One integrated clinic workflow was reviewed, not an endurance campaign.<br>
**Market validation:** hypothesis. No external team adoption, repeat-use, or commercial evidence is published.

## Audience and job

The intended user is an engineer maintaining an agent harness who wants repeat runs to expose intermittent failures, latency drift, or recovery problems that a one-shot smoke can miss. The job is to record each bounded iteration, retain a summary, and fail when the operator's declared exposure or latency gates are missed.

## Alternatives and position

| Substitute | What its first-party source establishes | Soak's testable position |
| --- | --- | --- |
| k6 and other performance-test tools | Grafana defines soak testing as extended pressure for performance/reliability issues and thresholds as explicit pass/fail criteria. | Soak focuses on repeated agent-harness iterations and adapter-reported outcomes with per-iteration receipts. It is not a load generator or replacement for service-level performance testing. |
| One-shot agent evaluations | Useful for broad benchmark or regression checks. | Soak emphasizes bounded repeated exposure and durable run accounting. It must show that repeated-run signals catch actionable failures missed by the team's normal tests. |
| Custom shell loops | Easy to write and tailor. | Soak provides a small adapter contract, timeouts, structured events, and gates. No productivity advantage is measured yet. |

Sources: [Grafana k6 soak-test glossary](https://grafana.com/docs/k6/latest/reference/glossary/) and [k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/). They describe performance-testing capabilities, not agent-specific outcome evaluation.

## Evidence and limits

- The included synthetic adapter exercises run accounting and gate behavior; it does not test a real model.
- One integrated clinic trial generated and validated bilingual materials, rendered pages, and received review of 18 pages. It is one bounded workflow, not a multi-hour reliability, resource-drift, or endurance study.
- The framework does not enforce model spend, guarantee child-process cleanup, or grade semantic quality. Adapter semantics and process management remain operator responsibilities.
- GitHub snapshot on 2026-11-23: 0 stars, 0 forks, and no published release. There is no public adoption or commercial evidence.

## Adoption friction and next experiment

Users must implement a trustworthy adapter and workload-specific evaluator, set realistic gates, manage credentials and spend limits, and ensure persistent services are monitored by the adapter. The next decision-changing study is a bounded multi-hour run against a real coding-agent harness with predeclared correctness cases, model/harness version pins, resource and cost receipts, and injected timeout/restart conditions. Compare failure detection with the team's existing short smoke and unit checks.

## Product and research values

- **Bound exposure:** duration, timeout, interval, drain window, and maximum run count are explicit.
- **Keep a durable trace:** event and summary records preserve outcomes and gate violations.
- **Define what pass means:** acceptance is the adapter's declared result for each completed iteration.
- **Keep reliability claims earned:** smoke, integrated workflow, and endurance evidence stay distinct.

## Sources

- [Project README](../README.md)
- [Design and remaining acceptance work](DESIGN.md)
- [Integrated trial guide](integrated-clinic-trials.md)
- [k6 soak-test glossary](https://grafana.com/docs/k6/latest/reference/glossary/)
- [k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/)
