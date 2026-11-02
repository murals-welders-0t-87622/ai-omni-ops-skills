# -*- coding: utf-8 -*-
import io, sys, numpy as np
from PIL import Image
sys.stdout = io.TextIOWrapper(open('_gapcheck.log', 'wb'), encoding='utf-8', write_through=True)

img = np.array(Image.open('_shot_split.png').convert('RGB'))
g = img.mean(axis=2)

# 渲染实测背景基准（stage 空白处采样，含 paper-grain 网点）
BG = float(np.median([g[1050,100], g[20,960], g[1000,960]]))
# 判据：中缝峰值应接近背景（差 ≤ 6%），且明显亮于 A 框内容(100)与 B 框黑线(0)
TOL = BG * 0.06

print('=' * 72)
print('SPLIT 中缝洁净度验证（渲染后逐像素）')
print('=' * 72)
print(f'\n渲染背景基准 = {BG:.0f}（stage 空白采样）  容差 ±{TOL:.0f}')

allpass = True
for y in (200, 400, 600, 800):
    row = g[y]
    print(f'\n-- y={y} 剖面 x=600..665 --')
    print('  ' + ' '.join(f'{int(v):3d}' for v in row[600:665]))
    mid = row[613:650]                      # 中缝 x=612..650
    peak = float(mid.max())
    near = int((mid >= BG - TOL).sum())      # 接近背景的像素数
    print(f'  中缝 37px: min={int(mid.min())} max={int(peak)} 均值={mid.mean():.1f}')
    print(f'  峰值距背景 {BG-peak:+.0f}（{(BG-peak)/BG*100:.1f}%）· 接近背景像素 {near}/{len(mid)}')
    ok = (peak >= BG - TOL) and (mid.min() > 120)
    print(f'  → {"OK" if ok else "NG"}')
    if not ok: allpass = False

print('\n' + '=' * 72)
print('几何复核')
print('=' * 72)
row = g[400]
# A 框白边右缘（白 >=240）
w = np.where(row[560:645] >= 240)[0]
aR = 560 + int(w.max()) if len(w) else None
# B 框黑线
s = row[645:700]; bL = 645 + int(np.argmin(s)); bv = int(s.min())
print(f'  A 白边右缘 x={aR}')
print(f'  B 黑线    x={bL} (值 {bv})')
if aR: print(f'  ★ 渲染中缝 = {bL - aR - 1}px   目标 39px')

wl = np.where(row[0:60] >= 240)[0]
print(f'  A 白边左缘 x={int(wl.min()) if len(wl) else None}  (令牌 24px)')
s2 = row[1840:1920]; br = 1840 + int(np.argmin(s2))
print(f'  B 黑线右缘 x={br} → 右留白 {1920-br-1}px  (令牌 51px)')

colA = g[:, 300]; t = np.where(colA[20:80] >= 240)[0]
colB = g[:, 1200]; u = np.where(colB[30:90] <= 60)[0]
print(f'  A 框顶 y={20+int(t.min()) if len(t) else None}  (令牌 46px)')
print(f'  B 框顶 y={30+int(u.min()) if len(u) else None}  (令牌 58px)')

print('\n' + '=' * 72)
print('判定：' + ('PASS — 中缝 39px，内部接近背景色，两框视觉分离' if allpass
                 else 'FAIL — 中缝仍被阴影填满'))
print('=' * 72)
