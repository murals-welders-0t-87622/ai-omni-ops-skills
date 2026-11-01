import importlib.util
import json
import unittest
from pathlib import Path

script = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/check_archive_receipt.py'
spec = importlib.util.spec_from_file_location('check_archive_receipt', script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ArchiveReceiptTests(unittest.TestCase):
    def setUp(self):
        self.expected = {'kind': 'plan', 'brandId': 'brand-a', 'workspaceScope': 'douyin', 'title': '计划', 'htmlContent': '<p>完整正文</p>'}
        self.record = {'id': 'id-1', **{k: v for k, v in self.expected.items() if k != 'kind'}}
        self.create = {'status': 'success', 'data': self.record.copy()}
        self.read = {'status': 'success', 'data': {'items': [self.record.copy()]}}

    def test_matching_record_does_not_claim_file_or_restart_verified(self):
        result = module.check(self.create, self.read, self.expected)
        self.assertEqual(result['state'], 'record_fields_match')
        self.assertFalse(result['durability_verified'])
        self.assertFalse(result['file_bytes_verified'])

    def test_same_title_with_different_id_is_not_readback(self):
        self.read['data']['items'][0]['id'] = 'id-2'
        self.assertEqual(module.check(self.create, self.read, self.expected)['state'], 'not_found_in_this_read')

    def test_keyed_found_receipt_requires_same_record_and_complete_content(self):
        read = {'status':'success','data':{'status':'found','item':self.record.copy()}}
        self.assertEqual(module.check(self.create, read, self.expected)['state'], 'record_fields_match')
        read['data']['item']['id'] = 'different-id'
        self.assertEqual(module.check(self.create, read, self.expected)['state'], 'not_found_in_this_read')
        read['data']['item'] = {**self.record, 'htmlContent':'<p>截断</p>'}
        self.assertEqual(module.check(self.create, read, self.expected)['state'], 'mismatch')

    def test_keyed_unknown_deleted_and_malformed_do_not_confirm(self):
        for status in ('deleted', 'not_found_unknown'):
            self.assertEqual(module.check(self.create, {'status':'success','data':{'status':status,'item':None}}, self.expected)['state'], 'not_found_in_this_read')
        for result in ({'status':'found','item':None},{'status':'deleted','item':self.record},{'status':'other','item':self.record}):
            with self.subTest(result=result), self.assertRaises(ValueError):
                module.check(self.create, {'status':'success','data':result}, self.expected)

    def test_wrong_brand_and_truncated_content_rejected(self):
        self.read['data']['items'][0].update(brandId='brand-b', htmlContent='<p>完整</p>')
        result = module.check(self.create, self.read, self.expected)
        self.assertEqual(result['state'], 'mismatch')
        self.assertEqual(result['mismatched_fields'], ['brandId', 'htmlContent'])

    def test_media_link_only_never_proves_actual_file(self):
        expected = {'kind': 'material', 'brandId': 'brand-a', 'workspaceScope': 'douyin', 'title': '图片', 'materialType': 'image'}
        row = {'id': 'm1', **{k: v for k, v in expected.items() if k != 'kind'}, 'fileUrl': 'https://example.invalid/image'}
        result = module.check({'status': 'success', 'data': row}, {'status': 'success', 'data': {'items': [row]}}, expected)
        self.assertEqual(result['state'], 'record_fields_match')
        self.assertFalse(result['file_bytes_verified'])

    def test_mcp_text_and_error(self):
        wrapped = {'result': {'content': [{'type': 'text', 'text': json.dumps(self.create)}]}}
        self.assertEqual(module.check(wrapped, self.read, self.expected)['state'], 'record_fields_match')
        with self.assertRaises(ValueError):
            module.check({'result': {'isError': True}}, self.read, self.expected)
