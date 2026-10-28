import importlib.util,json,unittest
from pathlib import Path

R=Path(__file__).resolve().parents[1];D=R/'skills/dynamic-video-craft'
spec=importlib.util.spec_from_file_location('styles',D/'scripts/style_catalog.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class StyleSourceTests(unittest.TestCase):
    def test_index_count_and_identity(self):
        rows=m.search()['entries'];self.assertEqual(len(rows),133);self.assertEqual(len({x['id'] for x in rows}),133)
    def test_chinese_paper_source(self):
        rows=m.search('层叠纸雕','motiongit')['entries'];self.assertEqual(len(rows),1);self.assertEqual(rows[0]['availability'],'coming-soon')
    def test_preview_is_not_downloadable(self):
        self.assertEqual(m.search('papercut','motiongit',True)['count'],0)
    def test_variants_remain_distinct(self):
        self.assertEqual(m.search('Kinetic Tech','motiongit')['count'],2)
    def test_direct_package_links_and_restricted_preview(self):
        rows=m.search('', 'motiongit', True)['entries']; self.assertTrue(rows); self.assertTrue(all(row['downloadType']=='direct-package' and row.get('directDownloads') for row in rows))
        previews=[row for row in m.search('', 'motiongit')['entries'] if row['availability']=='preview-only']; self.assertTrue(previews); self.assertTrue(all(row['downloadType']=='none' for row in previews))
    def test_website_audit_covers_all_44_pages(self):
        rows=[r for r in m.search(source='motiongit')['entries'] if r.get('websiteAuditDate')=='2026-10-28']
        self.assertEqual(len({r['url'] for r in rows}),44)
        self.assertEqual(len({r['url'] for r in rows if r['websiteStatus'].startswith('官网设置获取门槛')}),15)
        self.assertTrue(all(r.get('websiteLicenseSummary') for r in rows))
    def test_category_and_aspect_filters(self):
        rows=m.search(source='motiongit', category='talk', aspect='9:16')['entries']
        self.assertTrue(rows); self.assertTrue(all(x['category']=='talk' and x['aspect']=='9:16' for x in rows))
    def test_paper_docs_have_full_read_coverage(self):
        for key in ['paper lantern','paper popup']:
            row=m.search(key,'lemo')['entries'][0];self.assertEqual(row['coverage'],'Full STYLE read')
    def test_unknown_style_is_not_fabricated(self):
        self.assertEqual(m.search('does-not-exist')['count'],0)
    def test_other_style_stays_index_only(self):
        row=m.search('newsreel','lemo')['entries'][0];self.assertIn('index only',row['coverage'])

if __name__=='__main__':unittest.main()
