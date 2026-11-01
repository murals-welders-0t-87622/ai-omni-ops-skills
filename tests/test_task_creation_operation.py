import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/task_creation_operation.py'
spec = importlib.util.spec_from_file_location('task_creation_operation', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TaskCreationOperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.journal = Path(self.tmp.name) / 'journal.db'
        self.data = {'brandId': 'fake-brand-a', 'localRef': 'op-1', 'request': {
            'brand_id': 'fake-brand-a', 'goal': 'private-goal', 'scope_end': 'private-result', 'source_refs': []}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_restart_and_brand_isolation(self):
        with mod.connect(self.journal) as db:
            original = mod.prepare(db, self.data)
            mod.mark_attempted(db, {**self.data, 'operationKey': original['operationKey']})
        with mod.connect(self.journal) as db:
            result = mod.lookup(db, self.data)
            self.assertEqual(result['operationKey'], original['operationKey'])
            self.assertEqual(result['state'], 'attempted')
            self.assertEqual(mod.lookup(db, {**self.data, 'brandId': 'fake-brand-b'}), {'status': 'not_found'})
            self.assertEqual(mod.prepare(db, self.data)['state'], 'attempted')
            with self.assertRaises(ValueError):
                mod.mark_attempted(db, {**self.data, 'operationKey': original['operationKey']})
        self.assertNotIn(b'private-goal', self.journal.read_bytes())
        self.assertNotIn(b'private-result', self.journal.read_bytes())

    def test_changed_request_and_wrong_brand_rejected(self):
        with mod.connect(self.journal) as db:
            mod.prepare(db, self.data)
            for data in ({**self.data, 'brandId': 'fake-brand-b'},
                         {**self.data, 'request': {**self.data['request'], 'goal': 'changed'}},
                         {**self.data, 'request': {**self.data['request'], 'command_id': 'injected'}}):
                with self.subTest(data=data), self.assertRaises(ValueError):
                    mod.prepare(db, data)

    def test_concurrent_prepare_and_attempt(self):
        def process(action, data):
            return subprocess.Popen([sys.executable, str(SCRIPT), action, '--journal', str(self.journal)],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, encoding='utf-8')
        def collect(processes, data):
            results = []
            for p in processes:
                out, err = p.communicate(json.dumps(data), timeout=30)
                results.append((p.returncode, out, err))
            return results
        prepared = collect([process('prepare', self.data) for _ in range(6)], self.data)
        self.assertTrue(all(code == 0 for code, _, _ in prepared), prepared)
        keys = {json.loads(out)['operationKey'] for _, out, _ in prepared}
        self.assertEqual(len(keys), 1)
        attempted = {**self.data, 'operationKey': keys.pop()}
        results = collect([process('mark-attempted', attempted) for _ in range(6)], attempted)
        self.assertEqual(sum(code == 0 for code, _, _ in results), 1, results)


if __name__ == '__main__':
    unittest.main()
