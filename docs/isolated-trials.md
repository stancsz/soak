# Isolated clinic workflow trials

Run the deterministic synthetic example:

```console
python -m soak.trial examples/clinic-trial.json --output runs/clinic-trial-001
```

The destination must not exist. The runner creates it and a child `workspace`, sends the JSON `brief` on stdin to the generation command, and checks that its JSON output names existing relative artifact paths inside that workspace. If configured, validation receives the generation JSON and must emit JSON with a boolean `passed`. `trial.json` records separate generation/validation status, outcome, UTC time, repository revision/dirty state, hashes of the command/config representations, supplied target/harness/model/skill revision labels, and artifact paths. Prompts, command output, credentials, and full config are not copied into the record. Exit codes are 0 for passed, 1 for failed or unverified, and 2 for invalid configuration or an existing output destination. No validator means unverified, never pass.

The example fixture writes fresh bilingual Markdown hypothesis and buyer-ledger artifacts using explicitly synthetic sample data. It uses no fake PDFs and is **not real-agent generation, research, or visual proof**. To test a deliberately failed validator, copy the example JSON, point `validation_command` to a command that emits `{"passed": false}` (for example a small local script), and run it into a new output directory; the result must have `validation_status: failed` and exit 1.

A real agent CLI can replace `generation_command`; use an argument array and `{python}` / `{repo}` only where required. The runner provides the brief as JSON stdin, invokes commands from the isolated workspace, and consumes bounded output through `soak.process.invoke`. Its cwd isolation is **not a security sandbox**: commands run with the caller's permissions and may access or alter other files or use the network. Only use trusted commands. The runner checks structure and file containment, not clinical accuracy, privacy/compliance, factual research, design quality, or rendered deliverables. Independently inspect generated files, verify research against sources, and review actual rendered visuals before accepting a real workflow.

## Repeated fresh trials through Soak

```console
python -m soak.cli examples/clinic-workflow.json --output runs/clinic-workflow-001
```

The adapter creates a unique workspace and trial receipt for every iteration under `runs/workflow-trials` (override with `SOAK_TRIAL_ROOT`). This smoke example runs three deterministic synthetic generations and validations. It demonstrates isolated execution and honest failure reporting; it does not measure stochastic model/agent quality. Substitute the trusted real generator/validator in the trial configuration and supply accurate revision labels before making real-target claims. Local script arguments inside the repository are content-hashed; revision labels supplied by the caller are not independently verified. Artifact digests capture generation-time contents.

A trial also records a framework source fingerprint. Ordinary execution failures record exception types rather than echoing potentially sensitive command arguments. Full commands, briefs and stdout/stderr are not saved in the receipt. Generated artifacts themselves may contain the requested brief; use only approved input data. Validation code runs with the caller's environment and authority.
