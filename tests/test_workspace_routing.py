import importlib.util, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('workspace_routing',ROOT/'skills/00-omni-system-setup/scripts/configure-workspace.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

class WorkspaceRoutingTests(unittest.TestCase):
    def test_append_preserves_existing_and_is_idempotent(self):
        parent=ROOT/'.local/test-tmp'; parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            path=Path(directory)/'AGENTS.md'; original='# 原有规则\n\n不可删除\n'; path.write_text(original,encoding='utf-8')
            status,_=module.configure(directory); self.assertEqual(status,'added'); result=path.read_text(encoding='utf-8')
            self.assertTrue(result.startswith(original)); self.assertIn('视频',result)
            self.assertEqual(module.configure(directory)[0],'existing'); self.assertEqual(path.read_text(encoding='utf-8'),result)
    def test_partial_markers_not_overwritten(self):
        parent=ROOT/'.local/test-tmp'; parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as directory:
            path=Path(directory)/'AGENTS.md'; path.write_text(module.START,encoding='utf-8')
            with self.assertRaises(ValueError): module.configure(directory)
            self.assertEqual(path.read_text(encoding='utf-8'),module.START)

if __name__=='__main__': unittest.main()
