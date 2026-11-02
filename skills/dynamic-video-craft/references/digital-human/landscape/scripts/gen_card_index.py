# -*- coding: utf-8 -*-
"""扫描 src/cards/*.tsx，生成 src/cards/index.ts 卡片注册表。

提取：
  - default export 组件名（export default function Xxx）
  - meta.durationInFrames（卡片自身节奏长度，用于 Freeze 定格）

产出：
  CARDS: Record<卡片ID, { Comp, dur }>
  CARD_IDS: string[]

用法：
  python gen_card_index.py --dir <remotion 工程目录>
  python gen_card_index.py                 # 默认取脚本所在目录的 ../src/cards
"""
import os
import re
import sys

RE_DEFAULT = re.compile(r'export\s+default\s+function\s+(\w+)')
RE_META = re.compile(r'durationInFrames:\s*(\d+)')

DEFAULT_DUR = 90


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    if '--dir' in sys.argv:
        i = sys.argv.index('--dir')
        base = sys.argv[i + 1]

    cards = os.path.join(base, 'src', 'cards')
    if not os.path.isdir(cards):
        # 也允许直接传 cards 目录
        cards = base
    out = os.path.join(cards, 'index.ts')
    if not os.path.isdir(cards):
        print('未找到 cards 目录：%s' % cards)
        return 1

    rows = []
    for fn in sorted(os.listdir(cards)):
        if not fn.endswith('.tsx') or fn == 'index.ts':
            continue
        cid = fn[:-4]
        src = open(os.path.join(cards, fn), encoding='utf-8').read()
        m = RE_DEFAULT.search(src)
        if not m:
            print('跳过（无 default export）：%s' % fn)
            continue
        comp = m.group(1)
        dm = RE_META.search(src)
        dur = int(dm.group(1)) if dm else DEFAULT_DUR
        rows.append((cid, comp, dur))

    L = [
        '// 自动生成 — 由 scripts/gen_card_index.py 扫描 cards/*.tsx 生成，勿手改',
        "import React from 'react';",
        '',
    ]
    for cid, comp, _d in rows:
        L.append("import %s from './%s';" % (comp, cid))
    L += [
        '',
        'export interface CardEntry {',
        '  Comp: React.FC<{ hostSrc?: string }>;',
        '  dur: number; // meta.durationInFrames：卡片自身节奏长度',
        '}',
        '',
        'export const CARDS: Record<string, CardEntry> = {',
    ]
    for cid, comp, dur in rows:
        L.append("  '%s': { Comp: %s, dur: %d }," % (cid, comp, dur))
    L += [
        '};',
        '',
        'export const CARD_IDS = Object.keys(CARDS);',
        '',
    ]

    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L))

    print('生成 %s：%d 个卡片' % (out, len(rows)))
    for cid, comp, dur in rows:
        print('  %-28s %-28s %d帧' % (cid, comp, dur))
    return 0


if __name__ == '__main__':
    sys.exit(main())
