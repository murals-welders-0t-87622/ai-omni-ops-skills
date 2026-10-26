import importlib.util, json, tempfile, unittest
from unittest.mock import patch
from pathlib import Path

def module(name):
    p=Path(__file__).resolve().parents[1]/'scripts'/f'{name}.py';s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
manage=module('manage');validator=module('validate')

class InstallTests(unittest.TestCase):
    def setUp(self):
        parent=Path(__file__).resolve().parents[1]/'.local/test-tmp';parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent);self.base=Path(self.tmp.name).resolve();assert self.base.is_relative_to(parent.resolve());self.repo=self.base/'repo';self.target=self.base/'target'
        (self.repo/'registry').mkdir(parents=True)
        for n in ['chief','domain']:
            d=self.repo/'skills'/n;d.mkdir(parents=True);(d/'SKILL.md').write_text(n+' v1',encoding='utf-8')
        self.reg={'version':'1.0.0','skills':[{'id':n,'path':'skills/'+n,'version':'1','dependencies':[] if n=='chief' else ['chief']} for n in ['chief','domain']],'profiles':{'all':['domain']}}
        self.refresh()
    def tearDown(self):self.tmp.cleanup()
    def refresh(self):
        (self.repo/'registry/skills.json').write_text(json.dumps(self.reg),encoding='utf-8')
        (self.repo/'release-manifest.json').write_text(json.dumps(validator.manifest(self.repo)),encoding='utf-8')
    def install(self,**kw):return manage.install(self.target,repo=self.repo,**kw)
    def test_fresh_dependency_closure_and_noop(self):
        result=self.install();self.assertEqual(result['changed'],2);self.assertTrue((self.target/'chief/SKILL.md').exists());self.assertEqual(self.install()['status'],'unchanged')
    def test_dry_run_writes_nothing(self):
        self.assertTrue(self.install(dry=True)['dryRun']);self.assertFalse(self.target.exists())
    def test_local_change_blocks_whole_update(self):
        self.install();(self.target/'domain/SKILL.md').write_text('local',encoding='utf-8');before=(self.target/manage.STATE).read_bytes()
        with self.assertRaisesRegex(ValueError,'Local or unmanaged'):self.install()
        self.assertEqual(before,(self.target/manage.STATE).read_bytes());self.assertEqual((self.target/'domain/SKILL.md').read_text(),'local')
    def test_unmanaged_requires_review_and_keeps_backup(self):
        (self.target/'domain').mkdir(parents=True);(self.target/'domain/custom.txt').write_text('keep',encoding='utf-8')
        with self.assertRaises(ValueError):self.install()
        r=self.install(adopt=True);manage.rollback(self.target,r['transaction']);self.assertEqual((self.target/'domain/custom.txt').read_text(),'keep');self.assertFalse((self.target/'chief').exists())
    def test_update_and_rollback(self):
        self.install();(self.repo/'skills/domain/SKILL.md').write_text('v2',encoding='utf-8');self.reg['version']='1.1.0';self.refresh();r=self.install();self.assertEqual((self.target/'domain/SKILL.md').read_text(),'v2');manage.rollback(self.target,r['transaction']);self.assertEqual((self.target/'domain/SKILL.md').read_text(),'domain v1')
    def test_rollback_protects_new_local_changes(self):
        r=self.install();(self.target/'domain/SKILL.md').write_text('new local',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'local changes'):manage.rollback(self.target,r['transaction'])
    def test_tampered_source_refuses_before_target_write(self):
        (self.repo/'skills/domain/SKILL.md').write_text('tampered',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'hash mismatch'):self.install()
        self.assertFalse(self.target.exists())
    def test_path_traversal_rejected(self):
        self.reg['skills'][1]['id']='../escape';self.reg['profiles']['all']=['../escape'];self.refresh()
        with self.assertRaisesRegex(ValueError,'Invalid skill'):self.install()
        self.assertFalse(self.target.exists())
    def test_missing_dependency_blocks_without_write(self):
        self.reg['skills'][1]['dependencies']=['missing'];self.refresh()
        with self.assertRaisesRegex(ValueError,'Unknown skill'):self.install()
        self.assertFalse(self.target.exists())
    def test_source_path_escape_rejected(self):
        self.reg['skills'][1]['path']='../outside';self.refresh()
        with self.assertRaisesRegex(ValueError,'Source path escapes'):self.install()
        self.assertFalse(self.target.exists())
    def test_failure_after_first_move_restores_bundle(self):
        original=Path.rename
        def failing(path,target):
            if path.name=='domain' and path.parent.name=='staged':raise OSError('simulated disk failure')
            return original(path,target)
        with patch.object(Path,'rename',failing):
            with self.assertRaisesRegex(OSError,'simulated'):self.install()
        self.assertFalse((self.target/'chief').exists());self.assertFalse((self.target/'domain').exists());self.assertEqual(json.loads((self.target/manage.STATE).read_text())['skills'],{})
    def test_old_rollback_cannot_remove_newer_ownership(self):
        first=self.install();(self.repo/'skills/domain/SKILL.md').write_text('new release',encoding='utf-8');self.refresh();self.install()
        with self.assertRaisesRegex(ValueError,'Newer installation'):manage.rollback(self.target,first['transaction'])

if __name__=='__main__':unittest.main()
