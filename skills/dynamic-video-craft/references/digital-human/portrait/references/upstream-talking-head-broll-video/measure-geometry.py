# -*- coding: utf-8 -*-
"""SPLIT 布局完整几何：A框 / 中缝 / B框 的四边精确坐标（原生 1280x720）"""
import io, sys, subprocess, numpy as np
sys.stdout = io.TextIOWrapper(open('_geom.log', 'wb'), encoding='utf-8', write_through=True)

SRC = '下载.mp4'
W, H = 1280, 720
BG = 209  # 实测背景基准

def frame(t):
    p = subprocess.run(
        ['ffmpeg', '-v', 'error', '-ss', str(t), '-i', SRC, '-frames:v', '1',
         '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True)
    if len(p.stdout) < W*H*3: return None
    return np.frombuffer(p.stdout[:W*H*3], np.uint8).reshape(H, W, 3)

def dump(vals, x0, tag):
    print(f'      {tag} x={x0}..{x0+len(vals)-1}:')
    for i in range(0, len(vals), 30):
        chunk = vals[i:i+30]
        print(f'        [{x0+i:4d}] ' + ' '.join(f'{int(v):3d}' for v in chunk))

# 用 t=62s（干净 SPLIT，A白边右缘=407）做主基准
print('='*78); print('SPLIT 完整几何（基准 t=62s，横向剖面 y=300）'); print('='*78)
img = frame(62); g = img.mean(axis=2)

row = g[300]
print('\n[A] 左端：找 A框白边左缘')
dump(row[0:40], 0, 'row300')

print('\n[B] 中缝区：A白边右缘 → B黑线')
dump(row[395:445], 395, 'row300')

print('\n[C] 右端：B黑线右缘 → 画面边')
dump(row[1235:1280], 1235, 'row300')

# 竖向：A框 上/下
print('\n' + '='*78); print('竖向剖面'); print('='*78)
colA = g[:, 200]
print('\n[D] A框 顶部 y=25..45')
dump(colA[25:46], 25, 'col200')
print('\n[E] A框 底部 y=580..660')
dump(colA[580:661], 580, 'col200')

colB = g[:, 800]
print('\n[F] B框 顶部 y=30..50')
dump(colB[30:51], 30, 'col800')
print('\n[G] B框 底部 y=580..660')
dump(colB[580:661], 580, 'col800')

# 多帧交叉验证中缝
print('\n' + '='*78); print('多帧交叉验证：中缝宽度'); print('='*78)
res = []
for t in (14, 16, 17, 32, 62, 90, 104, 120, 205, 240):
    im = frame(t)
    if im is None: continue
    gg = im.mean(axis=2); r = gg[300]
    # A白边右缘：x<420 内最后一个 >=240
    seg = r[380:420]; w = np.where(seg >= 240)[0]
    aR = 380 + w.max() if len(w) else None
    # B黑线：x 420..445 内最小值位置
    seg2 = r[420:450]; bL = 420 + int(np.argmin(seg2)); bv = int(seg2.min())
    if aR and bv < 40:
        gap = bL - aR - 1
        res.append(gap)
        print(f'  t={t:3d}s  A白边右缘={aR}  B黑线={bL}(值{bv})  中缝={gap}px')
    else:
        print(f'  t={t:3d}s  非标准 SPLIT (aR={aR} bv={bv})')
if res:
    print(f'\n  中缝统计: 众数={max(set(res), key=res.count)}px  取值={sorted(set(res))}')
print('\n完成')
