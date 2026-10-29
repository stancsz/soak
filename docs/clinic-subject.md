# Real subject: aesthetic-clinic research and bilingual demos

Owner-selected chat: 01a18699-39b3-7812-b292-8187f6460b77 (研究北美医美行业痛点). Its actual workflow includes research, buyer hypotheses, generated screens, bilingual Marp/PDF demos and skill evaluation. Observed failures include inconsistent numbers, count/currency confusion, cross-screen identity drift and PDF clipping.

Set SOAK_SUBJECT_ROOT to that chat workspace, then run `python -m soak.cli examples/clinic-artifacts.json --output runs/clinic-artifacts` from this checkout. The adapter reads existing v4 artifacts without modifying the source chat. It checks Marp metadata, selected mandatory copy, image reuse/order and PDF headers. It does not inspect rendering or image text, prove market claims or buyer demand, or demonstrate repeatable generation. The source chat was active when inspected.

For full workflow trials, use isolated workspaces and record harness/model/skill revisions. Independently evaluate evidence versus hypotheses, competing products, buyer workflows, image-first sequencing, exact navigation, sample identities/numbers/units, bilingual asset reuse, every rendered PDF page and unaided pricing questions. Retain failed candidates and repair lineage. Reuse observed failures as held-out regression cases and preserve original thresholds. No prospect contact or clinical decisions are part of this test.

## First observed run

2026-10-29: 30 seconds, 90 completed artifact audits, zero reported failures, p95 iteration latency 0.1604 seconds. Minimum exposure gates passed. Local receipt: runs/clinic-artifacts-1/summary.json and events.jsonl (ignored runtime artifacts). This is a short read-only regression run against real existing artifacts, not an endurance qualification or repeated generation trial. Six existing tests passed after the run; additional output-limit and interruption regressions were added afterward.
