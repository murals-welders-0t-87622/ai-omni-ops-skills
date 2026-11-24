import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts'
sys.path.insert(0, str(SCRIPTS))
import brand_workspace as kb


class BrandKnowledgeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = kb.workspace(temp.name, 'brand-A', True)
        kb.initialize(self.root)

    def test_all_areas_and_manual_upload_survive_reentry(self):
        manual = self.root/'知识库/品牌增长/产品资料库/试用资料.txt'
        manual.write_text('一个客户选择它的原因', encoding='utf-8')
        self.assertEqual(kb.initialize(self.root)['newPrincipleFiles'], 0)
        for parts, _ in kb.AREAS.values():
            self.assertTrue((self.root.joinpath('知识库', *parts)/kb.PRINCIPLES).is_dir())
        result = kb.search(self.root, '品牌增长', '客户选择它', 3)
        self.assertEqual(result[0]['line'], 1)
        self.assertEqual(manual, self.root/result[0]['file'])
        with self.assertRaises(ValueError):
            kb.workspace(self.root, 'brand-B', True)

    def test_versions_independent_sources_and_nested_areas(self):
        doc = self.root/'访谈.txt'
        doc.write_text('昨天的反馈', encoding='utf-8')
        def collect(origin):
            return kb.collect(self.root, '品牌增长', '产品资料库/访谈', doc, origin, '经验与反馈')
        first = collect('试用单 A')
        self.assertEqual(first, collect('试用单 A'))
        self.assertNotEqual(first['receipt'], collect('试用单 B')['receipt'])
        doc.write_text('补充后的反馈', encoding='utf-8')
        self.assertNotEqual(first['file'], collect('试用单 A')['file'])
        self.assertEqual((self.root/first['file']).read_text(encoding='utf-8'), '昨天的反馈')
        self.assertEqual(json.loads((self.root/first['receipt']).read_bytes())['origin'], '试用单 A')

    def test_principle_and_path_protection(self):
        doc = self.root/'记录.md'
        doc.write_text('资料', encoding='utf-8')
        for path in ('../../其他品牌', '第一性原理', '经营/第一性原理'):
            with self.assertRaises(ValueError):
                kb.collect(self.root, '品牌增长', path, doc, '访谈', '用户资料')
        principle = next((self.root/'知识库/品牌增长/第一性原理').glob('经营原理-*.md'))
        principle.write_bytes(b'local edits')
        with self.assertRaises(ValueError):
            kb.initialize(self.root)
        self.assertEqual(principle.read_bytes(), b'local edits')
