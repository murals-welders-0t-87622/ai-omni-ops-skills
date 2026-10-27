import json, unittest
from pathlib import Path
from test_manage import manage, validator

ROOT=Path(__file__).resolve().parents[1]
class SystemSetupTests(unittest.TestCase):
    def test_setup_is_first_and_installed_by_default(self):
        r=json.loads((ROOT/'registry/skills.json').read_text(encoding='utf-8'))
        self.assertEqual(r['skills'][0]['id'], '00-omni-system-setup')
        self.assertEqual(r['profiles']['all'][0], '00-omni-system-setup')
        rows=manage.selection(r,'all',None)
        self.assertEqual(rows[0]['id'], '00-omni-system-setup')
        self.assertEqual(len(rows),len(r['skills']))
        self.assertEqual(rows[0]['dependencies'],[])
    def test_system_setup_is_self_contained_and_has_no_business_routing_changes(self):
        r=json.loads((ROOT/'registry/skills.json').read_text(encoding='utf-8'))
        lock=json.loads((ROOT/'registry/architecture-lock.json').read_text(encoding='utf-8'))
        self.assertEqual(validator.architecture_errors(r,lock),[])
        for row in r['skills'][1:]:
            self.assertNotIn('00-omni-system-setup',row['dependencies'])
        entry=ROOT/'skills/00-omni-system-setup'
        self.assertTrue((entry/'references/windows-docker.md').is_file())
        self.assertTrue((entry/'scripts/prepare-new-machine.ps1').is_file())

if __name__=='__main__': unittest.main()
