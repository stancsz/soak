import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from .process import invoke

ROOT = Path(__file__).resolve().parent.parent
MAX_CONFIG_BYTES = 65536
MAX_OUTPUT_BYTES = 65536


class ConfigError(ValueError):
    pass


def _digest(data):
    return hashlib.sha256(data).hexdigest()


def _file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _load_config(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_CONFIG_BYTES + 1)
    if len(raw) > MAX_CONFIG_BYTES:
        raise ConfigError("config exceeds size limit")
    try:
        cfg = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigError("config must be valid UTF-8 JSON") from exc
    if not isinstance(cfg, dict):
        raise ConfigError("config must be a JSON object")
    required = ("target_revision", "harness_revision", "model_revision", "skill_revision", "brief", "generation_command")
    for key in required:
        if key not in cfg:
            raise ConfigError("missing config field: " + key)
    for key in required[:4]:
        if not isinstance(cfg[key], str) or not cfg[key].strip():
            raise ConfigError(key + " must be a nonempty string")
    if not isinstance(cfg["brief"], dict):
        raise ConfigError("brief must be a JSON object")
    _validate_command(cfg["generation_command"], "generation_command")
    if cfg.get("validation_command") is not None:
        _validate_command(cfg["validation_command"], "validation_command")
    for key, default in (("generation_timeout", 120), ("validation_timeout", 60)):
        val = cfg.get(key, default)
        if not isinstance(val, (int, float)) or isinstance(val, bool) or not 0 < val <= 600:
            raise ConfigError(key + " must be between 0 and 600 seconds")
    return cfg, raw


def _validate_command(command, label):
    if not isinstance(command, list) or not command or any(not isinstance(part, str) or not part for part in command):
        raise ConfigError(label + " must be a nonempty array of strings")


def _expand(command):
    return [part.replace("{python}", sys.executable).replace("{repo}", str(ROOT)) for part in command]


def _git_facts():
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                                  text=True, timeout=3, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True,
                                    text=True, timeout=3, check=True).stdout.strip())
        return revision, dirty
    except (OSError, subprocess.SubprocessError):
        return None, None


def _parse_json(stdout):
    try:
        return json.loads(stdout)
    except (ValueError, TypeError):
        return None


def run_trial(config_path, output_path):
    try:
        cfg, config_raw = _load_config(config_path)
    except (OSError, ConfigError) as exc:
        raise ConfigError(str(exc)) from exc
    out = Path(output_path).expanduser().absolute()
    try:
        out.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ConfigError("output directory already exists") from exc
    workspace = out / "workspace"
    workspace.mkdir()
    generation_cmd = _expand(cfg["generation_command"])
    validation_cmd = _expand(cfg["validation_command"]) if cfg.get("validation_command") else None
    git_revision, git_dirty = _git_facts()
    framework_hash = hashlib.sha256()
    for source in sorted((ROOT / "soak").glob("*.py")):
        framework_hash.update(source.name.encode())
        framework_hash.update(source.read_bytes())
    command_sources = {}
    for argument in generation_cmd + (validation_cmd or []):
        path = Path(argument)
        if path.is_absolute() and path.is_relative_to(ROOT) and path.is_file():
            command_sources[path.relative_to(ROOT).as_posix()] = _file_digest(path)
    record = {
        "local_command_sources_sha256": command_sources,
        "artifact_sha256": {},
        "framework_sha256": framework_hash.hexdigest(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": git_revision,
        "git_dirty": git_dirty,
        "config_sha256": _digest(config_raw),
        "generation_command_sha256": _digest(_json_bytes(generation_cmd)),
        "validation_command_sha256": _digest(_json_bytes(validation_cmd)) if validation_cmd else None,
        "target_revision": cfg["target_revision"],
        "harness_revision": cfg["harness_revision"],
        "model_revision": cfg["model_revision"],
        "skill_revision": cfg["skill_revision"],
        "generation_status": "not_run",
        "validation_status": "unverified",
        "outcome": "unverified",
        "artifacts": [],
        "failure": None,
    }
    try:
        try:
            result = invoke(generation_cmd, json.dumps(cfg["brief"], ensure_ascii=False),
                            cfg.get("generation_timeout", 120), limit=MAX_OUTPUT_BYTES, cwd=str(workspace))
            generated = _parse_json(result.stdout)
            if result.returncode != 0 or not isinstance(generated, dict):
                raise ValueError("generation command failed or returned invalid JSON")
            paths = generated.get("artifacts")
            if not isinstance(paths, list) or not paths or any(not isinstance(p, str) or not p for p in paths):
                raise ValueError("generation JSON must contain a nonempty artifacts list")
            verified = []
            for item in paths:
                rel = Path(item)
                if rel.is_absolute() or ".." in rel.parts:
                    raise ValueError("artifact path must remain relative to workspace")
                candidate = (workspace / rel).resolve()
                if not candidate.is_relative_to(workspace.resolve()) or not candidate.is_file():
                    raise ValueError("listed artifact missing or outside workspace: " + item)
                verified.append(rel.as_posix())
            record["artifacts"] = verified
            record["artifact_sha256"] = {name: _file_digest(workspace/name) for name in verified}
            record["generation_status"] = "passed"
        except Exception as exc:
            record["generation_status"] = "failed"
            record["failure"] = "generation: " + type(exc).__name__
        if record["generation_status"] == "passed" and validation_cmd:
            try:
                validation = invoke(validation_cmd, json.dumps(generated, ensure_ascii=False),
                                    cfg.get("validation_timeout", 60), limit=MAX_OUTPUT_BYTES, cwd=str(workspace))
                parsed = _parse_json(validation.stdout)
                if validation.returncode != 0 or not isinstance(parsed, dict) or not isinstance(parsed.get("passed"), bool):
                    raise ValueError("validator failed or JSON must contain boolean passed")
                for name, digest in record["artifact_sha256"].items():
                    candidate = (workspace/name).resolve()
                    if not candidate.is_relative_to(workspace.resolve()) or _file_digest(candidate) != digest:
                        raise ValueError("validator changed generated artifacts")
                record["validation_status"] = "passed" if parsed["passed"] else "failed"
                if not parsed["passed"]:
                    record["failure"] = "validation: validator reported failed"
            except Exception as exc:
                record["validation_status"] = "failed"
                record["failure"] = "validation: " + type(exc).__name__
        record["outcome"] = "passed" if record["generation_status"] == "passed" and record["validation_status"] == "passed" else (
            "failed" if "failed" in (record["generation_status"], record["validation_status"]) else "unverified")
    finally:
        (out / "trial.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Run an isolated, bounded clinic workflow trial")
    parser.add_argument("config")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        record = run_trial(args.config, args.output)
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({"outcome": record["outcome"], "output": str(Path(args.output).absolute())}))
    return 0 if record["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
