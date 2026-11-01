import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/archive_operation.py'
spec = importlib.util.spec_from_file_location('archive_operation', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ArchiveOperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'journal.db'
        self.req = {'taskId': 'task-one', 'brandId': 'brand-one', 'slot': 'plan-v1',
                    'payload': {'title': 'private-title', 'htmlContent': '<p>private-body</p>'}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_restart_and_changed_content(self):
        with mod.connect(self.path) as db:
            first = mod.prepare(db, self.req)
        with mod.connect(self.path) as db:
            self.assertEqual(mod.prepare(db, self.req), first)
            with self.assertRaises(ValueError):
                mod.prepare(db, {**self.req, 'payload': {'title': 'other'}})
            self.assertEqual(mod.prepare(db, {**self.req, 'slot': 'plan-v2'})['state'], 'prepared')
            self.assertEqual(mod.prepare(db, {**self.req, 'brandId': 'brand-two'})['state'], 'prepared')
        data = self.path.read_bytes()
        self.assertNotIn(b'private-title', data)
        self.assertNotIn(b'private-body', data)

    def test_attempt_unknown_then_acknowledge(self):
        with mod.connect(self.path) as db:
            key = mod.prepare(db, self.req)['operationKey']
            action = {**self.req, 'operationKey': key}
            self.assertEqual(mod.transition(db, action, 'attempted')['state'], 'attempted')
        with mod.connect(self.path) as db:
            self.assertEqual(mod.prepare(db, self.req)['state'], 'attempted')
            self.assertEqual(mod.transition(db, {**action, 'recordId': 'record-one'}, 'acknowledge')['state'], 'acknowledged')
            with self.assertRaises(ValueError):
                mod.transition(db, {**action, 'recordId': 'record-two'}, 'acknowledge')
            with self.assertRaises(ValueError):
                mod.transition(db, action, 'attempted')

    def test_concurrent_processes_reuse_one_key(self):
        processes = [subprocess.Popen([sys.executable, str(SCRIPT), 'prepare', '--journal', str(self.path)],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8') for _ in range(8)]
        results = []
        for process in processes:
            out, err = process.communicate(json.dumps(self.req, ensure_ascii=False), timeout=30)
            self.assertEqual(process.returncode, 0, err)
            results.append(json.loads(out)['operationKey'])
        self.assertEqual(len(set(results)), 1)

    def test_legacy_input_and_nonfinite_payload_rejected(self):
        with mod.connect(self.path) as db:
            with self.assertRaises(ValueError):
                mod.prepare(db, {**self.req, 'payload': {'idempotencyKey': 'bad'}})
            with self.assertRaises(ValueError):
                mod.prepare(db, {**self.req, 'payload': {'value': float('nan')}})

    def test_verified_acknowledgement_requires_matching_plan_receipts(self):
        req = {**self.req, 'payload': {'workspaceScope': 'douyin', 'title': '计划', 'htmlContent': '<p>完整正文</p>'}}
        expected = {'kind': 'plan', 'brandId': req['brandId'], **req['payload']}
        record = {'id': 'record-1', **{k: v for k, v in expected.items() if k != 'kind'}}
        created = {'status': 'success', 'data': record.copy()}
        read = {'status': 'success', 'data': {'items': [record.copy()]}}
        with mod.connect(self.path) as db:
            key = mod.prepare(db, req)['operationKey']
            args = {**req, 'operationKey': key, 'expected': expected, 'createReceipt': created, 'readReceipt': read}
            with self.assertRaises(ValueError):
                mod.acknowledge_verified(db, args)
            mod.transition(db, args, 'attempted')
            cases = [
                {**args, 'expected': {**expected, 'brandId': 'other-brand'}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'items': []}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'items': [{**record, 'htmlContent': '<p>截断</p>'}]}}},
                {**args, 'payload': {**req['payload'], 'extra': 'changed'}},
                {**args, 'createReceipt': {'result': {'isError': True}}},
            ]
            for changed in cases:
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    mod.acknowledge_verified(db, changed)
                self.assertEqual(mod.prepare(db, req)['state'], 'attempted')
            verified = mod.acknowledge_verified(db, args)
            self.assertEqual((verified['state'], verified['recordId']), ('acknowledged', 'record-1'))
        self.assertNotIn('完整正文'.encode('utf-8'), self.path.read_bytes())

    def test_verified_acknowledgement_cli(self):
        req = {**self.req, 'payload': {'workspaceScope': 'douyin', 'title': '计划', 'htmlContent': '<p>正文</p>'}}
        with mod.connect(self.path) as db:
            key = mod.prepare(db, req)['operationKey']
            mod.transition(db, {**req, 'operationKey': key}, 'attempted')
        expected = {'kind': 'plan', 'brandId': req['brandId'], **req['payload']}
        record = {'id': 'r1', **{k: v for k, v in expected.items() if k != 'kind'}}
        request = {**req, 'operationKey': key, 'expected': expected,
                   'createReceipt': {'status': 'success', 'data': record},
                   'readReceipt': {'status': 'success', 'data': {'items': [record]}}}
        result = subprocess.run([sys.executable, str(SCRIPT), 'acknowledge-verified', '--journal', str(self.path)],
                                input=json.dumps(request, ensure_ascii=False), capture_output=True, text=True, encoding='utf-8', timeout=30,
                                env={**os.environ, 'PYTHONUTF8': '0'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['state'], 'acknowledged')
        self.assertNotIn('正文', result.stdout)

    def test_verified_acknowledgement_accepts_matching_keyed_read(self):
        req = {**self.req, 'payload': {'workspaceScope':'douyin','title':'计划','htmlContent':'<p>正文</p>'}}
        expected = {'kind':'plan','brandId':req['brandId'],**req['payload']}
        record = {'id':'r1',**{k:v for k,v in expected.items() if k!='kind'}}
        with mod.connect(self.path) as db:
            key = mod.prepare(db, req)['operationKey']
            args = {**req,'operationKey':key,'expected':expected,'createReceipt':{'status':'success','data':record},'readReceipt':{'status':'success','data':{'status':'found','item':record.copy()}}}
            mod.transition(db, args, 'attempted')
            bad = {**args,'readReceipt':{'status':'success','data':{'status':'found','item':{**record,'id':'other'}}}}
            with self.assertRaises(ValueError):
                mod.acknowledge_verified(db,bad)
            self.assertEqual(mod.prepare(db,req)['state'],'attempted')
            self.assertEqual(mod.acknowledge_verified(db,args)['recordId'],'r1')

    def test_lab_recovery_requires_matching_key_identity_and_full_content(self):
        req = {**self.req, 'payload': {'workspaceScope': 'douyin', 'title': '计划', 'htmlContent': '<p>完整正文</p>'}}
        with mod.connect(self.path) as db:
            key = mod.prepare(db, req)['operationKey']
            record_id = 'ai_control_center_marketing_plan_' + hashlib.sha256(json.dumps([req['brandId'], key], ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
            record = {'id': record_id, 'brandId': req['brandId'], **req['payload']}
            receipt = {'status': 'success', 'data': {'status': 'found', 'item': record}}
            args = {**req, 'operationKey': key, 'readReceipt': receipt}
            with self.assertRaises(ValueError):
                mod.acknowledge_recovered_lab(db, args)
            mod.transition(db, args, 'attempted')
            cases = [
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'not_found_unknown', 'item': None}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'deleted', 'item': None}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'found', 'item': {**record, 'id': 'other-key'}}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'found', 'item': {**record, 'brandId': 'other-brand'}}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'found', 'item': {**record, 'workspaceScope': 'wechat'}}}},
                {**args, 'readReceipt': {'status': 'success', 'data': {'status': 'found', 'item': {**record, 'htmlContent': '<p>截断</p>'}}}},
                {**args, 'payload': {**req['payload'], 'extra': 'changed'}},
                {**args, 'operationKey': 'other-key'},
                {**args, 'readReceipt': {'result': {'isError': True}}},
            ]
            for changed in cases:
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    mod.acknowledge_recovered_lab(db, changed)
                self.assertEqual(mod.prepare(db, req)['state'], 'attempted')
            result = mod.acknowledge_recovered_lab(db, args)
            self.assertEqual((result['state'], result['recordId']), ('acknowledged', record_id))
        self.assertNotIn('完整正文'.encode('utf-8'), self.path.read_bytes())

    @unittest.skipUnless(shutil.which('node'), 'Node is needed to compare the Lab ID implementation')
    def test_lab_key_digest_matches_javascript_for_unicode_brand(self):
        brand, key = '品牌🙂测试', 'key-123'
        js = "const c=require('node:crypto');const s=JSON.stringify(['品牌🙂测试','key-123']);process.stdout.write(c.createHash('sha256').update(s).digest('hex'))"
        result = subprocess.run(['node', '-e', js], capture_output=True, text=True, encoding='utf-8', timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        python_digest = hashlib.sha256(json.dumps([brand, key], ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
        self.assertEqual(result.stdout, python_digest)


if __name__ == '__main__':
    unittest.main()
