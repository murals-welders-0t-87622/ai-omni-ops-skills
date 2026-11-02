# -*- coding: utf-8 -*-
"""
数字人居中·像素级终检
不相信数学推导，直接对渲染后的截图做肤色检测，测量人物中心
在 A 框内的真实水平位置，判定是否落在正中（容差 ±3%）。
"""
import io, sys, os, json, subprocess
sys.stdout = io.TextIOWrapper(open('_pv_center.log', 'wb'), encoding='utf-8', write_through=True)
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = [
    ('p1', 'p1-s02-three-voices.html'),
    ('p3', 'p3-s19-socket.html'),
    ('p4', 'p4-s42-auto-route.html'),
    ('p5', 'p5-s01-opening.html'),
]
GEO_JS = """() => {
  const st = document.querySelector('.stage');
  const a  = st.querySelector('.frame-a');
  const img= a.querySelector('img');
  const r  = st.getBoundingClientRect();
  const k  = r.width / 1920;
  const ar = a.getBoundingClientRect();
  const ir = img.getBoundingClientRect();
  return { k: k, stageL: r.left, stageT: r.top,
           aL:(ar.left-r.left)/k, aT:(ar.top-r.top)/k, aW:ar.width/k, aH:ar.height/k,
           iL:(ir.left-r.left)/k, iT:(ir.top-r.top)/k, iW:ir.width/k, iH:ir.height/k,
           objPos: getComputedStyle(img).objectPosition };
}"""

def skin_mask(a):
    a = a.astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx = np.maximum(np.maximum(R, G), B); mn = np.minimum(np.minimum(R, G), B)
    m = ((R > 95) & (G > 40) & (B > 20) & ((mx - mn) > 15) &
         (np.abs(R - G) > 15) & (R > G) & (R > B))
    if m.sum() < (a.shape[0] * a.shape[1] * 0.004):
        m = ((R > 70) & (G > 30) & (B > 15) & ((mx - mn) > 8) & ((R - G) > 6) & (R > B))
    return m

def col_center(mask, min_frac=0.004):
    h, w = mask.shape
    col = mask.sum(axis=0).astype(np.float32)
    keep = col > max(2.0, h * min_frac)
    idx = np.nonzero(keep)[0]
    if idx.size == 0: return None
    cw = col.copy(); cw[~keep] = 0.0
    return float((cw * np.arange(w)).sum() / cw.sum()) / w

fails, rows = [], []
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={'width': 1600, 'height': 950}, device_scale_factor=2)
    for tag, fn in PAGES:
        pg.goto('file:///' + os.path.join(HERE, fn).replace('\\', '/'))
        pg.wait_for_timeout(600)
        g = pg.evaluate(GEO_JS)
        shot = os.path.join(HERE, '_ctr_%s.png' % tag)
        pg.screenshot(path=shot)
        im = Image.open(shot).convert('RGB')
        # 截图像素 = CSS 像素 * dsf；把 A 框内容区换算到截图坐标
        dsf = im.width / 1600.0
        k = g['k']
        x0 = int((g['stageL'] + g['iL'] * k) * dsf); x1 = int(x0 + g['iW'] * k * dsf)
        y0 = int((g['stageT'] + g['iT'] * k) * dsf); y1 = int(y0 + g['iH'] * k * dsf)
        crop = np.asarray(im.crop((x0, y0, x1, y1)))
        m = skin_mask(crop)
        # 只看上 55% 的头肩带
        cx = col_center(m[0:int(m.shape[0] * 0.55), :])
        print('[%s] %s' % (tag, fn))
        print('   A框 %.0fx%.0f  内容区 %.0fx%.0f  object-position=%s'
              % (g['aW'], g['aH'], g['iW'], g['iH'], g['objPos']))
        print('   裁出区域 %dx%d  肤色占比 %.2f%%' % (crop.shape[1], crop.shape[0], m.mean() * 100))
        if cx is None:
            print('   ✗ 未检出肤色'); fails.append(tag); continue
        dev = (cx - 0.5) * 100
        ok = abs(dev) <= 3.0
        print('   人物头肩中心在框内 %.3f   偏离正中 %+.1f%%   %s'
              % (cx, dev, 'OK ✓' if ok else '✗ 超差'))
        rows.append(dict(tag=tag, cx=cx, dev=dev, ok=ok, objPos=g['objPos'], aW=g['aW']))
        if not ok: fails.append(tag)
        print()
    br.close()

print('=' * 52)
print('容差 ±3.0%%   通过 %d/%d' % (len(rows) - len(fails), len(rows)))
if fails: print('未通过: %s' % ', '.join(fails))
else:     print('全部页面数字人已水平居中 ✓')
json.dump(rows, open('_pv_center.json', 'w'), ensure_ascii=False, indent=2)
