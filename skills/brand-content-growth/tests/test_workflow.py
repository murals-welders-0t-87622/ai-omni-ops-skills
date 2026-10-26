from pathlib import Path
import importlib.util,unittest,tempfile,json,copy,subprocess,sys,os

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('project',BASE/'scripts/project.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class Workflow(unittest.TestCase):
    def setUp(self):
        self.temp_parent=Path(os.environ.get('BCG_TEST_TMP',tempfile.gettempdir())).resolve()
        self.temp_parent.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=self.temp_parent);self.root=Path(self.tmp.name)
        self.d=json.loads((BASE/'assets/project-template.json').read_text(encoding='utf-8'))
        self.d['brand']['name']='离线演练品牌'
        self.d['strategy'].update(business_bottleneck='目标客户不理解适用条件',priority_user='购买决策者',priority_scenario='购买前比较',value_proposition='提供明确适配判断',primary_task='T2',handoff_path='先了解条件',measurement_plan='记录真实相关提问，不推算成交')
        self.d['evidence']=[{'id':'E1','kind':'brand_fact','source_ref':'fixture-only','fact':'用于离线检查的明确条件'}]
        self.d['value_cards']=[{'id':'V1','user':'购买决策者','scenario':'购买前比较','pain':'不知道适用条件','solution':'解释边界','difference':'相对只列参数','limits':'仅演练','evidence_ids':['E1'],'status':'supported'}]
    def tearDown(self):
        assert self.root.resolve().is_relative_to(self.temp_parent) and self.root.resolve()!=self.temp_parent
        self.tmp.cleanup()
    def script(self):
        (self.root/'script.txt').write_text('离线测试脚本，不是业务成果',encoding='utf-8')
        self.d['content_items']=[{'id':'C1','title':'如何判断适用','value_card_id':'V1','primary_task':'T2','strategy_ids':['M09'],'narrative_structure':'问题到判断','format':'图解','brand_role':'解释者','next_step':'查看条件','measurement':'有效提问','script_path':'script.txt','claims':[{'text':'明确条件','evidence_ids':['E1'],'status':'verified'}],'assets':[]}]
    def test_new_draft_does_not_invent_authority(self):
        dest=self.root/'new';r=subprocess.run([sys.executable,str(BASE/'scripts/project.py'),'init','--root',str(dest),'--brand','演练'],capture_output=True)
        self.assertEqual(r.returncode,0);d=json.loads((dest/'project.json').read_text(encoding='utf-8'));self.assertIsNone(d['authority']['task_id']);self.assertFalse(d['permissions']['paid_generation']['authorized'])
        r2=subprocess.run([sys.executable,str(BASE/'scripts/project.py'),'init','--root',str(dest),'--brand','另一个'],capture_output=True);self.assertEqual(r2.returncode,2);self.assertEqual(d,json.loads((dest/'project.json').read_text(encoding='utf-8')))
    def test_valid_strategy_without_platform_data(self):self.assertTrue(mod.validate(self.d,self.root,'strategy')['passed'])
    def test_supported_pain_cannot_use_only_hypothesis(self):
        self.d['evidence'][0]['kind']='hypothesis';self.assertFalse(mod.validate(self.d,self.root,'strategy')['passed'])
    def test_script_requires_real_file_and_links(self):
        self.script();self.assertTrue(mod.validate(self.d,self.root,'script')['passed']);self.d['content_items'][0]['value_card_id']='foreign';self.assertFalse(mod.validate(self.d,self.root,'script')['passed'])
    def test_unverified_claim_or_preference_not_fact(self):
        self.script();self.d['evidence'][0]['kind']='user_preference';self.assertFalse(mod.validate(self.d,self.root,'script')['passed'])
    def test_file_cannot_escape_project(self):
        self.script();self.d['content_items'][0]['script_path']='../outside';self.assertFalse(mod.validate(self.d,self.root,'script')['passed'])
    def test_ready_script_is_not_publication(self):
        self.script();result=mod.validate(self.d,self.root,'release');self.assertFalse(result['passed']);self.assertTrue(any('authorization' in e for e in result['errors']));self.assertTrue(any('video missing' in e for e in result['errors']))
    def test_unknown_sku_does_not_pass_product_proof(self):
        self.script();(self.root/'asset.txt').write_text('fixture');self.d['content_items'][0]['assets']=[{'path':'asset.txt','rights_status':'cleared','is_product_proof':True,'sku_status':'unknown'}];self.assertTrue(any('SKU' in e for e in mod.validate(self.d,self.root,'release')['errors']))
    def test_unknown_zero_and_rate_are_distinct(self):
        self.assertIsNone(mod.ratio(None,100));self.assertIsNone(mod.ratio(1,0));self.assertEqual(mod.ratio(0,100),0)
        self.d['metrics']=[{'name':'示意率','source_ref':'fixture','window':'same','unit':'ratio','attribution':'unknown','numerator':None,'denominator':100,'rate':0.2}]
        self.assertFalse(mod.validate(self.d,self.root,'review')['passed'])
    def test_source_search_and_read(self):
        r=subprocess.run([sys.executable,str(BASE/'scripts/sources.py'),'search','--query','陌生化','--limit','2'],capture_output=True,encoding='utf-8');self.assertEqual(r.returncode,0);rows=json.loads(r.stdout);self.assertTrue(rows)
        read=subprocess.run([sys.executable,str(BASE/'scripts/sources.py'),'read','--id',rows[0]['source_id'],'--lines','5'],capture_output=True,encoding='utf-8');self.assertEqual(read.returncode,0);self.assertIn(rows[0]['source_id'],read.stdout)

if __name__=='__main__':unittest.main()
