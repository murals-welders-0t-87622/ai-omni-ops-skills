# -*- coding: utf-8 -*-
"""截图健康度检查：判断一批 PNG 是不是「正常版面」而不是空白/纯噪点。

★ 为什么要这个（本轮踩的坑，勿删）：
  用 Read 直接看 PNG 时，大图会被缩放，肉眼判断很不可靠 ——
  _v7chk/fix_s07.png 被我读成「大面积噪点」，
  而 _chart_probe.py 独立测得 S07 图表宽 1496 / 畸变 1.07 完全正常，
  两个结论互相矛盾。既然目视不可信，就改用像素统计做机器判据。

判据（三条一起看，缺一条都会误判）：
  1) mean   —— 整体亮度。纸艺风格底色 ~247，成片帧应落在 150~250。
                mean > 252 且 std 极小 → 几乎纯白 = 页面没渲染出来。
  2) std    —— 明暗跨度。std < 6 → 画面几乎没内容（空白页）。
  3) 暗像素占比 dark%(L<110) —— 墨色文字/描边的占比。
                正常版面有 1%~25% 的暗像素；
                0% → 一个字都没画上；> 60% → 整片黑（被遮挡或渲染异常）。

用法： python _shot_health.py _v7chk/shot_v8_s07.png ...
      python _shot_health.py            # 默认扫 _v7chk/shot_v8_*.png
★ 必须用系统 Python 3.11 跑（勿删这条，本轮踩过）：
  numpy / Pillow 只装在系统解释器里，托管的 3.13.12 里没有。
    C:/Users/.../AppData/Local/Programs/Python/Python311/python.exe _shot_health.py
  裸 `python _shot_health.py` 会 ModuleNotFoundError: No module named 'numpy'，
  而且因为 stderr 走了管道，外层还会显示 exit=0，很容易误判成「跑过了」。
"""
import glob
import io
import os
import sys

import numpy as np
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                              errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))

files = [a for a in sys.argv[1:] if a.lower().endswith('.png')]
if not files:
    files = sorted(glob.glob(os.path.join(BASE, '_v7chk', 'shot_v8_*.png')))
if not files:
    print('没找到待检图片')
    sys.exit(2)

print('%-22s %6s %8s %7s %7s %7s  %s'
      % ('文件', '尺寸', 'mean', 'std', 'dark%', 'white%', '判定'))
print('-' * 82)

fails = []
for f in files:
    im = Image.open(f).convert('L')
    a = np.asarray(im).astype(np.float32)
    mean = float(a.mean())
    std = float(a.std())
    dark = float((a < 110).mean() * 100.0)
    white = float((a > 250).mean() * 100.0)

    bad = []
    if std < 6:
        bad.append('几乎空白(std过小)')
    if mean > 252 and std < 12:
        bad.append('纯白未渲染')
    if dark < 0.2:
        bad.append('无墨色内容')
    if dark > 60:
        bad.append('整片过暗')
    ok = not bad

    print('%-22s %6s %8.1f %7.1f %6.2f%% %6.1f%%  %s'
          % (os.path.basename(f), '%dx%d' % im.size, mean, std, dark, white,
             'ok' if ok else '✗ ' + ' / '.join(bad)))
    if not ok:
        fails.append(os.path.basename(f))

print()
print('=== 结果 ===')
print('检查 %d 张   FAIL %d' % (len(files), len(fails)))
if fails:
    print('异常：' + ', '.join(fails))
    sys.exit(1)
print('全部通过：截图均为正常版面（有底色、有墨色、明暗跨度正常）')
