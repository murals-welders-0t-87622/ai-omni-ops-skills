# -*- coding: utf-8 -*-
"""单点诊断器：把某镜某选择器下的文字元素的实际计算样式打出来。

用途：文字探针报 LOW 之后，用它区分三类根因 ——
  1) 元素自身/祖先 opacity 被动画压低 → 纸板半透明，暗视频透穿
  2) 元素没有底衬（background / box-shadow 都是 none）→ 直接压在视频上
  3) 元素溢出画框 → 量到的是画框外页面底色（见 _text_probe.py 注释）

用法： python _diag_low.py 09 ".vs__t, .vs__s"
"""
import io
import os
import sys

from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                              errors='replace')

SID = sys.argv[1]
SEL = sys.argv[2] if len(sys.argv) > 2 else '*'

JS = """(sel) => {
  const out = [];
  const fb = document.querySelector('.frame-b');
  const fr = fb.getBoundingClientRect();
  fb.querySelectorAll(sel).forEach(el => {
    const cs = getComputedStyle(el);
    const rc = el.getBoundingClientRect();
    if (rc.width < 20) return;
    if (parseFloat(cs.fontSize) < 20) return;
    const chain = [];
    for (let n = el; n && n !== document.body && chain.length < 4;
         n = n.parentElement) {
      const s = getComputedStyle(n);
      chain.push((n.className || n.tagName).toString().slice(0, 24)
        + '[o=' + s.opacity + ' bg=' + s.backgroundColor + ']');
    }
    out.push({
      txt: el.textContent.trim().slice(0, 12),
      fs: cs.fontSize,
      color: cs.color,
      bg: cs.backgroundColor,
      shadow: cs.boxShadow.slice(0, 48),
      stroke: cs.webkitTextStrokeWidth + ' / ' + cs.paintOrder,
      rect: [rc.x | 0, rc.y | 0, rc.width | 0, rc.height | 0],
      outside: rc.bottom > fr.bottom + 2 || rc.top < fr.top - 2,
      chain: chain
    });
  });
  return out;
}"""

src = os.path.abspath('compositions/scene-%s.html' % SID).replace(os.sep, '/')
with sync_playwright() as p:
    b = p.chromium.launch(
        headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto('file:///' + src)
    pg.wait_for_timeout(2400)
    rows = pg.evaluate(JS, SEL)
    b.close()

print('=== S%s  选择器 %s  共 %d 个 ===' % (SID, SEL, len(rows)))
for r in rows:
    print()
    print('  文本   : %s' % r['txt'])
    print('  字号   : %s   墨色: %s' % (r['fs'], r['color']))
    print('  自身底 : %s' % r['bg'])
    print('  阴影   : %s' % (r['shadow'] or '(none)'))
    print('  描边   : %s' % r['stroke'])
    print('  矩形   : %s   溢出画框: %s' % (r['rect'], r['outside']))
    print('  祖先链 : %s' % ' < '.join(r['chain']))
