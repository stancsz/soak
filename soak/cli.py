import argparse
import json
import sys
from pathlib import Path
from .runner import run


def main():
    parser = argparse.ArgumentParser(description="Run a bounded soak test")
    parser.add_argument("config", help="JSON run configuration")
    parser.add_argument("--output", required=True, help="New output directory")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        summary = run(config, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"soak: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary))
    return 0 if summary["outcome"] == "pass" else 1

if __name__ == "__main__":
    sys.exit(main())
