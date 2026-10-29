# Independent integrated acceptance review

Reviewed revision: 8ef0d8f457ed602e35f4ee6c0980825125c506ad. Reviewer: nonauthor Codex CLI, codex-luna via the configured local Subroute route, read-only executor. No product edits.

## Original reviewer verdict

**Verdict: NOT READY** for this integrated implementation increment. I found one concrete acceptance defect: the committed successful trial cannot pass the adapter’s own validator.

- **Must-fix:** `examples/clinic_integrated_adapter.py:138-139` requires `generated["passed"] is True`. But the generic `soak.trial.run_trial` records the artifact manifest and statuses in `trial.json`; it does not add a `passed` field to the generation command’s JSON result. Reproduced read-only against `docs/evidence/clinic-integrated-trial`: `adapter.validate(root, trial.json)` returned `passed: false`, with `successful_trial_required: false`; the other 22 checks were true. So the evidence’s reported successful outcome does not establish an independently accepted trial through the current validator. This defect must be resolved and the validator rerun before acceptance.
- **Verified otherwise:** at the requested HEAD, independently hashed all 31 manifested trial artifacts with no missing files or digest mismatches; adapter source hashes in `stages.json` match the checked-in adapter files. The fresh source hashes reconcile with the nested trial and renderer receipt; the ledger preserves `86 / 62 / 41 / USD 16400`, the period, and `sample: true`. The receipt reports two nine-page PDFs and page images; visual review and endurance remain explicitly unverified.
- **Checks run:** focused integrated-adapter tests passed (4/4) via `PYTHONPATH=<repo>; python -B tests/test_clinic_integrated_adapter.py -v`. The separate committed-fixture validator check reproduced the failure above. I did not inspect PNGs myself; parent visual review is reported, not independently verified here. No live generation or product writes performed.
- **Scope boundary:** full owner scope is not complete: the reusable framework, companion soak-testing skill, and Northstar interoperability were not independently accepted here; the skill edits remain unapplied. No endurance, top-percentile, generated-UI, market, or buyer-validation claim is established. READY for a targeted recheck after the validator mismatch is fixed; no implementation changes made.

## Commander scope clarification

The live runner passes the raw generator JSON, which includes passed:true; the saved receipt uses a different schema. The live integrated run was valid under that contract. The reported failure is retained as a saved-receipt audit/replay gap. One scoped write-enabled worker is assigned explicit support for successful saved receipts while preserving rejection of failed, unverified and contradictory payloads. Original source/PDF receipts will remain unchanged. A targeted nonauthor recheck is pending.

## Targeted nonauthor recheck

The read-only recheck followed one bounded write-enabled codex-luna repair assignment and a parent correction for partial contradictory status fields. Original source and PDF receipts were not modified. No new live generation, rendering, skill write or permission change occurred.

**Verdict: READY** for the integrated implementation and saved-receipt replay fix.

- The focused suite passed: 8 tests via `python -B -m unittest discover -s tests -p test_clinic_integrated_adapter.py -v`.
- Direct, unmocked validation of the committed `trial.json` passed all 23 checks. No flags were inserted; the receipt was not modified.
- Independent probes rejected failed, unverified, malformed, false-flag, and partially contradictory status inputs.
- The live manifest path remains covered by a passing regression test. `git diff --check` passed.
- No concrete must-fix found in the scoped diff. The worktree also contains an untracked prior-review report; I left it untouched.

This verdict is limited to the requested integrated acceptance and replay fix; it does not accept the full aspirational owner goal or verify visual quality, endurance, or live generation. No temp-permission failure occurred.

## Current code and checks

Parent full regression: 42 tests passed. Nonauthor focused regression: 8 tests passed. Nonauthor unmocked replay: all 23 checks passed. Original live generation consumed the generator manifest as designed; the repair adds direct saved-receipt support for operators. The original producer fingerprints remain historical evidence, and are not relabelled as new producer fingerprints.

Integrated adapter SHA-256 at acceptance: `d9e8bdac9bc4eb61b3dab094d8a59ccae87a8037083214acc0fbe858a1685ade`.

Remote main was independently checked through `gh api repos/stancsz/soak/commits/main` and matched local 8ef0d8f457ed602e35f4ee6c0980825125c506ad before this repair. Final publication is checked separately after commit.

## Owner scope and remaining authority

The reusable framework/package, bounded self-test tooling, selected clinic subject, one real integrated source-to-PDF trial, original and derived provenance, failure receipts and scoped nonauthor implementation acceptance are delivered with their stated evidence. Broader quality ambitions remain unclaimed. No additional endurance budget, generated UI feature, or percentile-ranking gate is inferred for this accepted increment.

The companion skill source exists but still has its original minimal instructions. The requested skill-led repair/improvement workflow and complementary Northstar guidance are unapplied. The earlier combined operation editing the repository Soak and Northstar SKILL.md files was rejected with only `blocked by policy`. That same denied operation has not been retried or rerouted. Completing those explicit owner requirements requires the execution boundary to permit those edits. No further mandatory code defect was identified by this scoped review.
