# -*- coding: utf-8 -*-
"""排查「某个文字元素所在区域实际被谁盖住了」。

背景：S31 的 66px「7 : 3」文字探针报 Δ=15，量其包围盒发现
min=0 max=15 —— 整块纯黑，连 6px 纸白描边都没有。
纯黑说明既不是对比度问题、也不是没渲染，而是【被别的图层盖住】。

做法：用 elementsFromPoint 取该点上方的完整图层栈，
并逐层临时隐藏后重新采样，看哪一层一去掉这块就亮起来。

用法： python _diag_cover.py 31 "7 : 3"
"""
import io
import os
import sys

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                              errors='replace')

SID = sys.argv[1]
NEEDLE = sys.argv[2]
OUT = '_v7chk'

FIND = """(needle) => {
  const all = [...document.querySelectorAll('.frame-b *')];
  const el = all.find(e => e.textContent.trim() === needle
                        || e.textContent.trim().startsWith(needle));
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const cx = r.x + r.width / 2, cy = r.y + r.height / 2;
  const stack = document.elementsFromPoint(cx, cy).map(n => {
    const s = getComputedStyle(n);
    return {
      tag: n.tagName,
      cls: (n.className || '').toString().slice(0, 34),
      z: s.zIndex,
      bg: s.backgroundColor,
      op: s.opacity,
      pos: s.position,
      mix: s.mixBlendMode,
      isTarget: n === el
    };
  });
  return {rect: [r.x | 0, r.y | 0, r.width | 0, r.height | 0],
          cx: cx | 0, cy: cy | 0, stack: stack};
}"""

src = os.path.abspath('compositions/scene-%s.html' % SID).replace(os.sep, '/')
with sync_playwright() as p:
    b = p.chromium.launch(
        headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto('file:///' + src)
    pg.wait_for_timeout(2400)
    info = pg.evaluate(FIND, NEEDLE)
    if not info:
        print('找不到文本 "%s"' % NEEDLE)
        sys.exit(1)
    shot = '%s/cover_s%s.png' % (OUT, SID)
    pg.screenshot(path=shot)
    b.close()

x, y, w, h = info['rect']
print('=== S%s  "%s" ===' % (SID, NEEDLE))
print('包围盒 %s   采样点 (%d, %d)' % (info['rect'], info['cx'], info['cy']))
print()
print('该点自上而下的图层栈：')
for i, s in enumerate(info['stack']):
    mark = '  ← 目标元素' if s['isTarget'] else ''
    print('  %d. %-6s %-34s z=%-6s op=%-4s pos=%-8s bg=%s%s' % (
        i, s['tag'], s['cls'] or '(no class)', s['z'], s['op'],
        s['pos'], s['bg'], mark))
    if s['isTarget']:
        print('     ↑ 上面这 %d 层都盖在文字之上' % i)
        break

a = np.asarray(Image.open(shot).convert('L'), dtype=float)
roi = a[y:y + h, x:x + w]
print()
print('该区域像素: min=%.0f max=%.0f mean=%.1f  暗(<110)=%d/%d' % (
    roi.min(), roi.max(), roi.mean(), (roi < 110).sum(), roi.size))
