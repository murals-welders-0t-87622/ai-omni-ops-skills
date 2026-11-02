# -*- coding: utf-8 -*-
"""_geom_regress.py — 几何回归：验证 SPLIT 两框不叠压、且间距 = 实测中缝
   直接解析 design-tokens.css 的令牌做算术校验，不依赖浏览器渲染。
"""
import io, sys, re
sys.stdout = io.TextIOWrapper(open('_geom_regress.log', 'wb'), encoding='utf-8', write_through=True)

css = open('design-tokens.css', encoding='utf-8').read()

def tok(name):
    m = re.search(rf'--{name}\s*:\s*(-?[\d.]+)px', css)
    if not m: return None
    return float(m.group(1))

STAGE_W = tok('stage-w'); STAGE_H = tok('stage-h')
P, F = 0, 0
def chk(cond, desc, got=''):
    global P, F
    if cond: P += 1; print(f'  [PASS] {desc} {got}')
    else:    F += 1; print(f'  [FAIL] {desc} {got}')

print('=' * 74)
print('几何回归 · SPLIT 两框间距（修复"A/B 叠在一起"）')
print('=' * 74)

aL = tok('split-a-left'); aT = tok('split-a-top')
aW = tok('split-a-width'); aB = tok('split-a-bottom')
G  = tok('split-gutter')
bL = tok('split-b-left'); bT = tok('split-b-top')
bW = tok('split-b-width'); bR = tok('split-b-right'); bB = tok('split-b-bottom')

print('\n-- 令牌存在性 --')
for n, v in [('split-a-left',aL),('split-a-top',aT),('split-a-width',aW),
             ('split-a-bottom',aB),('split-gutter',G),('split-b-left',bL),
             ('split-b-top',bT),('split-b-width',bW),('split-b-right',bR),
             ('split-b-bottom',bB)]:
    chk(v is not None, f'--{n} 已定义', f'= {v}')
if None in (aL,aT,aW,aB,G,bL,bT,bW,bR,bB):
    print('\n令牌缺失，中止'); raise SystemExit(1)

print('\n-- 核心：两框水平不叠压 --')
aRight = aL + aW                      # A 框右外沿 x
gap    = bL - aRight                  # 实际间距
chk(gap > 0,        'A/B 不叠压（间距 > 0）',      f'A右沿={aRight:.0f} B左沿={bL:.0f} 间距={gap:.0f}px')
chk(gap == G,       f'实际间距 == --split-gutter', f'{gap:.0f} vs {G:.0f}')
chk(abs(G - 26*1.5) <= 1, '中缝 == 实测 26px×1.5', f'{G:.0f}px vs 39px')
chk(gap >= 24,      '间距肉眼可辨（≥24px）',        f'{gap:.0f}px')

print('\n-- A 框右阴影不得越过中缝 --')
m = re.search(r'--shadow-frame-a:(.*?);', css, re.S)
rshadow = None
for ln in [x.strip().rstrip(',') for x in m.group(1).strip().split('\n') if x.strip()]:
    p = ln.split()
    if len(p) >= 2 and not p[0].startswith('-') and p[1] == '0':
        rshadow = float(p[0].rstrip('px'))
chk(rshadow is not None, 'A 框右阴影偏移已定义', f'= {rshadow}px')
if rshadow is not None:
    chk(rshadow <= G, '右阴影 ≤ 中缝（不糊到 B 框）', f'{rshadow:.0f}px ≤ {G:.0f}px')

print('\n-- 右侧不贴边 --')
bRight = bL + bW
chk(abs((STAGE_W - bRight) - bR) <= 1, 'B 框右留白与令牌一致',
    f'算得 {STAGE_W-bRight:.0f}px, 令牌 {bR:.0f}px')
chk(bR > 0, 'B 框不贴右边', f'留白 {bR:.0f}px')
chk(aL > 0, 'A 框不贴左边', f'留白 {aL:.0f}px')

print('\n-- 总宽守恒 --')
total = aL + aW + G + bW + bR
chk(abs(total - STAGE_W) <= 2, 'aL+aW+gutter+bW+bR == 画面宽',
    f'{total:.0f} vs {STAGE_W:.0f}')

print('\n-- A/B 顶底错位（实测 12px，非对齐） --')
chk(abs((bT - aT) - 12) <= 1, 'B 框顶部比 A 低 12px', f'{bT-aT:.0f}px')
chk(abs((bB - aB) - 12) <= 1, 'B 框底部比 A 高 12px', f'{bB-aB:.0f}px')

print('\n-- box-sizing 防外撑 --')
for cls in ('frame-a', 'frame-b'):
    m2 = re.search(rf'\.{cls}\s*\{{(.*?)\}}', css, re.S)
    chk(m2 and 'box-sizing: border-box' in m2.group(1),
        f'.{cls} 设了 box-sizing:border-box', '(否则边框外撑吃掉中缝)')

print('\n-- 禁止百分比宽度回归 --')
chk('--frame-a-width-ratio' not in css, '已移除 --frame-a-width-ratio')
chk('--frame-b-width-ratio' not in css, '已移除 --frame-b-width-ratio')
m3 = re.search(r'\.layout-split\s+\.frame-a\s*\{(.*?)\}', css, re.S)
chk(m3 and 'left: 0;' not in m3.group(1), 'SPLIT 的 A 框不再 left:0 贴边')

print('\n-- FULL 布局左右对称 --')
fl = tok('full-b-left'); fr = tok('full-b-right')
chk(fl == fr, 'FULL 左右留白对称', f'{fl:.0f} / {fr:.0f}')

print('\n' + '=' * 74)
print(f'几何回归结果：通过 {P} / 失败 {F}')
print('=' * 74)
print('\n两框间距成立，不再叠压。' if F == 0 else f'\n仍有 {F} 项不合格，需修。')
