# -*- coding: utf-8 -*-
"""文字可读性探针（纸幕降 alpha 后的反向校验）。

降纸幕 alpha 让视频透出来是好事，但代价可能是文字被纹理啃。
这里不问"好不好看"，只量一件事：每个文字块所在矩形内，
文字墨色 与 其紧邻背景 的亮度差是否够大。

做法：对每个文字元素取其自身包围盒，量盒内的
  · 暗部（文字笔画，L<110）均值  = ink
  · 亮部（背景，L>170）均值      = bg
对比度指标 = bg - ink，WCAG 换算下 >=110 大致相当于 4.5:1 以上，
视频压制场景取 100 作闸——低于这个数字幕上电视就发虚。
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

SID = sys.argv[1] if len(sys.argv) > 1 else '19'
# 基线模式：把 AI 视频层整层拿掉，只留纯 HTML。
# 用来分离"文字对比度不足"的归因——
# 如果基线同样 LOW，那是组件配色本身如此（比如芥末黄粗体压纸卡，
# 亮度差天然就小），跟纸幕 alpha 无关，不该为它把视频再压回去。
BASE = '--base' in sys.argv
src = os.path.abspath('compositions/scene-%s.html' % SID).replace(os.sep, '/')
OUT = '_v7chk'
os.makedirs(OUT, exist_ok=True)

KILL_AI = """
.ai-vid { display: none !important; }
.frame-b.has-ai::after { background: none !important; }
.frame-b.has-ai > .b-pad::before { background: none !important; }
"""

# 收集"承载正文/标题的元素"的包围盒。只要有直接文本子节点、
# 且字号 >= 20px 的元素，避免把整个容器算进来。
JS = """() => {
  const out = [];
  document.querySelectorAll('.frame-b *').forEach(el => {
    const hasText = [...el.childNodes].some(
      n => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasText) return;
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize);
    if (fs < 20) return;
    /* ★ 必须排掉不可见元素（血泪教训，勿删）：
       .is-second .rule-strip / .corner-fold 等副组件图形层是
       `display:none !important` 隐藏的。隐藏元素的 getBoundingClientRect()
       在某些排版下仍会返回非零矩形（父级 flex 残留 / transform 影响），
       ROI 落到一块纯纸白区域上，dark/light 都取不满 12 像素，
       于是走到「极差」兜底分支算出 Δ=39 并报 LOW(极差) ——
       S01 的那处假阳性就是这么来的（真正可见的那条 rule-strip b Δ=145 已达标）。
       判据用三件套：display / visibility / opacity，并逐级检查祖先，
       因为隐藏往往加在容器上而不是文字元素自己身上。 */
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === 'none' || s.visibility === 'hidden'
          || parseFloat(s.opacity) < 0.06) return;
    }
    const r = el.getBoundingClientRect();
    if (r.width < 40 || r.height < 14) return;
    /* ★ 溢出画框检测（S01 实测 bug，勿删）：
       .b-pad 是 overflow:visible（不能改 hidden，会裁掉 box-shadow 底衬），
       子元素纵向堆太多就会漏到 .frame-b 之外。这种元素在成片里
       【根本看不见】，但 DOM 里它存在，照常量它就会把 ROI 落到
       画框外的页面底色上 —— S01 实测那块 min=156 max=195、
       一个暗像素都没有，于是走「极差」兜底分支报 Δ=39 LOW。
       结果是把版式溢出伪装成配色问题，一路去调颜色越调越不对。
       所以这里单独打标，下游当【布局错误】单独报，不混进对比度统计。 */
    const fb = document.querySelector('.frame-b');
    let outside = false;
    /* ★ SVG 内部元素排除在溢出检测之外（S31 实测误判，勿删）：
       <text> 等 SVG 子元素的 getBoundingClientRect 在父级 svg 带
       viewBox + preserveAspectRatio 时返回的是【用户坐标系】的值，
       不是屏幕像素 —— S31 的「水上」「水下」量出 bottom=439/548，
       看着像溢出，实际它们稳稳在画框（bottom=1132）内。
       溢出问题只发生在 HTML 流式布局的块级元素上（.b-pad 的直接子孙），
       所以这里用 el.ownerSVGElement 判定，SVG 内的直接跳过检测。 */
    if (fb && !el.ownerSVGElement) {
      const fr = fb.getBoundingClientRect();
      outside = (r.bottom > fr.bottom + 2) || (r.top < fr.top - 2)
             || (r.right > fr.right + 2) || (r.left < fr.left - 2);
    }
    out.push({cls: (el.className || el.tagName).toString().slice(0, 30),
              fs: Math.round(fs), txt: el.textContent.trim().slice(0, 14),
              x: r.x, y: r.y, w: r.width, h: r.height, outside: outside});
  });
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch(headless=True,
                          args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})
    pg.goto('file:///' + src)
    if BASE:
        pg.add_style_tag(content=KILL_AI)
    pg.wait_for_timeout(2200)   # 等动画落位，否则量到 fadeUp 中途的半透明态
    boxes = pg.evaluate(JS)
    shot = '%s/text_s%s%s.png' % (OUT, SID, '_base' if BASE else '')
    pg.screenshot(path=shot)
    b.close()

