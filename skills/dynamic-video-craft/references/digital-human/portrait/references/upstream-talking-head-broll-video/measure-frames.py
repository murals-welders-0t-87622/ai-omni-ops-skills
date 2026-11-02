# -*- coding: utf-8 -*-
"""参考视频像素级测量 第三轮
1) 右侧 B-roll 框精确边框结构
2) 阴影方向性与衰减曲线 (四边分别测)
3) 字幕精确字号 (限定 y 620-710 避开卡片污染)
4) 布局切换节奏 (1s 采样, 求切换点与镜头时长分布)
"""
import subprocess, os, json, sys, io
sys.stdout = io.TextIOWrapper(open('_m3.log', 'wb'), encoding='utf-8', write_through=True)
import numpy as np

REF = "下载.mp4"
W, H = 1280, 720
OUT = "_ref_measure"
os.makedirs(OUT, exist_ok=True)


def grab_rgb(t):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", REF, "-frames:v", "1",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    n = W * H * 3
    if len(p.stdout) < n:
        return None
    return np.frombuffer(p.stdout[:n], dtype=np.uint8).reshape(H, W, 3).astype(np.int16)


def hexof(rgb):
    return "#%02X%02X%02X" % (int(round(rgb[0])), int(round(rgb[1])), int(round(rgb[2])))


BG = np.array([231, 213, 183], dtype=np.float32)   # 实测 #E7D5B7 (85% 采样)
BGL = float(BG.mean())                             # 209.0

print("=" * 84)
print("H. 右侧 B-roll 框 完整边界扫描 (t=45s, 从 x=425 扫到 x=1279)")
print("=" * 84)
img = grab_rgb(45)
for y in (120, 360, 600):
    row = img[y].mean(axis=1)
    # 找右框左边缘: 从 x=425 起第一个 "接近白" 的位置
    print("   y=%3d  x=425..470: %s" % (y, " ".join("%3d" % int(row[x]) for x in range(425, 471))))
print()
for y in (120, 360, 600):
    row = img[y].mean(axis=1)
    print("   y=%3d  x=1230..1279: %s" % (y, " ".join("%3d" % int(row[x]) for x in range(1230, 1280))))

print()
print("=" * 84)
print("I. 上下边缘扫描 (t=45s 左框 x=200 竖扫; 右框 x=800 竖扫)")
print("=" * 84)
for x, tag in ((200, "左框(数字人)"), (800, "右框(B-roll)")):
    col = img[:, x].mean(axis=1)
    print("   %s x=%d  y=0..40:   %s" % (tag, x, " ".join("%3d" % int(col[y]) for y in range(0, 41))))
    print("   %s x=%d  y=680..719: %s" % (tag, x, " ".join("%3d" % int(col[y]) for y in range(680, 720))))
    print()

print("=" * 84)
print("J. 阴影方向性: 四边阴影深度与宽度 (t=250s 左框四周)")
print("=" * 84)


def shadow_profile(img, pts, direction, tag, span=34):
    """从边框外侧往背景方向逐像素测 亮度相对背景的差值"""
    dx, dy = direction
    prof = []
    for i in range(span):
        vals = []
        for (px, py) in pts:
            x = px + dx * i
            y = py + dy * i
            if 0 <= x < W and 0 <= y < H:
                vals.append(img[y, x].mean())
        if vals:
            prof.append(np.mean(vals) - BGL)
    print("   %s (相对背景 %+.0f 为暗):" % (tag, 0))
    print("      " + " ".join("%+4.0f" % v for v in prof))
    # 阴影宽度 = 连续 <-4 的长度
    n = 0
    for v in prof:
        if v < -4:
            n += 1
        else:
            break
    deepest = min(prof) if prof else 0
    print("      -> 阴影宽度约 %dpx, 最深 %+.0f (相对背景)" % (n, deepest))
    return n, deepest


img2 = grab_rgb(250)
# t=250s 左框: 白边框外沿 左 x=16, 右 x=407, 上 y≈43, 下 y≈642 (先探测)
col = img2[:, 200].mean(axis=1)
ys = [y for y in range(0, H) if col[y] > BGL + 20]
top_edge = min(ys) if ys else 0
bot_edge = max(ys) if ys else H - 1
print("   探测: 左框上白边 y=%d, 下白边 y=%d (高=%d)" % (top_edge, bot_edge, bot_edge - top_edge + 1))
print()
shadow_profile(img2, [(15, y) for y in (200, 350, 500)], (-1, 0), "左边阴影 (向左外扩)")
shadow_profile(img2, [(408, y) for y in (200, 350, 500)], (1, 0), "右边阴影 (向右外扩)")
shadow_profile(img2, [(x, top_edge - 1) for x in (100, 200, 300)], (0, -1), "上边阴影 (向上外扩)")
shadow_profile(img2, [(x, bot_edge + 1) for x in (100, 200, 300)], (0, 1), "下边阴影 (向下外扩)")

