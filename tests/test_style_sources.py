import importlib.util,json,unittest
from pathlib import Path

R=Path(__file__).resolve().parents[1];D=R/'skills/dynamic-video-craft'
spec=importlib.util.spec_from_file_location('styles',D/'scripts/style_catalog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class StyleSourceTests(unittest.TestCase):
    def test_index_count_and_identity(self):
        rows=m.search()['entries'];self.assertEqual(len(rows),103);self.assertEqual(len({x['id'] for x in rows}),103)
    def test_chinese_paper_source(self):
        rows=m.search('层叠纸雕','motiongit')['entries'];self.assertEqual(len(rows),1);self.assertEqual(rows[0]['availability'],'coming-soon')
    def test_preview_is_not_downloadable(self):
        self.assertEqual(m.search('papercut','motiongit',True)['count'],0)
    def test_variants_remain_distinct(self):
        self.assertEqual(m.search('Kinetic Tech','motiongit')['count'],2)
    def test_paper_docs_have_full_read_coverage(self):
        for key in ['paper lantern','paper popup']:
            row=m.search(key,'lemo')['entries'][0];self.assertEqual(row['coverage'],'Full STYLE read')
    def test_unknown_style_is_not_fabricated(self):
        self.assertEqual(m.search('does-not-exist')['count'],0)
    def test_other_style_stays_index_only(self):
        row=m.search('newsreel','lemo')['entries'][0];self.assertIn('index only',row['coverage'])

if __name__=='__main__':unittest.main()
