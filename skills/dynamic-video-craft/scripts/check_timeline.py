#!/usr/bin/env python3
"""Validate starter timelines and optionally export subtitles. Standard library only."""
import argparse
import json
import math
from pathlib import Path


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def frame(seconds, fps):
    return math.floor(seconds * fps + 0.5)


def validate(data, public_dir, require_voiceover=False):
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ['Root must be an object'], warnings
    for name in ['fps', 'width', 'height', 'duration']:
        value = data.get(name)
        if not finite(value) or value <= 0:
            errors.append(f'{name} must be a positive finite number')
    if errors:
        return errors, warnings
    fps, duration = data['fps'], data['duration']
    for name in ['fps', 'width', 'height']:
        if data[name] != int(data[name]):
            errors.append(f'{name} must be an integer in this starter')
    if frame(duration, fps) < 1:
        errors.append('Composition must contain at least one frame')
    if data.get('mode') not in ['promo', 'explainer', 'shot']:
        errors.append('mode must be promo, explainer, or shot')
    palette = data.get('palette', {})
    for key in ['background', 'surface', 'text', 'muted', 'accent']:
        if not isinstance(palette.get(key), str) or not palette[key].strip():
            errors.append(f'palette.{key} must be a color string')
    arrays = {}
    for name in ['scenes', 'events', 'anchors', 'captions']:
        value = data.get(name, [])
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            errors.append(f'{name} must be an array of objects')
            value = []
        arrays[name] = value

    def keyed(items, name):
        result = {}
        for item in items:
            identifier = item.get('id')
            if not isinstance(identifier, str) or not identifier:
                errors.append(f'{name}: missing string id')
            elif identifier in result:
                errors.append(f'{name}: duplicate id {identifier}')
            else:
                result[identifier] = item
        return result

    def interval(item, label):
        a, b = item.get('start'), item.get('end')
        if not finite(a) or not finite(b) or not 0 <= a < b <= duration:
            errors.append(f'{label}: invalid start/end interval')
            return False
        return True

    def media(value, label):
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{label}: missing media path')
            return
        normalized = value.replace('\\', '/')
        path = Path(normalized)
        if ':' in normalized or path.is_absolute() or '..' in path.parts or normalized.startswith('/'):
            errors.append(f'{label}: must be a relative path inside public/')
            return
        resolved = (public_dir / path).resolve()
        if not resolved.is_relative_to(public_dir.resolve()) or not resolved.is_file():
            errors.append(f'{label}: missing or out-of-root asset {value}')

    scenes = keyed(arrays['scenes'], 'scenes')
    anchors = keyed(arrays['anchors'], 'anchors')
    events = keyed(arrays['events'], 'events')
    valid_scenes = {}
    previous = 0
    if not scenes:
        errors.append('At least one scene is required')
    for scene in arrays['scenes']:
        label = f'scene {scene.get("id", "?")}'
        if interval(scene, label):
            a, b = frame(scene['start'], fps), frame(scene['end'], fps)
            if a != previous:
                errors.append(f'{label}: gap/overlap at frame {a}, expected {previous}')
            if a == b:
                errors.append(f'{label}: shorter than one frame')
            previous = b
            if isinstance(scene.get('id'), str):
                valid_scenes[scene['id']] = scene
        if scene.get('type') not in ['title', 'metric', 'steps', 'evidence']:
            errors.append(f'{label}: unsupported type')
        if not isinstance(scene.get('headline'), str) or not scene['headline'].strip():
            errors.append(f'{label}: headline is required')
        if scene.get('type') == 'metric' and not finite(scene.get('metric')):
            errors.append(f'{label}: metric must be finite')
        if scene.get('type') == 'evidence':
            media(scene.get('image'), label)
        if scene.get('type') == 'steps' and (not isinstance(scene.get('labels'), list) or not scene['labels'] or any(not isinstance(x, str) for x in scene['labels'])):
            errors.append(f'{label}: steps requires a nonempty list of text labels')
        if scene.get('transition', 'cut') not in ['cut', 'wipe']:
            errors.append(f'{label}: unsupported transition')
        camera = scene.get('camera', {})
        if not isinstance(camera, dict):
            errors.append(f'{label}: camera must be an object')
        else:
            for endpoint in ['from', 'to']:
                state = camera.get(endpoint, {})
                if not isinstance(state, dict) or any(not finite(v) for v in state.values()):
                    errors.append(f'{label}: invalid camera {endpoint}')
                elif state.get('scale', 1) <= 0:
                    errors.append(f'{label}: camera scale must be positive')
        if scene.get('revealEvent'):
            event = events.get(scene['revealEvent'])
            if not event or event.get('sceneId') != scene.get('id'):
                errors.append(f'{label}: revealEvent must reference an event in this scene')
    if previous != frame(duration, fps):
        errors.append('Scenes must cover the full composition duration')
    valid_anchors = {key: value for key, value in anchors.items() if interval(value, f'anchor {key}')}
    aligned = 0
    for key, event in events.items():
        at = event.get('at')
        scene = valid_scenes.get(event.get('sceneId'))
        if not finite(at) or not 0 <= at < duration:
            errors.append(f'event {key}: invalid at')
            continue
        if not scene or not scene['start'] <= at < scene['end']:
            errors.append(f'event {key}: outside its scene')
        elif scene['end'] - at < 0.5:
            warnings.append(f'event {key}: less than 0.5 seconds before scene end; check readability')
        if event.get('anchorId'):
            anchor = valid_anchors.get(event['anchorId'])
            if not anchor:
                errors.append(f'event {key}: missing/invalid anchor')
            elif abs(at - anchor['start']) > 0.100001:
                errors.append(f'event {key}: anchor mismatch exceeds 0.1 seconds')
            else:
                aligned += 1
        if event.get('sfx'):
            media(event['sfx'], f'event {key} sfx')
        if 'volume' in event and (not finite(event['volume']) or event['volume'] < 0):
            errors.append(f'event {key}: invalid volume')
    previous_end = 0
    for index, caption in enumerate(arrays['captions']):
        if interval(caption, f'caption {index}'):
            if caption['start'] < previous_end:
                errors.append(f'caption {index}: overlap or unsorted captions')
            previous_end = caption['end']
        if not isinstance(caption.get('text'), str) or not caption['text'].strip():
            errors.append(f'caption {index}: missing text')
    audio = data.get('audio', {})
    if not isinstance(audio, dict):
        errors.append('audio must be an object')
        audio = {}
    for kind in ['voiceover', 'music']:
        if kind in audio:
            track = audio[kind]
            if not isinstance(track, dict):
                errors.append(f'audio.{kind}: must be an object')
                continue
            media(track.get('src'), f'audio.{kind}')
            if not finite(track.get('volume')) or track['volume'] < 0:
                errors.append(f'audio.{kind}: invalid volume')
    if require_voiceover and ('voiceover' not in audio or not aligned):
        errors.append('Final narrated delivery requires a voiceover and at least one anchored visual event')
    return errors, warnings


