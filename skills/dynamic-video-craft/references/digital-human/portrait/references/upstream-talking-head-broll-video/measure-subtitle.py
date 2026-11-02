# -*- coding: utf-8 -*-
"""字幕精确测量 · 严格版
上一轮 K 段被卡片污染 (y0 卡在窗口下界 615, 中心x=424≠640)。
本轮策略:
  1) 只在水平中段 x=[330,950] 取样 (字幕一定居中, 卡片多在左/右侧)
  2) 从 y=700 向上逐行扫, 遇到"连续空行"即认定字幕块结束 -> 得到真实 y0
  3) 用"白+暗描边"双条件确认是字幕而非卡片底色
  4) 统计字幕块高、字符高(用列投影的连续段高度)、距底、中心x
"""
import subprocess, os, sys, io, json
sys.stdout = io.TextIOWrapper(open('_sub.log', 'wb'), encoding='utf-8', write_through=True)
import numpy as np

REF = "下载.mp4"
W, H = 1280, 720
X0, X1 = 330, 950          # 中段取样窗
BG = np.array([231, 213, 183], dtype=np.float32)


def grab(t):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(t), "-i", REF, "-frames:v", "1",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    n = W * H * 3
    if len(p.stdout) < n:
        return None
    return np.frombuffer(p.stdout[:n], dtype=np.uint8).reshape(H, W, 3).astype(np.int16)


recs = []
for t in range(4, 306, 2):
    im = grab(t)
    if im is None:
        continue
    band = im[600:719, X0:X1, :]      # 只看底部 + 中段
    g = band.mean(axis=2)
    white = g > 232                   # 字幕填充: 近白
    dark = g < 105                    # 字幕描边: 近黑
    wrow = white.sum(axis=1)
    drow = dark.sum(axis=1)
    # 字幕行判定: 同一行既有足量白 又有描边暗像素
    is_sub = (wrow > 6) & (drow > 4)
    ys = np.where(is_sub)[0]
    if len(ys) < 4:
        continue
    # 取最靠下的连续块 (真字幕一定贴底)
    blocks = []
    st = ys[0]
    prev = ys[0]
    for y in ys[1:]:
        if y - prev <= 2:             # 容忍 2px 断裂(字内空隙)
            prev = y
        else:
            blocks.append((st, prev))
            st = y
            prev = y
    blocks.append((st, prev))
    b = blocks[-1]                    # 最下面那块
    if b[1] - b[0] + 1 < 8:
        continue
    y0, y1 = b[0] + 600, b[1] + 600
    # 该块内的水平范围 (回到全宽找, 确认居中)
    sub = im[y0:y1 + 1, :, :].mean(axis=2)
    wcol = (sub > 232).sum(axis=0)
    cols = np.where(wcol > 0)[0]
    if len(cols) < 20:
        continue
    x0, x1 = int(cols.min()), int(cols.max())
    recs.append((t, y0, y1, y1 - y0 + 1, x0, x1, x1 - x0 + 1, (x0 + x1) // 2, 719 - y1))

print("=" * 88)
print("字幕严格测量 (x取样窗 %d..%d, 白>232 且 描边<105)" % (X0, X1))
print("=" * 88)
print("有效帧 %d 个, 列出前 30:" % len(recs))
for r in recs[:30]:
    print("   t=%3ds  y=%3d..%3d  块高=%2dpx  x=%4d..%4d w=%4d  中心x=%4d  距底=%dpx" % r)

if recs:
    a = np.array([[r[1], r[2], r[3], r[7], r[8], r[6]] for r in recs], dtype=np.float32)
    print()
    print("统计 (n=%d):" % len(a))
    for i, nm in enumerate(["顶 y0", "底 y1", "块高 h", "中心 x", "距底", "块宽 w"]):
        col = a[:, i]
        print("   %-7s 中位=%6.1f  p10=%6.1f  p90=%6.1f  min=%4.0f  max=%4.0f"
              % (nm, np.median(col), np.percentile(col, 10), np.percentile(col, 90),
                 col.min(), col.max()))
    h = float(np.median(a[:, 2]))
    print()
    print(">> 1280x720 原生: 字幕块高 %.0fpx, 底边 y=%.0f, 距底 %.0fpx, 中心x=%.0f (画面中心 640)"
          % (h, np.median(a[:, 1]), np.median(a[:, 4]), np.median(a[:, 3])))
    print(">> 换算 1920x1080 (x1.5): 块高 %.0fpx, 底边 y=%.0f, 距底 %.0fpx"
          % (h * 1.5, np.median(a[:, 1]) * 1.5, np.median(a[:, 4]) * 1.5))
    print()
    # 中文字幕: 块高 ≈ 字号 (方块字满高), 通常字号 = 块高 * 0.92~1.0
    print(">> 推断 font-size: 原生约 %.0f~%.0fpx  ->  1920 等效约 %.0f~%.0fpx"
          % (h * 0.92, h * 1.0, h * 0.92 * 1.5, h * 1.5))
    with open("_ref_measure/subtitle_metrics.json", "w", encoding="utf-8") as f:
        json.dump({"native": {"h": h, "y1": float(np.median(a[:, 1])),
                              "bottom_gap": float(np.median(a[:, 4])),
                              "center_x": float(np.median(a[:, 3]))},
                   "scaled_1920": {"h": h * 1.5,
                                   "bottom_gap": float(np.median(a[:, 4])) * 1.5},
                   "n_frames": len(recs)}, f, ensure_ascii=False, indent=1)
    print("-> _ref_measure/subtitle_metrics.json")
