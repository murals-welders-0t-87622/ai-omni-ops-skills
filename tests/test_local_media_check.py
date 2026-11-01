import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import wave
import zlib

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/brand-omni-growth-expert/scripts/check_local_media.py'
spec = importlib.util.spec_from_file_location('check_local_media', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def png_chunk(name, data):
    return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data) & 0xffffffff)


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg and ffprobe are required')
class LocalMediaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.image = root / 'synthetic-image.mp4'
        raw = b'\x00' + bytes([255, 0, 0, 0, 255, 0])
        raw += b'\x00' + bytes([0, 0, 255, 255, 255, 255])
        self.image.write_bytes(b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 2, 8, 2, 0, 0, 0)) + png_chunk(b'IDAT', zlib.compress(raw)) + png_chunk(b'IEND', b''))
        self.audio = root / 'synthetic-audio.wav'
        with wave.open(str(self.audio), 'wb') as out:
            out.setnchannels(1); out.setsampwidth(2); out.setframerate(8000)
            out.writeframes(b''.join(struct.pack('<h', int(12000 * math.sin(2 * math.pi * 440 * i / 8000))) for i in range(8000)))
        self.video = root / 'synthetic-video.png'
        result = subprocess.run([shutil.which('ffmpeg'), '-nostdin', '-v', 'error', '-f', 'lavfi', '-i',
                                 'color=c=blue:s=32x32:r=5:d=1', '-c:v', 'mpeg4', '-f', 'mp4', str(self.video)],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise RuntimeError('could not create synthetic video')

    def tearDown(self):
        self.tmp.cleanup()

    def test_real_media_decodes_and_detects_type_not_extension(self):
        for kind, file in [('image', self.image), ('audio', self.audio), ('video', self.video)]:
            with self.subTest(kind=kind):
                expected = hashlib.sha256(file.read_bytes()).hexdigest()
                result = mod.check({'kind': kind, 'filePath': str(file), 'expectedSha256': expected})
                self.assertEqual(result['sha256'], expected)
                self.assertTrue(result['sampled_decode'])
                self.assertFalse(result['entire_file_decoded'])
                self.assertFalse(result['server_storage_verified'])

    def test_wrong_kind_corruption_and_hash_are_rejected(self):
        for kind, file in [('video', self.image), ('image', self.video), ('audio', self.video)]:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                mod.check({'kind': kind, 'filePath': str(file)})
        with self.assertRaises(ValueError):
            mod.check({'kind': 'image', 'filePath': str(self.image), 'expectedSha256': '0' * 64})
        self.image.write_bytes(b'not-an-image')
        with self.assertRaises(ValueError):
            mod.check({'kind': 'image', 'filePath': str(self.image)})

    def test_missing_tools_and_remote_path_are_not_success(self):
        with mock.patch.object(mod.shutil, 'which', return_value=None), self.assertRaises(ValueError):
            mod.check({'kind': 'image', 'filePath': str(self.image)})
        with self.assertRaises(ValueError):
            mod.check({'kind': 'image', 'filePath': 'https://example.invalid/image.png'})

    def test_decode_without_frames_is_not_success(self):
        probe = json.dumps({'format': {'format_name': 'png_pipe'},
                            'streams': [{'codec_type': 'video'}]}).encode()
        with mock.patch.object(mod, 'run', side_effect=[probe, b'#format: frame checksums\n']), self.assertRaisesRegex(ValueError, 'no decodable samples'):
            mod.check({'kind': 'image', 'filePath': str(self.image)})

    def test_cli_does_not_claim_server_storage(self):
        req = {'kind': 'image', 'filePath': str(self.image)}
        result = subprocess.run([sys.executable, str(SCRIPT)], input=json.dumps(req, ensure_ascii=False),
                                capture_output=True, text=True, encoding='utf-8', timeout=30,
                                env={**os.environ, 'PYTHONUTF8': '0'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['server_storage_verified'])


if __name__ == '__main__':
    unittest.main()
