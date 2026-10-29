# Integrated clinic trial

Run one isolated trial that first generates and validates fresh synthetic clinic source drafts through the approved Codex CLI route, then renders those exact files into bilingual PDFs and page images:

```powershell
$env:SOAK_CODEX_BIN = "<absolute path to native codex.exe>"
python -m soak.trial examples/clinic-integrated.json --output runs/clinic-integrated-run
```

`SOAK_CODEX_BIN` must point to the Codex executable. The source adapter uses the configured `subroute-subagents` profile, endpoint `http://127.0.0.1:4000/v1`, alias `codex-luna`, and `workspace-write`; the alias's upstream backend is unknown. It uses a custom source-generation protocol; the installed demo skill is not invoked. Rendering requires Node.js, an available Marp CLI (`SOAK_NODE_BIN` and `SOAK_MARP_CLI` can select them), and Poppler `pdfinfo`/`pdftoppm` on `PATH`.

The output retains the nested `source-trial/trial.json`, generated Markdown/ledger and `runtime.json`, rendered Markdown/ledger/PDFs/all page PNGs and `render.json`, plus `stages.json`. Source generation or validation failure stops before rendering while retaining receipts. Missing Codex or renderer capabilities fail nonzero; there is no snapshot fallback. The independent trial validator accepts either the live generic-runner manifest (`passed: true` plus its artifact list) or a saved successful source-trial receipt (`generation_status`, `validation_status`, and `outcome` all equal `passed`). A saved receipt with a false or contradictory `passed` value, failed or unverified status, or missing success fields is rejected. This input-schema compatibility does not weaken stage receipts, manifest coverage, fresh-source SHA-256 values, renderer input hashes, expected styling transformation, exact fresh-vs-copied ledger bytes, or renderer mechanical PDF/page-image checks; validation does not modify artifacts.

Visual review and endurance remain unverified. Passing mocked unit tests or mechanical checks does not establish a live integrated agent trial, visual quality, or endurance behavior.

The original source bytes and styled Markdown are intentionally different: render.json identifies input bytes, while the validator checks that each styled copy equals the renderer transformation of its fresh input. Adapter dependency fingerprints are retained in stages.json. Native codex.exe is required on Windows; Get-Command codex may resolve to a PowerShell shim and is not a reliable native-binary lookup.

`examples/clinic-integrated-soak.json` is a bounded three-trial repeatability preset. It has not established endurance: use an explicit duration/exposure budget and provider quotas for any longer campaign. Each nested source trial preserves its own revision, source hashes, generation and validation outcomes. The real model alias may resolve to a different upstream backend; that identity remains unknown unless independently observed.
