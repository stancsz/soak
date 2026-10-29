import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soak.trial import ROOT, run_trial
from examples import clinic_render_adapter as renderer

SOURCE_CONFIG = ROOT / "examples/clinic-real-agent.json"
SOURCE_NAMES = ("deck-en.md", "deck-zh.md", "ledger.json")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("artifact path missing or outside trial output: " + relative)
    return path


def _write_stages(workspace, stages):
    path = workspace / "stages.json"
    path.write_text(json.dumps(stages, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def generate(workspace):
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    source_output = workspace / "source-trial"
    rendered = workspace / "rendered"
    adapters = {name: digest(ROOT/"examples"/name) for name in (
        "clinic_integrated_adapter.py", "clinic_codex_adapter.py", "clinic_render_adapter.py")}
    stages = {"adapter_sources_sha256": adapters, "visual_review": "unverified", "evidence_category": "fresh_integrated_agent_and_render", "endurance": "unverified",
              "failure_category": None, "generation": {"status": "not_run"},
              "source_validation": {"status": "not_run"}, "render": {"status": "not_run"},
              "mechanical_validation": {"status": "not_run"}, "source_to_render_sha256": {}}
    result = {"passed": False, "artifacts": [], "stages": stages}
    try:
        source_trial = run_trial(SOURCE_CONFIG, source_output)
        stages["generation"] = {"status": source_trial.get("generation_status"), "trial_outcome": source_trial.get("outcome")}
        stages["source_validation"] = {"status": source_trial.get("validation_status"), "trial_outcome": source_trial.get("outcome")}
        if source_trial.get("generation_status") != "passed" or source_trial.get("validation_status") != "passed" or source_trial.get("outcome") != "passed":
            stages["failure_category"] = "source_generation_failed" if source_trial.get("generation_status") != "passed" else "source_validation_failed"
            result["error"] = "fresh source trial did not pass generation and validation"
            return _finish(workspace, result)
        source_workspace = source_output / "workspace"
        fresh = {name: contained(source_workspace, name) for name in SOURCE_NAMES}
        hashes = {name: digest(path) for name, path in fresh.items()}
        actual = source_trial.get("artifact_sha256", {})
        if any(actual.get(name) != hashes[name] for name in SOURCE_NAMES):
            stages["failure_category"] = "source_trial_provenance_mismatch"
            result["error"] = "fresh source bytes differ from nested validated trial receipt"
            return _finish(workspace, result)
        stages["source_to_render_sha256"] = hashes
        rendered.mkdir(parents=True, exist_ok=False)
        rendered_result = renderer.generate(rendered, sources=fresh)
        stages["render"] = {"status": "passed" if rendered_result.get("passed") else "failed",
                             "failure_category": (rendered_result.get("receipt") or {}).get("failure_category")}
        if not rendered_result.get("passed"):
            stages["failure_category"] = "render_failed"
            result["error"] = "renderer failed"
            return _finish(workspace, result)
        if not all(render_provenance(fresh, rendered, hashes).values()):
            stages["failure_category"] = "source_to_render_provenance_mismatch"
            result["error"] = "render input identity or styling transformation does not match fresh sources"
            return _finish(workspace, result)
        expected_ledger = fresh["ledger.json"].read_text(encoding="utf-8")
        validation = renderer.validate(rendered, expected_ledger)
        ledger_equal = json.loads(expected_ledger) == json.loads((rendered / "ledger.json").read_text(encoding="utf-8"))
        stage_pass = bool(validation.get("passed")) and ledger_equal
        stages["mechanical_validation"] = {"status": "passed" if stage_pass else "failed", "checks": validation.get("checks", {}), "fresh_ledger_exact": ledger_equal}
        if not stage_pass:
            stages["failure_category"] = "mechanical_validation_failed"
            result["error"] = "mechanical renderer validation failed"
            return _finish(workspace, result)
        result["passed"] = True
        result["artifacts"] = _artifact_paths(workspace)
        return _finish(workspace, result)
    except Exception as exc:
        stages["failure_category"] = stages["failure_category"] or "integration_error"
        result["error"] = type(exc).__name__
        if rendered.exists() and not (rendered / "render.json").exists():
            (rendered / "render.json").write_text(json.dumps({"status": "failed", "failure_category": "integration_error", "visual_review": "unverified"}) + "\n", encoding="utf-8")
        return _finish(workspace, result)


def _artifact_paths(workspace):
    paths = []
    for relative in ("source-trial/trial.json", "rendered/render.json"):
        if (workspace / relative).is_file():
            paths.append(relative)
    for folder in ("source-trial/workspace", "rendered"):
        base = workspace / folder
        if base.exists():
            paths.extend(path.relative_to(workspace).as_posix() for path in sorted(base.rglob("*")) if path.is_file())
    return sorted(set(paths))


def _finish(workspace, result):
    path = _write_stages(workspace, result["stages"])
    result["artifacts"] = sorted(set(_artifact_paths(workspace) + [path.relative_to(workspace).as_posix()]))
    return result


def render_provenance(fresh, rendered, hashes):
    receipt = json.loads((rendered / "render.json").read_text(encoding="utf-8"))
    checks = {}
    for name, source in fresh.items():
        copied = rendered / name
        checks[name + "_render_input_hash"] = receipt.get("source_sha256", {}).get(name) == hashes[name]
        try:
            checks[name + "_styled_copy"] = copied.is_file() and (
                digest(copied) == hashes[name] if name == "ledger.json" else
                copied.read_text(encoding="utf-8") == renderer.style_source(source.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            checks[name + "_styled_copy"] = False
    return checks


def validate(workspace, generated):
    workspace = Path(workspace).resolve()
    try:
        stages = json.loads((workspace / "stages.json").read_text(encoding="utf-8"))
        trial = json.loads(contained(workspace, "source-trial/trial.json").read_text(encoding="utf-8"))
        artifacts = generated.get("artifacts", []) if isinstance(generated, dict) else []
        manifested = {}
        for relative in artifacts:
            contained(workspace, relative)
            manifested[relative] = relative
        source_root = (workspace / "source-trial/workspace").resolve()
        render_root = (workspace / "rendered").resolve()
        actual_artifacts = _artifact_paths(workspace) + ["stages.json"]
        trial_passed = (trial.get("generation_status") == "passed" and
                        trial.get("validation_status") == "passed" and
                        trial.get("outcome") == "passed")
        live_manifest = isinstance(generated, dict) and generated.get("passed") is True
        saved_receipt = (isinstance(generated, dict) and "passed" not in generated and
                         generated.get("generation_status") == "passed" and
                         generated.get("validation_status") == "passed" and
                         generated.get("outcome") == "passed")
        live_receipt_consistent = isinstance(generated, dict) and all(
            generated.get(field, "passed") == "passed"
            for field in ("generation_status", "validation_status", "outcome"))
        successful_trial = trial_passed and live_receipt_consistent and (live_manifest or saved_receipt)
        checks = {"generated_manifest_matches_actual": set(actual_artifacts) == set(artifacts) and len(actual_artifacts) == len(artifacts),
                  "successful_trial_required": successful_trial,
                  "generation_and_validation_passed": trial_passed,
                  "stage_statuses_passed": stages["generation"]["status"] == "passed" and stages["source_validation"]["status"] == "passed" and stages["render"]["status"] == "passed" and stages["mechanical_validation"]["status"] == "passed",
                  "all_fresh_source_artifacts_manifested": all("source-trial/workspace/" + name in manifested for name in SOURCE_NAMES),
                  "all_render_artifacts_manifested": all("rendered/" + name in manifested for name in ("deck-en.md", "deck-zh.md", "ledger.json", "render.json", "deck-en.pdf", "deck-zh.pdf"))}
        for name in SOURCE_NAMES:
            source, copied = source_root / name, render_root / name
            expected = stages["source_to_render_sha256"].get(name)
            checks[name + "_fresh_source_hash"] = source.is_file() and digest(source) == expected and trial.get("artifact_sha256", {}).get(name) == expected
            checks[name + "_copied_render_present"] = copied.is_file() and ("rendered/" + name) in manifested
        checks.update(render_provenance({name: source_root/name for name in SOURCE_NAMES}, render_root, stages["source_to_render_sha256"]))
        checks["nested_source_artifacts_unchanged"] = all(
            digest(contained(source_root, name)) == expected and "source-trial/workspace/" + name in manifested
            for name, expected in trial.get("artifact_sha256", {}).items())
        checks["fresh_ledger_matches_render"] = checks["ledger.json_fresh_source_hash"] and checks["ledger.json_styled_copy"]
        fresh_ledger = (source_root / "ledger.json").read_text(encoding="utf-8")
        rendered_ledger = (render_root / "ledger.json").read_text(encoding="utf-8")
        checks["fresh_ledger_exact_bytes"] = (source_root / "ledger.json").read_bytes() == (render_root / "ledger.json").read_bytes()
        mechanical = renderer.validate(render_root, fresh_ledger)
        checks["independent_mechanical_renderer_checks"] = bool(mechanical.get("passed"))
        checks["stages_json_is_manifested"] = "stages.json" in manifested
        passed = all(checks.values())
        return {"passed": passed, "checks": checks, "visual_review": "unverified", "endurance": "unverified"}
    except Exception as exc:
        return {"passed": False, "checks": {"integrity_and_coverage": False}, "error": type(exc).__name__, "visual_review": "unverified", "endurance": "unverified"}


def main():
    request = json.load(sys.stdin)
    workspace = Path.cwd().resolve()
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode == "generate":
        result = generate(workspace)
    elif mode == "validate":
        result = validate(workspace, request)
    else:
        result = {"passed": False, "error": "mode must be generate or validate"}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
