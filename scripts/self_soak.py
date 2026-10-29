"""Exercise runner accounting under deliberate failures. Run from the repo root."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from soak.runner import run

ADAPTER = """import json,sys,time
case=json.load(sys.stdin)
mode=case['id']
if mode=='timeout': time.sleep(3)
elif mode=='noisy': sys.stdout.write('x'*1000000)
elif mode=='malformed': print('bad json')
else: print(json.dumps({'passed':mode=='pass'}))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--duration', type=float, default=60)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    config = {'duration_seconds': args.duration, 'timeout_seconds': 0.3,
              'drain_seconds': 1, 'interval_seconds': 0.01,
              'output_limit_bytes': 1024, 'command': [sys.executable, '-c', ADAPTER],
              'cases': [{'id': mode} for mode in ('pass','fail','malformed','noisy','timeout')]}
    summary = run(config, args.output)
    counts = Counter()
    expected = {'pass':'pass','fail':'fail','malformed':'error','noisy':'error','timeout':'timeout'}
    total = failed = 0
    with (Path(args.output)/'events.jsonl').open(encoding='utf-8') as stream:
        for line in stream:
            event = json.loads(line)
            total += 1
            if event['iteration'] != total or event['status'] != expected[event['case_id']]:
                raise RuntimeError('event sequence or fault classification mismatch')
            failed += event['status'] != 'pass'
            counts[event['case_id']] += 1
    if total != summary['iterations'] or failed != summary['failures'] or summary['outcome'] != 'fail':
        raise RuntimeError('summary accounting mismatch')
    if set(counts) != set(expected) or min(counts.values()) < 2:
        raise RuntimeError('insufficient self-test exposure')
    receipt = {'self_test':'pass', 'injected_failure_run_outcome':summary['outcome'],
               'iterations':total,'failures':failed,'case_counts':dict(counts),
               'elapsed_seconds':summary['elapsed_seconds'],
               'limitations':'controlled subprocess faults; not live model or multi-hour endurance proof'}
    (Path(args.output)/'self-test.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
