# Real-agent clinic source-draft trial

This repo-local generator asks Codex CLI to create four source artifacts in an isolated trial workspace: `research-note.md`, `deck-en.md`, `deck-zh.md`, `ledger.json`, plus runtime provenance in `runtime.json`. It is real CLI generation, not fixture/template substitution. It is not the complete visual/deck workflow.

Set `SOAK_CODEX_BIN` to the absolute path of the native Codex executable (not a `.cmd` shim). The configured route is the `subroute-subagents` profile, `codex-luna` alias, and explicit `http://127.0.0.1:4000/v1` Responses endpoint; underlying model identity is unknown. Preserve existing environment and permissions. No credentials are serialized. The generator sets ephemeral execution, workspace-write sandboxing, disables plugins/apps/remote_plugin/multi_agent, enables shell_tool, and passes the task on stdin using `-`. No bypass, ignore-rule, or config-discovery override is used. It performs no live trial itself.

From the repository root, run `python -m soak.trial examples/clinic-real-agent.json --output <new-output-dir>`. The deterministic validator checks exact synthetic ledger values, expected figures and safety/pricing language in both Marp sources, and source-note structure. It does not use a model grader. Parent acceptance requires independent inspection.

The brief contains only synthetic values: 86 inquiries, 62 booked, 41 visited, USD 16400 associated revenue for the same synthetic reporting period. No external sources are provided or fabricated; research is a buyer hypothesis and a plan, not completed research. Drafts must include staff review, clinical escalation, current workflow, and unaided pricing including zero and currency. No patient details or buyer outcomes are asserted.

**Limits:** This checkpoint validates source files only. No PDF rendering, image generation, visual inspection, external research, contact, clinical validation, or buyer-outcome evidence is included.

**Failure example:** missing `SOAK_CODEX_BIN` returns a JSON error and nonzero exit; the trial records generation failure, does not run validation, and must not be represented as a successful agent trial.

## Repeated trials

`python -m soak.cli examples/clinic-real-soak.json --output runs/clinic-real-soak` runs up to three fresh isolated source-generation trials. The native executable environment variable must be set for every process. Per-trial generation and validation have independent limits; this preset is a repeatability smoke test, not endurance qualification. Set provider-side quotas before longer paid/shared-service campaigns. No live network research or contacts are part of the approved synthetic task. Each iteration retains its workspace and receipt under runs/workflow-trials.

The configuration uses absolute repository/executable placeholders when switching into trial workspaces. CLI startup uses the same features.* and mcp_servers.* overrides as the proven worker dispatch; it never bypasses execpolicy or changes saved configuration. The parent independently reviews actual output rather than equating the deterministic validator with complete quality acceptance.

## Grader validation and retained failures

Early real-agent runs generated coherent sources but failed narrow Chinese phrase checks. Corrected checks normalize Markdown and accept zero options within a pricing section, including zero, 零 and USD 0, plus equivalent staff wording such as 工作人员. Positive wording variants and negative examples are checked before further live inference. Earlier trial.json outcomes remain failed; separate validation-review-final.json files record regrades of unchanged artifacts and their grader fingerprint. A regrade is not another successful generation.

Deterministic checks cover explicit structure and invariants; they do not establish persuasive sales writing, factual research quality, natural bilingual equivalence, or visual quality. The parent reviews source content separately. Generated sources intentionally disclose synthetic data and unverified hypotheses; they are not finished buyer-facing visual demos. Validators may not mutate and certify generated files in one step; source fingerprints are checked after validation.
