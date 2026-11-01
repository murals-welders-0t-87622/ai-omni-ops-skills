import contextlib, importlib.util, io, json, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from test_manage import manage, validator

ROOT=Path(__file__).resolve().parents[1]
ASR_CHECK=ROOT/'skills/00-omni-system-setup/scripts/check-compose-asr.py'
spec=importlib.util.spec_from_file_location('check_compose_asr',ASR_CHECK)
asr_check=importlib.util.module_from_spec(spec)
spec.loader.exec_module(asr_check)
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
    def test_new_install_enables_video_transcription_and_documents_verification(self):
        entry=ROOT/'skills/00-omni-system-setup'
        script=(entry/'scripts/prepare-new-machine.ps1').read_text(encoding='utf-8')
        guide=(entry/'references/windows-docker.md').read_text(encoding='utf-8')
        self.assertIn('INSTALL_LOCAL_ASR=1',script)
        self.assertIn('INSTALL_LOCAL_ASR=1',guide)
        self.assertIn('HF_HUB_OFFLINE=1',guide)
        self.assertIn('短视频样本',guide)
        self.assertIn('check-local-asr.py',guide)
        self.assertIn('model_files_present_not_loaded',guide)

    def test_resolved_asr_model_and_disabled_cases(self):
        cfg={'services':{'server':{'build':{'args':{'INSTALL_LOCAL_ASR':'1',
             'LOCAL_ASR_PRELOAD_WHISPER_MODEL':'small'}},'environment':{'WHISPER_MODEL_NAME':'small'}}}}
        self.assertEqual(asr_check.check(cfg)['state'], 'models_match')
        cfg['services']['server']['environment']['WHISPER_MODEL_NAME']='base'
        self.assertEqual(asr_check.check(cfg)['state'], 'model_mismatch')
        cfg['services']['server']['build']['args']['INSTALL_LOCAL_ASR']='0'
        self.assertEqual(asr_check.check(cfg)['state'], 'asr_not_built')
        self.assertEqual(asr_check.check({'services':{}})['state'], 'configuration_unavailable')

    def test_compose_failure_never_prints_sensitive_config_or_stderr(self):
        output=io.StringIO()
        with patch.object(asr_check.subprocess, 'run', return_value=SimpleNamespace(returncode=1,stdout='',stderr='secret-value')):
            with contextlib.redirect_stdout(output):
                self.assertEqual(asr_check.main(['--','-f','compose.yml']),2)
        self.assertNotIn('secret-value', output.getvalue())
        self.assertEqual(json.loads(output.getvalue())['state'],'configuration_unavailable')

if __name__=='__main__': unittest.main()