img = np.asarray(Image.open(shot).convert('L'), dtype=np.float32)
print('=== 文字可读性 · S%s%s ===  (共 %d 个文字块)' % (
    SID, ' [基线·无AI视频]' if BASE else ' [含AI视频]', len(boxes)))
print('%-30s %4s %6s %6s %7s  %s' % ('元素', 'px', 'ink', 'bg', 'Δ', '判定'))

fails = []
overflow = []
for bx in boxes:
    # ★ 溢出画框的元素单独归类，不参与对比度统计（详见 JS 段注释）
    if bx.get('outside'):
        overflow.append((bx['cls'], bx['txt'], int(bx['y'] + bx['h'])))
        print('%-30s %4d %6s %6s %7s  %s' % (
            bx['cls'], bx['fs'], '-', '-', '-', '溢出画框(不计)'))
        continue
    x0, y0 = int(max(0, bx['x'])), int(max(0, bx['y']))
    x1 = int(min(img.shape[1], bx['x'] + bx['w']))
    y1 = int(min(img.shape[0], bx['y'] + bx['h']))
    if x1 <= x0 or y1 <= y0:
        continue
    roi = img[y0:y1, x0:x1]
    dark, light = roi[roi < 110], roi[roi > 170]
    if dark.size < 12 or light.size < 12:
        # 纯色块或反白字（白字压深底），换一套判据：整体极差
        d = float(roi.max() - roi.min())
        ok = d >= 100
        print('%-30s %4d %6s %6s %7.0f  %s' % (
            bx['cls'], bx['fs'], '-', '-', d, 'OK' if ok else 'LOW(极差)'))
        if not ok:
            fails.append((bx['cls'], d))
        continue
    ink, bg = float(dark.mean()), float(light.mean())
    d = bg - ink
    ok = d >= 100
    print('%-30s %4d %6.0f %6.0f %7.0f  %s' % (
        bx['cls'], bx['fs'], ink, bg, d, 'OK' if ok else 'LOW'))
    if not ok:
        fails.append((bx['cls'], d))

print()
if overflow:
    print('⚠ %d 个文字块溢出 .frame-b 画框（版式错误，非配色问题）：' % len(overflow))
    for c, t, bot in overflow:
        print('   %-30s "%s"  bottom=%d' % (c, t, bot))
    print()
if fails:
    print('✗ %d 个文字块对比度不足（Δ<100）：' % len(fails))
    for c, d in fails:
        print('   %-30s Δ=%.0f' % (c, d))
else:
    print('✓ 全部文字块对比度达标（Δ>=100）')
