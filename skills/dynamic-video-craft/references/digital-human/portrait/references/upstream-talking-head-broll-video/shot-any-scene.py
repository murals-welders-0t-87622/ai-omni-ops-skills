# -*- coding: utf-8 -*-
"""通用「按镜号截图」工具 —— 目视验收专用。

★ 为什么要单独写这个（勿删，避免下次又翻半天）：
  仓里已有的 _shot*.py 全是专项工具，都不能按镜号截图：
    _shot.py   内嵌一段 SPLIT 版式的 HTML 字符串，专门逐像素量中缝宽度
    _shot2.py  批量但绑定了固定检查逻辑
    _shot3.py  只打开 demo.html，逐个 stage 读子框几何查两两重叠
    _shot_check.py / _comp_vis.py / _crop_a.py  各自的专项校验
  而验收 layout-full 的遮挡避让、图表缩窄这类改动，需要的就是
  「给我 scene-NN 的成品帧」这一件最朴素的事。

关键参数说明：
  viewport 1920x1080 + device_scale_factor=1
    → 与 _render60.py 的渲染尺寸一致，量出来的几何才能对得上
      （.frame-a 小窗 right:72 / 246x328 那套坐标就是按 1920 算的）
  等待 2600ms
    → 场景动画最长的一条 delay + duration 约 2.2s（fadeUp/plugIn/
      数据条生长都在这个量级），等满才能拍到【终态】版面。
      等太短会拍到动画中途，误判成「元素缺失/位置不对」。

用法：
  python _shot_any.py 07 10 12          # 指定镜次
  python _shot_any.py 07 --tag fix2     # 自定义文件名后缀
输出：_v7chk/shot_<tag>_sNN.png
"""
import io
import os
import sys

from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                              errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, '_v7chk')
os.makedirs(OUT, exist_ok=True)

args = [a for a in sys.argv[1:]]
tag = 'v8'
if '--tag' in args:
    i = args.index('--tag')
    tag = args[i + 1]
    del args[i:i + 2]

# ★ 不要 lstrip('0')：HTML 文件名是零填充的 scene-08.html（老坑）
sids = [a.zfill(2) for a in args if a.isdigit()]
if not sids:
    print('用法: python _shot_any.py 07 10 12 [--tag fix2]')
    sys.exit(2)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1920, 'height': 1080},
                    device_scale_factor=1)
    for sid in sids:
        f = os.path.join(BASE, 'compositions', 'scene-%s.html' % sid)
        if not os.path.exists(f):
            print('S%s  ✗ 页面不存在: %s' % (sid, f))
            continue
        pg.goto('file:///' + f.replace('\\', '/'))
        pg.wait_for_timeout(2600)
        png = os.path.join(OUT, 'shot_%s_s%s.png' % (tag, sid))
        pg.screenshot(path=png)
        # 顺手把版式与两个画框的几何打出来，和截图对照着看
        geo = pg.evaluate("""() => {
          const g = s => { const e = document.querySelector(s);
            if (!e) return null; const r = e.getBoundingClientRect();
            return [Math.round(r.x), Math.round(r.y),
                    Math.round(r.width), Math.round(r.height)]; };
          const st = document.querySelector('.stage');
          const lay = st ? [...st.classList].find(c => c.startsWith('layout-')) : '';
          return {lay: lay || '?', a: g('.frame-a'), b: g('.frame-b')};
        }""")
        print('S%s  %-14s A=%s  B=%s  → %s'
              % (sid, geo['lay'], geo['a'], geo['b'], os.path.basename(png)))
    b.close()
print('\n完成，输出目录: _v7chk/')
