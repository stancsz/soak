import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from soak.process import invoke, OutputLimitError


class ProcessTests(unittest.TestCase):
    def test_isolated_working_directory_and_stdin(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = "import sys,json;from pathlib import Path;v=json.load(sys.stdin);Path('fresh.txt').write_text(v['text']);print(json.dumps({'passed':True}))"
            result = invoke([sys.executable, '-c', code], json.dumps({'text':'fresh artifact'}), 3, cwd=tmp)
            self.assertEqual(result.returncode, 0)
            self.assertEqual((Path(tmp)/'fresh.txt').read_text(), 'fresh artifact')
            self.assertTrue(json.loads(result.stdout)['passed'])

    def test_stderr_output_is_also_bounded(self):
        with self.assertRaises(OutputLimitError):
            invoke([sys.executable, '-c', "import sys;sys.stderr.write('x'*1000000)"], '{}', 3, 1024)

    def test_timeout_is_reported(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            invoke([sys.executable, '-c', 'import time;time.sleep(3)'], '{}', 0.1)
