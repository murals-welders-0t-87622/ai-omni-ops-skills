import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/dynamic-video-craft/scripts/check_timeline.py'
spec = importlib.util.spec_from_file_location('host_timeline', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DigitalHostTimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.public = Path(self.tmp.name)
        (self.public / 'host.mp4').write_bytes(b'placeholder')
        self.timeline = json.loads((ROOT / 'skills/dynamic-video-craft/assets/remotion-starter/src/video.json').read_text(encoding='utf-8'))

    def tearDown(self):
        self.tmp.cleanup()

    def test_existing_valid_timeline_remains_valid(self):
        errors, _ = module.validate(self.timeline, self.public)
        self.assertEqual(errors, [])

    def test_valid_timed_host_is_accepted(self):
        self.timeline['hosts'] = [{'id': 'person', 'src': 'host.mp4', 'start': 1, 'end': 2, 'placement': 'lower-left'}]
        errors, _ = module.validate(self.timeline, self.public)
        self.assertEqual(errors, [])

    def test_missing_media_invalid_placement_and_overlap_are_rejected(self):
        self.timeline['hosts'] = [
            {'id': 'a', 'src': 'missing.mp4', 'start': 1, 'end': 3, 'placement': 'upper-middle'},
            {'id': 'b', 'src': 'host.mp4', 'start': 2, 'end': 4, 'placement': 'full'},
        ]
        errors, _ = module.validate(self.timeline, self.public)
        self.assertTrue(any('missing' in e for e in errors))
        self.assertTrue(any('placement' in e for e in errors))
        self.assertTrue(any('overlap' in e for e in errors))

    def test_media_escape_and_zero_frame_duration_are_rejected(self):
        self.timeline['hosts'] = [{'id': 'a', 'src': '../private.mp4', 'start': 1, 'end': 1.001, 'placement': 'full'}]
        errors, _ = module.validate(self.timeline, self.public)
        self.assertTrue(any('relative path' in e for e in errors))
        self.assertTrue(any('one frame' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
