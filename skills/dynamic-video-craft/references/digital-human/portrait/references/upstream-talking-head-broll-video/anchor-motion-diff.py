# -*- coding: utf-8 -*-
"""
数字人横向锚点 —— 帧间差分法（最终定案依据）

原理：
  每个数字人片段有 3 帧（_frame_0s / _frame_mid / _frame_tail），
  拍摄时相机固定、背景静止，只有人在说话/微动。
  => |tail - 0s| 与 |mid - 0s| 的差分区域 = 人体（尤其头肩）所在。
  这条证据完全不依赖亮度阈值，不会被影棚补光/背景亮物污染，
  也不受 v2 那种「18 帧左边界恒为 243」的固定亮物干扰。

输出：
  1) 每个片段的人体横向中心 cx（0~1 归一化）
  2) 由 cx 反解 CSS object-position 的 objX 百分比
  3) 差分掩码可视化图，便于人工复核
"""
import io
import os
import sys
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(ROOT, '_dh_diff.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)
sys.stderr = sys.stdout

import numpy as np
from PIL import Image, ImageDraw

# A 框内容区（design-tokens.css 推算）
BOX_W, BOX_H = 575, 872

CLIPS = ['dh_p1a', 'dh_p1b', 'dh_p3a', 'dh_p3b', 'dh_p5a', 'dh_p5b']
SUF = ['_frame_0s.jpg', '_frame_mid.jpg', '_frame_tail.jpg']


def cover_objx_from_cx(cx, src_w, src_h):
    """已知人体中心 cx（源图归一化），求让人体落在 A 框正中的 object-position X%"""
    scale = max(BOX_W / src_w, BOX_H / src_h)
    scaled_w = src_w * scale
    overflow_x = scaled_w - BOX_W
    if overflow_x <= 0:
        return 50.0, scale, overflow_x
    # 希望：裁剪窗中心（缩放后坐标）== cx * scaled_w
    #   窗中心 = off_x + BOX_W/2 ，off_x = overflow_x * p
    #   => p = (cx*scaled_w - BOX_W/2) / overflow_x
    p = (cx * scaled_w - BOX_W / 2.0) / overflow_x
    p = max(0.0, min(1.0, p))
    return p * 100.0, scale, overflow_x


def diff_mask(paths):
    """三帧两两差分，取并集作为运动区域掩码"""
    arrs = []
    for p in paths:
        arrs.append(np.asarray(Image.open(p).convert('L'), dtype=np.float32))
    h, w = arrs[0].shape
    d1 = np.abs(arrs[2] - arrs[0])
    d2 = np.abs(arrs[1] - arrs[0])
    d3 = np.abs(arrs[2] - arrs[1])
    d = np.maximum(np.maximum(d1, d2), d3)
    # 自适应阈值：取差分图的高分位，避免写死数值
    thr = max(6.0, float(np.percentile(d, 99.0)) * 0.30)
    m = (d > thr)
    return m, d, thr, w, h


def col_center(mask, min_frac=0.004):
    """列投影 -> 去噪 -> 加权中心 + 包围盒"""
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
    cx_w = float((cw * np.arange(w)).sum() / cw.sum())
    cx_b = (x0 + x1) / 2.0
    return dict(x0=x0, x1=x1, cx_weighted=cx_w, cx_bbox=cx_b, w=w, h=h)


print('=' * 64)
print('数字人横向锚点 —— 帧间差分法')
print('=' * 64)

results = {}
vis_tiles = []

for clip in CLIPS:
    paths = [os.path.join(ROOT, clip + s) for s in SUF]
    if not all(os.path.exists(p) for p in paths):
        print('[跳过] %s 帧不全' % clip)
        continue

    mask, d, thr, w, h = diff_mask(paths)
    info = col_center(mask)
    if info is None:
        print('[警告] %s 差分无有效运动区域' % clip)
        continue

    # 上半部（头肩）单独统计一次，人的头部位置更能代表「构图中心」
    head = col_center(mask[0:int(h * 0.55), :])

    cx_all = info['cx_weighted'] / w
    cx_head = (head['cx_weighted'] / w) if head else cx_all

    objx_all, scale, ovf = cover_objx_from_cx(cx_all, w, h)
    objx_head, _, _ = cover_objx_from_cx(cx_head, w, h)

    results[clip] = dict(
        w=w, h=h, thr=round(thr, 2),
        bbox=[info['x0'], info['x1']],
        cx_all=round(cx_all, 4),
        cx_head=round(cx_head, 4),
        objx_all=round(objx_all, 1),
        objx_head=round(objx_head, 1),
        scale=round(scale, 4), overflow_x=round(ovf, 1),
    )

    print('')
    print('[%s] %dx%d  差分阈值 %.1f' % (clip, w, h, thr))
    print('  全身运动列范围 x: %4d .. %4d   加权中心 %.4f' % (info['x0'], info['x1'], cx_all))
    if head:
        print('  头肩带运动列范围 x: %4d .. %4d  加权中心 %.4f' % (head['x0'], head['x1'], cx_head))
    print('  -> objX(全身) = %.1f%%   objX(头肩) = %.1f%%' % (objx_all, objx_head))

    # 可视化：原帧 + 差分掩码半透明红 + 中心竖线
    base = Image.open(paths[2]).convert('RGB')
    ov = Image.new('RGB', (w, h), (255, 0, 0))
    a = Image.fromarray((mask * 110).astype(np.uint8), mode='L')
    base = Image.composite(Image.blend(base, ov, 0.45), base, a)
    dd = ImageDraw.Draw(base)
    dd.line([int(cx_all * w), 0, int(cx_all * w), h], fill=(0, 255, 0), width=4)
    dd.line([int(cx_head * w), 0, int(cx_head * w), h], fill=(0, 200, 255), width=4)
    dd.rectangle([8, 8, 470, 60], fill=(0, 0, 0))
    dd.text((18, 24), '%s  cx_all=%.3f  cx_head=%.3f' % (clip, cx_all, cx_head), fill=(255, 255, 0))
    vis_tiles.append(base.resize((w // 2, h // 2)))

if vis_tiles:
    tw, th = vis_tiles[0].size
    cols = 2
    rows = (len(vis_tiles) + cols - 1) // cols
    grid = Image.new('RGB', (tw * cols, th * rows), (20, 18, 16))
    for i, t in enumerate(vis_tiles):
        grid.paste(t, ((i % cols) * tw, (i // cols) * th))
    grid.save(os.path.join(ROOT, '_dh_diff_vis.png'))
    print('')
    print('[可视化] _dh_diff_vis.png  绿线=全身中心  青线=头肩中心  红=运动区域')

# 汇总
if results:
    ha = sorted(v['objx_head'] for v in results.values())
    aa = sorted(v['objx_all'] for v in results.values())
    med_h = ha[len(ha) // 2]
    med_a = aa[len(aa) // 2]
    print('')
    print('=' * 64)
    print('汇总（%d 个片段）' % len(results))
    print('  objX(头肩) 各值: %s' % ', '.join('%.1f' % x for x in ha))
    print('  objX(全身) 各值: %s' % ', '.join('%.1f' % x for x in aa))
    print('  中位数: 头肩 %.1f%%   全身 %.1f%%' % (med_h, med_a))
    print('  极差:   头肩 %.1f    全身 %.1f' % (ha[-1] - ha[0], aa[-1] - aa[0]))
    print('=' * 64)

    with open(os.path.join(ROOT, '_dh_diff.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(per_clip=results, median_head=med_h, median_all=med_a),
                  f, ensure_ascii=False, indent=2)

print('')
print('DONE')