print()
print("=" * 84)
print("K. 字幕精确测量 (锁定 y=615..712, 排除卡片区)")
print("=" * 84)
sub_rows = []
for t in range(4, 306, 2):
    im = grab_rgb(t)
    if im is None:
        continue
    band = im[615:712, :, :]
    g = band.mean(axis=2)
    m = g > 234
    rs = m.sum(axis=1)
    rows = np.where(rs > 8)[0]
    cs = m.sum(axis=0)
    cols = np.where(cs > 1)[0]
    if len(rows) < 3 or len(cols) < 20:
        continue
    y0, y1 = int(rows.min()) + 615, int(rows.max()) + 615
    x0, x1 = int(cols.min()), int(cols.max())
    sub_rows.append((t, y0, y1, y1 - y0 + 1, x0, x1, x1 - x0 + 1, (x0 + x1) // 2, H - 1 - y1))

print("   有效字幕帧 %d 个, 前 22 个:" % len(sub_rows))
for r in sub_rows[:22]:
    print("      t=%3ds y=%d..%d h=%2dpx  x=%4d..%4d w=%4d 中心x=%4d 距底=%dpx" % r)
if sub_rows:
    arr = np.array([[r[1], r[2], r[3], r[7], r[8]] for r in sub_rows], dtype=np.float32)
    print()
    print("   统计 (n=%d):" % len(arr))
    print("      顶 y0  : 中位=%.0f  众数区间=%.0f~%.0f" % (np.median(arr[:, 0]),
          np.percentile(arr[:, 0], 10), np.percentile(arr[:, 0], 90)))
    print("      底 y1  : 中位=%.0f  众数区间=%.0f~%.0f" % (np.median(arr[:, 1]),
          np.percentile(arr[:, 1], 10), np.percentile(arr[:, 1], 90)))
    print("      字高 h : 中位=%.0f  区间=%.0f~%.0f" % (np.median(arr[:, 2]),
          arr[:, 2].min(), arr[:, 2].max()))
    print("      中心 x : 中位=%.0f (画面中心=%d)" % (np.median(arr[:, 3]), W // 2))
    print("      距底   : 中位=%.0f" % np.median(arr[:, 4]))
    print()
    print("   >> 换算到 1920x1080 (x1.5): 字高=%.0fpx 距底=%.0fpx 顶y=%.0f" % (
        np.median(arr[:, 2]) * 1.5, np.median(arr[:, 4]) * 1.5, np.median(arr[:, 0]) * 1.5))

print()
print("=" * 84)
print("L. 布局切换节奏 (1s 采样, 求切换点与镜头时长分布)")
print("=" * 84)
tl = []
for t in range(1, 309):
    im = grab_rgb(t)
    if im is None:
        continue
    diff = np.abs(im - BG.reshape(1, 1, 3)).sum(axis=2)
    mask = diff > 42
    cols = mask.sum(axis=0)
    cnz = cols > 40
    blocks = []
    inb = False
    st = 0
    for i, v in enumerate(cnz):
        if v and not inb:
            st = i; inb = True
        elif not v and inb:
            if i - st > 45:
                blocks.append((st, i - 1))
            inb = False
    if inb and len(cnz) - st > 45:
        blocks.append((st, len(cnz) - 1))
    if not blocks:
        key = "EMPTY"
    elif len(blocks) == 1:
        wp = (blocks[0][1] - blocks[0][0] + 1) / W
        key = "FULL" if wp > 0.90 else "WIDE"
    else:
        w0 = (blocks[0][1] - blocks[0][0] + 1) / W
        key = "SPLIT" if 0.28 < w0 < 0.40 else "MULTI"
    tl.append((t, key))

# 合并连续段
segs = []
for t, k in tl:
    if segs and segs[-1][2] == k and t == segs[-1][1] + 1:
        segs[-1][1] = t
    else:
        segs.append([t, t, k])
print("   共 %d 个布局段:" % len(segs))
for a, b, k in segs:
    print("      %3ds - %3ds  (%2ds)  %s" % (a, b, b - a + 1, k))
durs = {}
for a, b, k in segs:
    durs.setdefault(k, []).append(b - a + 1)
print()
print("   各布局镜头时长:")
for k, v in durs.items():
    print("      %-6s 段数=%2d  总时长=%3ds (%.0f%%)  平均=%.1fs  中位=%.1fs  范围=%d~%ds"
          % (k, len(v), sum(v), 100 * sum(v) / len(tl), np.mean(v), np.median(v), min(v), max(v)))

with open(os.path.join(OUT, "layout_segments.json"), "w", encoding="utf-8") as f:
    json.dump([{"start": a, "end": b, "dur": b - a + 1, "layout": k} for a, b, k in segs],
              f, ensure_ascii=False, indent=1)
print()
print("   -> %s/layout_segments.json" % OUT)
