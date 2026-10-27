import copy, importlib.util, json, unittest
from pathlib import Path

path=Path(__file__).resolve().parents[1]/'skills/omni-growth-learning/scripts/validate_record.py'
spec=importlib.util.spec_from_file_location('growth_record',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def record():
 return {'id':'synthetic-1','scope':{'brand':'TEST','object':'video-1'},'trigger':{'kind':'user-feedback','observation':'opening unclear','sources':['test-feedback']},'hypothesis':{'factor':'opening','mechanism':'expectation','competingExplanations':['audience mix']},'proposal':{'action':'compare openings','testDesign':'observational','primaryMetric':'retention'},'decision':{'status':'pending-user-choice'},'execution':{'status':'not-started','receipts':[]},'result':{'status':'not-observed'}}
class LearningRecordTests(unittest.TestCase):
 def test_all_business_entrypoints_route_feedback_to_learning(self):
  root=path.parents[3];reg=json.loads((root/'registry/skills.json').read_text(encoding='utf-8'))
  for skill in reg['skills']:
   if skill['id'] in {'omni-growth-learning','00-omni-system-setup'}: continue
   text=(root/skill['path']/'SKILL.md').read_text(encoding='utf-8')
   self.assertIn('omni-growth-learning',text,skill['id'])
 def test_candidate_needs_real_trigger(self):
  r=record();self.assertEqual(m.validate(r),[]);r['trigger']['sources']=[];self.assertTrue(m.validate(r))
 def test_no_execution_before_choice(self):
  r=record();r['execution']['status']='in-progress';self.assertIn("execution requires user's selection",m.validate(r))
 def test_selected_requires_actor_and_time(self):
  r=record();r['decision']={'status':'selected'};self.assertIn('user selection evidence missing',m.validate(r))
 def test_outcome_requires_actual_receipt_and_limits(self):
  r=record();r['decision']={'status':'selected','selectedBy':'test-user','selectedAt':'2026-10-27T10:00:00+08:00'};r['execution']={'status':'completed','receipts':[]};r['result']={'status':'support','metrics':['test observation'],'limitations':['non-randomized']};self.assertTrue(m.validate(r));r['execution']['receipts']=['test-receipt'];self.assertEqual(m.validate(r),[])
 def test_no_detectable_effect_requires_sample_not_empty_inference(self):
  r=record();r['decision']={'status':'selected','selectedBy':'test-user','selectedAt':'2026-10-27T10:00:00+08:00'};r['execution']={'status':'completed','receipts':['test']};r['result']={'status':'no-detectable-effect','metrics':['test observation'],'limitations':['uncertain'],'samples':None};self.assertTrue(m.validate(r));r['result']['status']='inconclusive';self.assertEqual(m.validate(r),[])
if __name__=='__main__':unittest.main()
