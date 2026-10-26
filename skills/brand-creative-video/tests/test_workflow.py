from pathlib import Path

import sys,json,tempfile,unittest,base64,io,os

SKILL=Path(__file__).resolve().parents[1]

ROOT=Path(os.environ.get('BRAND_VIDEO_TEST_ROOT',str(SKILL/'tests/output'))).resolve();ROOT.mkdir(parents=True,exist_ok=True)

sys.path.insert(0,str(SKILL/'scripts'))

import project,prepare_request,verify_package



class WorkflowTests(unittest.TestCase):

    def setUp(self):

        parent=(ROOT/'qa/offline-temporary').resolve();parent.mkdir(parents=True,exist_ok=True)

        self.tmp=tempfile.TemporaryDirectory(dir=parent,prefix='fixture-');self.folder=Path(self.tmp.name).resolve();assert self.folder.is_relative_to(parent)

        self.root=self.folder/'project';project.init(self.root,'测试虚构品牌','离线模拟',30,'demo-two')

    def tearDown(self):

        assert self.folder.is_relative_to((ROOT/'qa/offline-temporary').resolve());self.tmp.cleanup()

    def ready(self,shot='A01',jobs=2,retries=0):

        # Only fixture images/receipts, never supplier data or human approval.

        root,p,assets,shots=project.load(self.root);s=next(x for x in shots if x['id']==shot)

        fixture=self.root/'assets/keyframes/test-only.png';fixture.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aKuoAAAAASUVORK5CYII='))

        for a in assets:

            if a['id'] in set(s['asset_refs']+[s['keyframe_id']]):a.update(status='approved',file=fixture.relative_to(root).as_posix(),sha256=project.sha(fixture))

        for e in p['episodes']:e['script_status']='approved'

        schema=root/'runs/responses/schema-fixture.json';project.save(schema,{'fixture_only':True,'tool':'SIMULATED_SINGLE_IMAGE'})

        p['runtime_schema_evidence']={'path':schema.relative_to(root).as_posix(),'sha256':project.sha(schema)}

        p['authorization']['generation']={'allowed':True,'providers':['fixture-provider'],'max_jobs':jobs,'max_retries_per_shot':retries,'evidence':'TEST FIXTURE, NOT USER AUTHORIZATION'}

        project.save(root/'project.json',p);project.save(root/'assets/assets.json',assets)

        receipt=root/'runs/responses/upload-fixture.json';project.save(receipt,{'fixture_only':True,'fileName':'openapi/test-fixture.png'})

        return prepare_request.prepare(root,shot,'openapi/test-fixture.png',receipt)['request']

    def test_synthetic_project_has_two_independent_deliveries(self):

        v=project.validate(self.root);self.assertTrue(v['valid'],v['errors']);r,p,a,s=project.load(self.root)

        self.assertEqual([x['duration'] for x in p['episodes']],[8,8]);self.assertEqual(len(s),4);self.assertEqual(sum(x['kind']=='generated' for x in s),4)

        self.assertFalse(project.validate(self.root,True)['valid']);self.assertEqual(project.events(self.root),[])

        self.assertTrue((self.root/'state/checkpoint.json').is_file())

    def test_existing_project_is_not_silently_reinitialized(self):

        before=project.sha(self.root/'project.json')

        with self.assertRaises(ValueError):project.init(self.root,'另一个品牌','覆盖',30)

        self.assertEqual(before,project.sha(self.root/'project.json'))

    def test_timeline_gap_and_asset_cycle_are_detected(self):

        r,p,a,s=project.load(self.root);s[1]['start']+=.5;a[0]['depends_on']=[a[0]['id']]

        project.save(r/'storyboard/shots.json',s);project.save(r/'assets/assets.json',a)

        errors=project.validate(r)['errors'];self.assertTrue(any('gap/overlap' in x for x in errors));self.assertTrue(any('cycle' in x for x in errors))

    def test_single_image_request_and_scope_guard(self):

        req=Path(self.ready());d=project.read(req);self.assertEqual(len([x for x in d['nodeInfoList'] if x['nodeId']=='12']),1)

        self.assertEqual(next(x['fieldValue'] for x in d['nodeInfoList'] if x['fieldName']=='duration'),'4')

        with self.assertRaises(ValueError):prepare_request.prepare(self.root,'A01','C:/fake/local.png',self.root/'runs/responses/upload-fixture.json')

        project.reserve(self.root,'A01',req,'fixture-provider')

        with self.assertRaises(ValueError):project.reserve(self.root,'A01',req,'fixture-provider')

        self.assertEqual(len(project.events(self.root)),1)

    def test_unknown_outcome_is_not_failed_or_resubmitted(self):

        req=self.ready();project.reserve(self.root,'A01',req,'fixture-provider')

        receipt=self.root/'runs/responses/unknown.json';project.save(receipt,{'fixture_only':True,'error':'request timed out; result unknown'})

        project.event(self.root,'A01','outcome_unknown',None,receipt)

        with self.assertRaises(ValueError):project.reserve(self.root,'A01',req,'fixture-provider')

        self.assertEqual(project.status(self.root)['reconcile_before_submit'][-1]['state'],'outcome_unknown')

    def test_success_receipt_dedup_and_job_mismatch(self):

        req=self.ready();project.reserve(self.root,'A01',req,'fixture-provider')

        receipt=self.root/'runs/responses/real-format-fixture.json';project.save(receipt,{'fixture_only':True,'taskId':'fixture-job-1','status':'SUCCESS'})

        project.event(self.root,'A01','submitted','fixture-job-1',receipt);project.event(self.root,'A01','generated','fixture-job-1',receipt)

        self.assertTrue(project.event(self.root,'A01','generated','fixture-job-1',receipt)['deduplicated'])

        wrong=self.root/'runs/responses/wrong.json';project.save(wrong,{'taskId':'fixture-job-2'})

        with self.assertRaises(ValueError):project.event(self.root,'A01','generated','fixture-job-2',wrong)

        self.assertTrue(project.reserve(self.root,'A01',req,'fixture-provider')['existing'])

    def test_budget_and_late_old_job_do_not_create_duplicate_paid_work(self):

        req=Path(self.ready(jobs=2,retries=1));project.reserve(self.root,'A01',req,'fixture-provider')

        receipt=self.root/'runs/responses/failed-fixture.json';project.save(receipt,{'fixture_only':True,'taskId':'old-fixture-job','status':'FAILED'})

        project.event(self.root,'A01','failed','old-fixture-job',receipt)

        req2=req.with_name('retry.json');project.save(req2,{'fixture_only':True,'revision':2});project.reserve(self.root,'A01',req2,'fixture-provider')

        with self.assertRaises(ValueError):project.event(self.root,'A01','generated','old-fixture-job',receipt)

        new=self.root/'runs/responses/new.json';project.save(new,{'taskId':'new-fixture-job','status':'FAILED'});project.event(self.root,'A01','failed','new-fixture-job',new)

        with self.assertRaises(ValueError):project.reserve(self.root,'A01',req2,'fixture-provider')

        self.assertEqual(sum(e['state']=='reserved' for e in project.events(self.root)),2)

    def test_invalidation_only_marks_actual_dependencies_and_preserves_files(self):

        self.ready();file=self.root/'assets/keyframes/test-only.png';before=project.sha(file)

        x=project.invalidate(self.root,'CH-DEMO','fixture master revision changed')

        self.assertIn('B02',x['affected_shots']);self.assertIn('KF-B02',x['affected_assets']);self.assertNotIn('A01',x['affected_shots']);self.assertEqual(before,project.sha(file))

    def test_source_coverage_and_path_boundaries(self):

        v=verify_package.verify();self.assertTrue(v['valid'],v['errors']);self.assertEqual(v['indexed_cases'],0);self.assertEqual(v['distribution'],'public-methods')

        with self.assertRaises(ValueError):project.within(self.root,'../outside.json')



if __name__=='__main__':

    suite=unittest.defaultTestLoader.loadTestsFromTestCase(WorkflowTests);stream=io.StringIO();res=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)

    report={'testsRun':res.testsRun,'successful':res.wasSuccessful(),'failures':len(res.failures),'errors':len(res.errors),'scope':'离线模拟，不是供应商生成或人工美学审核；模拟授权与job仅存在于隔离临时夹具','log':stream.getvalue()}

    project.save(ROOT/'qa/offline-test-results.json',report);print(stream.getvalue());print(json.dumps({k:v for k,v in report.items() if k!='log'},ensure_ascii=False));sys.exit(0 if res.wasSuccessful() else 1)
