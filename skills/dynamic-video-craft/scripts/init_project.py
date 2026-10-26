#!/usr/bin/env python3
"""Copy the bundled original starter to a new, empty video directory."""
import argparse
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--aspect', choices=['landscape', 'portrait'], default='landscape')
    parser.add_argument('--mode', choices=['promo', 'explainer', 'shot'], default='promo')
    args = parser.parse_args()
    target = args.output.expanduser().resolve()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        parser.error(f'Refusing to overwrite a nonempty directory or file: {target}')
    source = Path(__file__).resolve().parents[1] / 'assets' / 'remotion-starter'
    if not (source / 'src' / 'video.json').is_file():
        parser.error(f'Missing bundled starter: {source}')
    shutil.copytree(source, target, dirs_exist_ok=True)
    config = target / 'src' / 'video.json'
    data = json.loads(config.read_text(encoding='utf-8'))
    data['width'], data['height'] = ((1080, 1920) if args.aspect == 'portrait' else (1920, 1080))
    data['mode'] = args.mode
    config.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (target / 'public').mkdir(exist_ok=True)
    (target / 'out').mkdir(exist_ok=True)
    rows = ['# 镜头工作表', '', '以下为工程演示，请按实际内容重写。', '',
            '| 镜头 | 起止秒 | 意图 | 主体 / 素材 | 相机 / 主动作 | 转场 / 音效 |',
            '|---|---|---|---|---|---|']
    for scene in data['scenes']:
        rows.append(f"| {scene['id']} | {scene['start']}–{scene['end']} | {scene['headline']} | 待按真实内容定义 | {scene['type']} | {scene.get('transition', 'cut')} |")
    (target / 'SHOTBOOK.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print(f'Created: {target}')
    print('Next: edit src/video.json and SHOTBOOK.md, add public/ media, then npm install and npm run typecheck.')


if __name__ == '__main__':
    main()
