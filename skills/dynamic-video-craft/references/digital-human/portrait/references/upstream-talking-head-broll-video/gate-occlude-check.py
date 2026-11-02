# -*- coding: utf-8 -*-
"""全局遮挡门禁：扫描所有镜次，检查是否有文字被 .frame-a 数字人小窗遮住。

★ 为什么需要这个门禁（S31 血泪教训，勿删）：
  layout-full 版式下 .frame-a 是右下角 246×328 的画中画小窗（z-index:3），
  压在 .frame-b 之上。任何钉在 B 框右下角的元素（absolute + right/bottom）
  都会被它盖住。S31 的 .ib__ratio「7 : 3」就这么被埋了，
  而文字探针只会报「Δ=15 对比度极差」，一路调颜色永远调不动。

  更麻烦的是：这类问题【看不出来】——
  页面截图里那块就是数字人的画面，不会有任何"缺了东西"的视觉提示。
  所以必须用 DOM 几何关系做机器检测。

判据：文字元素包围盒与 .frame-a 包围盒的交叠面积 / 文字自身面积。
  > 0.5  → 严重遮挡（几乎完全看不见）
  > 0.15 → 部分遮挡（边角被切）

用法： python _occlude_check.py           # 扫全部
       python _occlude_check.py 31 60     # 只扫指定镜次
"""
import glob
import io
import os
import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                              errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(BASE, 'compositions')

args = [a for a in sys.argv[1:] if a.isdigit()]
if args:
    sids = ['%02d' % int(a) for a in args]
else:
    sids = sorted(
        re.search(r'scene-(\d+)\.html', os.path.basename(f)).group(1)
        for f in glob.glob(os.path.join(COMP, 'scene-*.html')))

JS = """() => {
  const fa = document.querySelector('.frame-a');
  const fb = document.querySelector('.frame-b');
  if (!fa || !fb) return {layout: '', items: []};
  const ar = fa.getBoundingClientRect();
  const out = [];
  fb.querySelectorAll('*').forEach(el => {
    /* 只看真正承载文字的元素：有直接文本子节点、字号 >= 18px。
       容器不算（否则整个 .b-pad 都会被判成遮挡）。 */
    const hasText = [...el.childNodes].some(
      n => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasText) return;
    const cs = getComputedStyle(el);
    if (parseFloat(cs.fontSize) < 18) return;
    /* 不可见元素跳过 */
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === 'none' || s.visibility === 'hidden'
          || parseFloat(s.opacity) < 0.06) return;
    }
    const r = el.getBoundingClientRect();
    if (r.width < 10 || r.height < 8) return;
    const ox = Math.max(0, Math.min(r.right, ar.right)
                         - Math.max(r.left, ar.left));
    const oy = Math.max(0, Math.min(r.bottom, ar.bottom)
                         - Math.max(r.top, ar.top));
    const inter = ox * oy;
    if (inter <= 0) return;
    out.push({
      cls: (el.className || el.tagName).toString().slice(0, 30),
      txt: el.textContent.trim().slice(0, 16),
      fs: Math.round(parseFloat(cs.fontSize)),
      ratio: inter / (r.width * r.height),
      rect: [r.x | 0, r.y | 0, r.width | 0, r.height | 0]
    });
  });
  return {
    layout: (document.querySelector('.stage').className || ''),
    arect: [ar.x | 0, ar.y | 0, ar.width | 0, ar.height | 0],
    items: out
  };
}"""

bad = []
warn = []
print('=== 数字人小窗遮挡门禁 ===  共 %d 镜' % len(sids))
print()

with sync_playwright() as p:
    br = p.chromium.launch(
        headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    pg = br.new_page(viewport={'width': 1920, 'height': 1080})
    for sid in sids:
        f = os.path.join(COMP, 'scene-%s.html' % sid)
        if not os.path.exists(f):
            print('S%s  ✗ 文件不存在' % sid)
            continue
        pg.goto('file:///' + f.replace(os.sep, '/'))
        pg.wait_for_timeout(1500)
        r = pg.evaluate(JS)
        hits = [i for i in r['items'] if i['ratio'] > 0.15]
        if not hits:
            continue
        layout = [c for c in r['layout'].split()
                  if c.startswith('layout-')]
        print('S%s  [%s]  A框=%s' % (
            sid, layout[0] if layout else '?', r['arect']))
        for i in sorted(hits, key=lambda x: -x['ratio']):
            lvl = '严重' if i['ratio'] > 0.5 else '部分'
            print('    %s遮挡 %.0f%%  %-24s %3dpx  "%s"  %s' % (
                lvl, i['ratio'] * 100, i['cls'], i['fs'], i['txt'],
                i['rect']))
            (bad if i['ratio'] > 0.5 else warn).append(
                (sid, i['cls'], i['txt'], i['ratio']))
        print()
    br.close()

print('─' * 66)
if bad:
    print('✗ %d 处严重遮挡（几乎完全被数字人挡住，成片里看不见）：' % len(bad))
    for sid, cls, txt, ra in bad:
        print('   S%s  %-24s "%s"  %.0f%%' % (sid, cls, txt, ra * 100))
if warn:
    print('⚠ %d 处部分遮挡（边角被切，可接受但建议检查）：' % len(warn))
    for sid, cls, txt, ra in warn:
        print('   S%s  %-24s "%s"  %.0f%%' % (sid, cls, txt, ra * 100))
if not bad and not warn:
    print('✓ 全部镜次无文字被数字人小窗遮挡')
sys.exit(1 if bad else 0)
