# -*- coding: utf-8 -*-
"""
数字人横向锚点 —— 第三条独立证据：肤色检测
========================================================
前两条证据互相矛盾，必须引入第三条：
  v1 亮度质心   -> cx ~ 0.573 (偏右)
  v2 阈值包围盒 -> cx ~ 0.454 (偏左)   [已被差分证伪：左边界243=灯架]
  v5 帧间差分   -> cx ~ 0.615 (偏右)

肤色检测的独立性：完全不依赖亮度高低，也不依赖是否运动。
灯架/背景板/反光板都不可能通过肤色规则。
Kovac RGB 肤色判据 + 列投影 -> 头部/手部所在列。

同时输出一张「单帧原尺寸 + 三条证据竖线 + 50%参考线 + 大字标注」的
判定图，宽 1280 不缩放，保证肉眼可辨。
"""
import io, os, sys, json
import numpy as np
from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, '_dh_skin.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

BOX_W, BOX_H = 575, 872
CLIPS = ['dh_p1a', 'dh_p1b', 'dh_p3a', 'dh_p3b', 'dh_p5a', 'dh_p5b']
SUF = ['_frame_0s.jpg', '_frame_mid.jpg', '_frame_tail.jpg']


def cover_objx_from_cx(cx, src_w, src_h):
    """已知人体中心 cx（源图归一化 0~1），反解让其落在 A 框正中的 object-position X%"""
    scale = max(BOX_W / src_w, BOX_H / src_h)
    scaled_w = src_w * scale
    overflow_x = scaled_w - BOX_W
    if overflow_x <= 0:
        return 50.0
    p = (cx * scaled_w - BOX_W / 2.0) / overflow_x
    return max(0.0, min(1.0, p)) * 100.0


def skin_mask(path):
    """Kovac RGB 肤色判据"""
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, dtype=np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    m = ((R > 95) & (G > 40) & (B > 20) &
         ((mx - mn) > 15) & (np.abs(R - G) > 15) & (R > G) & (R > B))
    # 放宽版本兜底（影棚灯光可能压低饱和度）
    if m.sum() < (a.shape[0] * a.shape[1] * 0.004):
        m = ((R > 70) & (G > 30) & (B > 15) &
             ((mx - mn) > 8) & ((R - G) > 6) & (R > B))
    return m, im


def col_center(mask, min_frac=0.004):
    h, w = mask.shape
    col = mask.sum(axis=0).astype(np.float32)
    keep = col > max(2.0, h * min_frac)
    idx = np.nonzero(keep)[0]
    if idx.size == 0:
        return None
    x0, x1 = int(idx[0]), int(idx[-1])
    cw = col.copy()
    cw[~keep] = 0.0
    if cw.sum() <= 0:
        return None
    return dict(x0=x0, x1=x1,
                cx_weighted=float((cw * np.arange(w)).sum() / cw.sum()),
                cx_bbox=(x0 + x1) / 2.0, w=w, h=h)


def row_top(mask, min_frac=0.004):
    """肤色最上沿 -> 头顶位置（归一化）"""
    h, w = mask.shape
    row = mask.sum(axis=1).astype(np.float32)
    keep = row > max(2.0, w * min_frac)
    idx = np.nonzero(keep)[0]
    if idx.size == 0:
        return None
    return int(idx[0]) / h


print('=' * 64)
print('数字人横向锚点 —— 肤色检测（第三条独立证据）')
print('=' * 64)
print()

per, objs, tops = {}, [], []
for c in CLIPS:
    for s in SUF:
        p = os.path.join(BASE, c + s)
        if not os.path.exists(p):
            continue
        m, im = skin_mask(p)
        w, h = im.size
        info = col_center(m)
        if not info:
            print('[%s%s] 无肤色区域' % (c, s))
            continue
        # 上半 55% 为头肩带
        head = col_center(m[0:int(h * 0.55), :])
        cx_all = info['cx_weighted'] / w
        cx_head = (head['cx_weighted'] / w) if head else cx_all
        cxb_head = (head['cx_bbox'] / w) if head else info['cx_bbox'] / w
        ox = cover_objx_from_cx(cx_head, w, h)
        top = row_top(m)
        objs.append(ox)
        if top is not None:
            tops.append(top)
        per['%s%s' % (c, s)] = dict(cx_head=cx_head, cx_bbox_head=cxb_head,
                                    cx_all=cx_all, objx=ox, head_top=top)
        print('[%s%s] %dx%d  肤色像素 %d (%.2f%%)'
              % (c, s, w, h, int(m.sum()), 100.0 * m.sum() / (w * h)))
        print('   头肩肤色列 x: %4d..%4d  加权中心 %.4f  包围盒中点 %.4f'
              % (head['x0'] if head else -1, head['x1'] if head else -1,
                 cx_head, cxb_head))
        print('   -> objX = %.1f%%   头顶 y = %s'
              % (ox, ('%.3f' % top) if top is not None else 'n/a'))

objs_s = sorted(objs)
med = float(np.median(objs_s)) if objs_s else 50.0
print()
print('=' * 64)
print('汇总（%d 帧）' % len(objs_s))
print('  objX 各值: %s' % ', '.join('%.1f' % v for v in objs_s))
print('  中位数 %.1f%%   极差 %.1f' % (med, (objs_s[-1] - objs_s[0]) if objs_s else 0))
if tops:
    print('  头顶 y 中位数 %.3f  (范围 %.3f ~ %.3f)'
          % (float(np.median(tops)), min(tops), max(tops)))
print('=' * 64)
print()

# ---------- 清晰判定图：单帧原尺寸 + 多证据竖线 ----------
ref = os.path.join(BASE, 'dh_p1a_frame_tail.jpg')
m, im = skin_mask(ref)
w, h = im.size
base = im.copy()
ov = Image.new('RGB', (w, h), (255, 0, 255))
alpha = Image.fromarray((m * 130).astype(np.uint8), mode='L')
base = Image.composite(Image.blend(base, ov, 0.55), base, alpha)
d = ImageDraw.Draw(base)

info = col_center(m)
head = col_center(m[0:int(h * 0.55), :])
cx_skin = (head['cx_weighted'] / w) if head else info['cx_weighted'] / w

lines = [
    (0.50,     (255, 255, 255), '50% 源图正中(参考)'),
    (cx_skin,  (255, 0, 255),   '肤色头肩中心 %.3f' % cx_skin),
    (0.6153,   (0, 220, 255),   '帧间差分头肩 0.615'),
    (0.4540,   (255, 200, 0),   'v2阈值(已证伪) 0.454'),
]
for i, (cx, col, label) in enumerate(lines):
    x = int(cx * w)
    d.line([x, 0, x, h], fill=col, width=5)
    ty = 14 + i * 34
    d.rectangle([x + 8, ty, x + 8 + 9 * len(label) + 12, ty + 28], fill=(0, 0, 0))
    d.text((x + 14, ty + 7), label, fill=col)

# 10% 刻度
for k in range(1, 10):
    x = int(w * k / 10.0)
    d.line([x, h - 34, x, h], fill=(180, 180, 180), width=2)
    d.text((x + 4, h - 30), '%d0%%' % k, fill=(255, 255, 255))

out = os.path.join(BASE, '_dh_verdict.png')
base.save(out, quality=95)
print('[判定图] %s  (%dx%d)' % (out, w, h))

json.dump(dict(per_frame=per, median_objx=med, cx_skin_ref=cx_skin,
               head_top_median=(float(np.median(tops)) if tops else None)),
          open(os.path.join(BASE, '_dh_skin.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('DONE')
