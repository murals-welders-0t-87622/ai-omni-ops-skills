import copy,json,unittest
from pathlib import Path
from test_manage import module

v=module('validate');ROOT=Path(__file__).resolve().parents[1]
class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.reg=json.loads((ROOT/'registry/skills.json').read_text(encoding='utf-8'));self.lock=json.loads((ROOT/'registry/architecture-lock.json').read_text(encoding='utf-8'))
    def test_current_method_enrichment_preserves_business_framework(self):
        self.reg['version']='9.0.0';self.reg['skills'][0]['version']='8.2.0';self.reg['skills'][0]['description']='New craft details only';self.assertEqual(v.architecture_errors(self.reg,self.lock),[])
    def test_missing_domain_is_blocked(self):
        self.reg['skills'].pop();self.assertTrue(v.architecture_errors(self.reg,self.lock))
    def test_changing_accountability_is_blocked(self):
        self.reg['skills'][0]['kind']='orchestrator';self.assertTrue(v.architecture_errors(self.reg,self.lock))
    def test_cross_domain_dependency_change_is_blocked(self):
        self.reg['skills'][0]['dependencies']=['ai-sales-operations'];self.assertTrue(v.architecture_errors(self.reg,self.lock))
    def test_business_stage_reordering_is_blocked(self):
        self.reg['businessFramework']['businessFlow'].reverse();self.assertTrue(v.architecture_errors(self.reg,self.lock))
    def test_moving_entrypoint_is_blocked(self):
        self.reg['skills'][0]['path']='skills/renamed';self.assertTrue(v.architecture_errors(self.reg,self.lock))
if __name__=='__main__':unittest.main()
