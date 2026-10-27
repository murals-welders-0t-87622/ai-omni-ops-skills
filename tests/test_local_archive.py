import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/archive_init.py'
spec = importlib.util.spec_from_file_location('archive_init', SCRIPT)
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)

class LocalArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / '品牌A'
        self.root.mkdir()
    def tearDown(self):
        self.temp.cleanup()
    def run_init(self, *args):
        return subprocess.run([sys.executable, '-X', 'utf8', str(SCRIPT), '--brand-root', str(self.root), *args], capture_output=True, text=True, encoding='utf-8')
    def test_daily_work_and_idempotence(self):
        args=('--area','douyin','--mode','work','--date','20261027','--name','扫把罢工')
        dry=self.run_init(*args,'--dry-run');self.assertEqual(dry.returncode,0,dry.stderr)
        self.assertFalse((self.root/'公域获客').exists())
        result=self.run_init(*args);self.assertEqual(result.returncode,0,result.stderr)
        task=self.root/'公域获客'/'内容获客'/'抖音视频号'/'20261027'/'扫把罢工'
        self.assertEqual(set(x.name for x in task.iterdir()), {'素材','选题','文案','制作','成片','发布与复盘'})
        file=task/'文案'/'脚本_V01.txt';file.write_text('保留内容',encoding='utf-8')
        again=self.run_init(*args);self.assertEqual(again.returncode,0,again.stderr)
        self.assertEqual(file.read_text(encoding='utf-8'),'保留内容')
        self.assertEqual(json.loads(again.stdout)['new_directories'],[])
    def test_every_area_is_scoped(self):
        for area,(base,folders) in archive.AREAS.items():
            task,dirs=archive.build(self.root,area,'project','本次任务','20261027')
            self.assertEqual(task.relative_to(self.root).parts,(*base,'项目','本次任务'))
            self.assertEqual([p.name for p in dirs],list(folders))
    def test_all_business_skills_route_to_archive_standard(self):
        root=SCRIPT.parents[3]
        registry=json.loads((root/'registry'/'skills.json').read_text(encoding='utf-8'))
        for skill in registry['skills']:
            if skill['id'] in ('00-omni-system-setup','omni-skill-maintenance'):continue
            with self.subTest(skill=skill['id']):
                self.assertIn('local-archive-standard.md',(root/skill['path']/'SKILL.md').read_text(encoding='utf-8'))
    def test_other_channels_period_and_product(self):
        xhs=self.run_init('--area','xiaohongshu','--mode','work','--date','20261027','--name','作品甲')
        self.assertEqual(xhs.returncode,0,xhs.stderr)
        self.assertTrue((self.root/'公域获客'/'内容获客'/'小红书'/'20261027'/'作品甲'/'文案').is_dir())
        report=self.run_init('--area','taobao','--mode','period','--date','20261001','--end','20261031','--name','月度复盘')
        self.assertEqual(report.returncode,0,report.stderr)
        self.assertTrue((self.root/'电商板块'/'淘宝天猫运营'/'周期'/'20261001-20261031'/'月度复盘'/'店铺数据').is_dir())
        detail=self.run_init('--area','detail','--name','商品甲')
        self.assertEqual(detail.returncode,0,detail.stderr)
        self.assertTrue((self.root/'电商板块'/'详情页'/'项目'/'商品甲'/'主图').is_dir())
    def test_existing_content_project_tool_uses_task_subdirectory(self):
        result=self.run_init('--area','content','--name','本期内容')
        self.assertEqual(result.returncode,0,result.stderr)
        task=self.root/'公域获客'/'内容获客'/'内容规划'/'项目'/'本期内容'
        existing=SCRIPT.parents[2]/'brand-content-growth'/'scripts'/'project.py'
        init=subprocess.run([sys.executable,'-X','utf8',str(existing),'init','--root',str(task/'内容项目数据'),'--brand','品牌A'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(init.returncode,0,init.stderr)
        self.assertTrue((task/'内容项目数据'/'project.json').is_file())
    def test_reject_unsafe_and_bad_dates(self):
        for name in ('../别的品牌','..','a/b','CON','a.','a\\b'):
            self.assertNotEqual(self.run_init('--area','douyin','--mode','work','--name',name).returncode,0)
        self.assertNotEqual(self.run_init('--area','douyin','--mode','work','--date','20260230','--name','任务').returncode,0)
        self.assertNotEqual(self.run_init('--area','sales','--mode','period','--date','20261031','--end','20261001','--name','任务').returncode,0)
        self.assertFalse((self.root/'公域获客').exists())
    def test_existing_file_conflict(self):
        (self.root/'品牌增长').write_text('不可覆盖',encoding='utf-8')
        result=self.run_init('--area','brand','--name','任务')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual((self.root/'品牌增长').read_text(encoding='utf-8'),'不可覆盖')
    def test_reject_symlink_when_available(self):
        outside=Path(self.temp.name)/'other';outside.mkdir()
        try:(self.root/'品牌增长').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('symlink not available')
        self.assertNotEqual(self.run_init('--area','brand','--name','任务').returncode,0)
        self.assertEqual(list(outside.iterdir()),[])

if __name__ == '__main__': unittest.main()
