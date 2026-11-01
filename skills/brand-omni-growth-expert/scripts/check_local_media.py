#!/usr/bin/env python3
"""Read-only sampled validation of a local media file, not proof of remote storage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

IMAGE_FORMATS = {'image2', 'png_pipe', 'jpeg_pipe', 'bmp_pipe', 'webp_pipe', 'tiff_pipe', 'gif', 'apng'}


def run(args):
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('media inspection failed or timed out') from exc
    if result.returncode:
        raise ValueError('media inspection or sampled decode failed')
    return result.stdout


def check(request):
    if not isinstance(request, dict) or request.get('kind') not in ('image', 'audio', 'video'):
        raise ValueError('kind must be image, audio or video')
    location = request.get('filePath')
    if not isinstance(location, str) or not location.strip() or '://' in location:
        raise ValueError('a local file path is required')
    path = Path(location).resolve(strict=True)
    before = path.stat()
    if not path.is_file() or not before.st_size:
        raise ValueError('local file is empty or unavailable')
    ffprobe, ffmpeg = shutil.which('ffprobe'), shutil.which('ffmpeg')
    if not ffprobe or not ffmpeg:
        raise ValueError('ffmpeg and ffprobe are required for media inspection')
    output = run([ffprobe, '-v', 'error', '-protocol_whitelist', 'file,pipe', '-show_entries',
                  'format=format_name:stream=codec_type', '-of', 'json', str(path)])
    try:
        probe = json.loads(output.decode('utf-8'))
        formats = set(probe['format']['format_name'].split(','))
        streams = {s.get('codec_type') for s in probe['streams'] if isinstance(s, dict)}
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
        raise ValueError('media structure could not be identified') from exc
    image = bool(formats & IMAGE_FORMATS)
    kind = request['kind']
    if kind == 'image' and (not image or 'video' not in streams):
        raise ValueError('file is not a supported image')
    if kind == 'video' and (image or 'video' not in streams):
        raise ValueError('file is not a supported video')
    if kind == 'audio' and ('audio' not in streams or 'video' in streams):
        raise ValueError('file is not a supported audio-only file')
    cmd = [ffmpeg, '-nostdin', '-v', 'error', '-xerror', '-protocol_whitelist', 'file,pipe', '-i', str(path)]
    cmd += ['-map', '0:a:0', '-t', '1'] if kind == 'audio' else ['-map', '0:v:0', '-frames:v', '1']
    frame_hash = run(cmd + ['-f', 'framehash', '-'])
    if not any(line.strip() and not line.lstrip().startswith(b'#') for line in frame_hash.splitlines()):
        raise ValueError('media contains no decodable samples')
    digest = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(chunk)
    actual = digest.hexdigest()
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('local file changed during inspection')
    expected = request.get('expectedSha256')
    if expected is not None:
        if not isinstance(expected, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', expected):
            raise ValueError('expectedSha256 must be a SHA-256 hex digest')
        if actual != expected.lower():
            raise ValueError('local file digest does not match expected digest')
    return {'kind': kind, 'sizeBytes': after.st_size, 'sha256': actual,
            'sampled_decode': True, 'entire_file_decoded': False,
            'server_storage_verified': False, 'business_quality_verified': False}


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    argparse.ArgumentParser(description=__doc__).parse_args()
    try:
        result = check(json.load(sys.stdin))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
