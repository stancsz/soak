"""Soak adapter: generate and validate a fresh isolated trial per iteration."""
import json
import os
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soak.trial import run_trial


def main():
    case = json.load(sys.stdin)
    config = (ROOT / case.get("trial_config", "examples/clinic-trial.json")).resolve()
    if not config.is_relative_to(ROOT):
        raise ValueError("trial configuration must be inside the repository")
    base = Path(os.environ.get("SOAK_TRIAL_ROOT", ROOT / "runs/workflow-trials")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    output = base / uuid.uuid4().hex
    record = run_trial(config, output)
    print(json.dumps({"passed": record["outcome"] == "passed",
        "detail": "trial=" + output.name + "; generation=" + record["generation_status"] +
                  "; validation=" + record["validation_status"]}))


if __name__ == "__main__":
    main()
