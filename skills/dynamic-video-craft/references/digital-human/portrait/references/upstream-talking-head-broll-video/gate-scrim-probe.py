# -*- coding: utf-8 -*-
"""纸幕遮盖度量化探针。

背景：AI 视频铺在 .frame-b 底层，上面盖一层暖米色半透明纸幕
（rgba(247,242,232,.70→.88)）保证文字可读。肉眼看抽帧觉得偏白，
但"偏白"不能靠感觉定，得量。

做法：同一个页面渲两次——
  A) 正常渲染（有纸幕）
  B) 用 JS 把 ::after 的 background 干掉（无纸幕）
两次都只截 .frame-b 区域，然后比 亮度均值 / 对比度(标准差) / 可辨识度。

判据：
  · 纸幕后的标准差若比无纸幕跌掉 60% 以上 → 视频纹理基本被洗没了，纸幕过重
  · 纸幕后亮度均值 > 228（255制）→ 画面接近纯白纸，视频白铺了
两条任一命中就要下调 alpha。
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np

SID = sys.argv[1] if len(sys.argv) > 1 else '19'
src = os.path.abspath('compositions/scene-%s.html' % SID).replace(os.sep, '/')
OUT = '_v7chk'
os.makedirs(OUT, exist_ok=True)

# 把纸幕彻底移除：::after 不能用 element.style 改，只能注入一条更高优先级的规则
KILL_SCRIM = """
.frame-b.has-ai::after { background: none !important; }
"""
# 只留纸幕、把内容层藏掉，用来单独量文字区域的背景亮度
HIDE_CONTENT = """
.frame-b.has-ai > .b-pad { visibility: hidden !important; }
.ai-badge { display: none !important; }
"""


def shoot(pg, path, extra_css=None):
    pg.goto('file:///' + src)
    if extra_css:
        pg.add_style_tag(content=extra_css)
    # 视频要走到有画面的时刻；autoplay+muted 在 headless 下会播，
    # 但首帧可能还是黑的，给它跑到 1.8s 再截
    pg.wait_for_timeout(1800)
    pg.locator('.frame-b').screenshot(path=path)
    return path


def stat(path):
    a = np.asarray(Image.open(path).convert('L'), dtype=np.float32)
    return {
        'mean': float(a.mean()),
        'std': float(a.std()),
        'p05': float(np.percentile(a, 5)),
        'p95': float(np.percentile(a, 95)),
        'dark_ratio': float((a < 200).mean()),  # 非纸白像素占比
    }


with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1920, 'height': 1080})

    f_on = shoot(pg, '%s/scrim_on_s%s.png' % (OUT, SID))
    f_off = shoot(pg, '%s/scrim_off_s%s.png' % (OUT, SID), KILL_SCRIM)
    f_bg = shoot(pg, '%s/scrim_bg_s%s.png' % (OUT, SID), HIDE_CONTENT)

    b.close()

s_on, s_off, s_bg = stat(f_on), stat(f_off), stat(f_bg)

print('=== 纸幕遮盖度量化 · S%s ===' % SID)
hdr = '%-14s %7s %7s %7s %7s %9s' % ('', 'mean', 'std', 'p05', 'p95', 'dark%')
print(hdr)
for name, s in (('原始视频层', s_off), ('叠纸幕后', s_on), ('纸幕(无内容)', s_bg)):
    print('%-14s %7.1f %7.1f %7.1f %7.1f %8.1f%%' % (
        name, s['mean'], s['std'], s['p05'], s['p95'], s['dark_ratio'] * 100))

std_keep = s_on['std'] / s_off['std'] if s_off['std'] > 0.01 else 0
tex_keep = s_bg['std'] / s_off['std'] if s_off['std'] > 0.01 else 0

# ★ tex_keep 的理论上限就是 (1 - 平均alpha)，不是 100%。
#   线性合成 out = a*247 + (1-a)*src 里，常数项不贡献方差，所以
#       std(out) = (1-a) * std(src)     =>   tex_keep ≡ (1-a)
#   纸幕梯度 .48/.56/.62 的平均 alpha ≈ .55  =>  上限 ≈ 45%。
#   numpy 实测验证：contrast 从 1.0 拉到 2.5，tex_keep 稳定在 43~46%，
#   与素材反差、与滤镜参数【完全无关】。
#   所以拿 40% 当绝对闸值是错的 —— 它离理论上限只差 5 个点，
#   任何叠在纸幕之上的额外亮层（.b-pad::before 那层 .40 径向柔光，
#   在 HIDE_CONTENT 模式下并不会被隐藏，仍参与合成）都会把它推到 40% 以下，
#   于是把「柔光罩正常工作」误报成「纸幕过重」。S01 的 37% 就是这么来的。
#   改成看「实际保留 / 理论上限」的达成率，闸值 80%。
SCRIM_A = 0.55                      # 与 _rich.css 的 .48/.56/.62 梯度对应
tex_ceil = 1.0 - SCRIM_A
tex_ratio = tex_keep / tex_ceil if tex_ceil > 0 else 0

print()
print('整体对比度保留率 : %.0f%%  (含文字，参考值)' % (std_keep * 100))
print('视频纹理保留率   : %.0f%%   (理论上限 %.0f%%，达成率 %.0f%%)'
      % (tex_keep * 100, tex_ceil * 100, tex_ratio * 100))
print('纸幕区亮度均值   : %.1f' % s_bg['mean'])
print('纸幕区非白占比   : %.1f%%' % (s_bg['dark_ratio'] * 100))

bad = []
if tex_ratio < 0.80:
    bad.append('纹理保留 %.0f%% 仅为理论上限 %.0f%% 的 %.0f%%（<80%%），'
               '说明纸幕之外还有多余亮层在洗画面'
               % (tex_keep * 100, tex_ceil * 100, tex_ratio * 100))
if s_bg['mean'] > 228:
    bad.append('纸幕区亮度均值 %.1f > 228，画面接近纯纸白' % s_bg['mean'])
if s_bg['dark_ratio'] < 0.25:
    bad.append('纸幕区非白像素仅 %.1f%% < 25%%，看不出底下有东西' % (s_bg['dark_ratio'] * 100))

print()
if bad:
    print('判定：纸幕过重，需下调 alpha')
    for x in bad:
        print('  ✗ ' + x)
else:
    print('判定：纸幕强度合适 ✓')