def srt_time(seconds):
    total = math.floor(seconds * 1000 + 0.5)
    hours, rest = divmod(total, 3600000)
    minutes, rest = divmod(rest, 60000)
    secs, millis = divmod(rest, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{millis:03}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('timeline', type=Path)
    parser.add_argument('--public-dir', type=Path)
    parser.add_argument('--require-voiceover', action='store_true')
    parser.add_argument('--srt', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.timeline.read_text(encoding='utf-8-sig'))
        public = args.public_dir or args.timeline.resolve().parent.parent / 'public'
        errors, warnings = validate(data, public, args.require_voiceover)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    for warning in warnings:
        print(f'WARN: {warning}')
    for error in errors:
        print(f'ERROR: {error}')
    if errors:
        raise SystemExit(1)
    if args.srt:
        lines = [f'{i}\n{srt_time(c["start"])} --> {srt_time(c["end"])}\n{c["text"]}\n'
                 for i, c in enumerate(data.get('captions', []), 1)]
        args.srt.parent.mkdir(parents=True, exist_ok=True)
        args.srt.write_text('\n'.join(lines), encoding='utf-8')
    print(f'PASS: {len(data["scenes"])} scenes; {frame(data["duration"], data["fps"])} frames; {len(warnings)} warnings')


if __name__ == '__main__':
    main()
