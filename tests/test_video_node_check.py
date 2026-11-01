import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/check_video_nodes.py'
spec = importlib.util.spec_from_file_location('check_video_nodes', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class VideoNodeTests(unittest.TestCase):
    def setUp(self):
        self.app = {'key': 'demo-video', 'configured': True,
                    'nodeInfoList': [{'nodeId': '7', 'fieldName': 'image', 'fieldType': 'IMAGE'},
                                     {'nodeId': '22', 'fieldName': 'audio', 'fieldType': 'AUDIO'},
                                     {'nodeId': '4', 'fieldName': 'duration', 'fieldType': 'LIST'}]}
        self.receipt = {'status': 'success', 'data': {'item': self.app}}
        self.selection = {'appKey': 'demo-video', 'nodes': [{'nodeId': '7', 'fieldName': 'image', 'fieldType': 'IMAGE'}]}

    def test_matching_nodes_never_prove_generation_or_cost(self):
        result = mod.check(self.receipt, self.selection)
        self.assertEqual(result['mapping_state'], 'matched')
        self.assertTrue(result['configured_indicator'])
        for key in ('required_inputs_verified', 'provider_access_verified', 'cost_authorized', 'generation_verified'):
            self.assertFalse(result[key])

    def test_wrong_type_or_missing_node_is_rejected(self):
        self.selection['nodes'] += [{'nodeId': '22', 'fieldName': 'audio', 'fieldType': 'IMAGE'},
                                    {'nodeId': '99', 'fieldName': 'image', 'fieldType': 'IMAGE'}]
        self.assertEqual([x['issue'] for x in mod.check(self.receipt, self.selection)['issues']],
                         ['type_mismatch', 'not_in_current_detail'])

    def test_wrong_app_duplicate_and_extra_value_rejected(self):
        with self.assertRaises(ValueError):
            mod.check(self.receipt, {**self.selection, 'appKey': 'other'})
        with self.assertRaises(ValueError):
            mod.check(self.receipt, {**self.selection, 'nodes': self.selection['nodes'] * 2})
        with self.assertRaises(ValueError):
            mod.check(self.receipt, {**self.selection, 'nodes': [{**self.selection['nodes'][0], 'fieldValue': 'private'}]})
        with self.assertRaises(ValueError):
            mod.check(self.receipt, {**self.selection, 'nodes': [{'nodeId': None, 'fieldName': 'image', 'fieldType': 'IMAGE'}]})
        with self.assertRaises(ValueError):
            mod.check(self.receipt, {**self.selection, 'nodes': [{'nodeId': True, 'fieldName': 'image', 'fieldType': 'IMAGE'}]})

    def test_wrapped_response_and_unconfigured(self):
        self.app['configured'] = False
        wrapped = {'result': {'content': [{'type': 'text', 'text': json.dumps(self.receipt)}]}}
        self.assertFalse(mod.check(wrapped, self.selection)['configured_indicator'])
        with self.assertRaises(ValueError):
            mod.check({'result': {'isError': True}}, self.selection)

    def test_cli_utf8_no_media_values(self):
        request = {'receipt': self.receipt, 'selection': self.selection}
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(request, ensure_ascii=False),
                                capture_output=True, text=True, encoding='utf-8', timeout=30,
                                env={**os.environ, 'PYTHONUTF8': '0'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['mapping_state'], 'matched')


if __name__ == '__main__':
    unittest.main()
