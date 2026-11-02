# -*- coding: utf-8 -*-
"""
hero 布局（p5-s01-opening）A 框与 split 布局几何不同，
68% 这个锚点是针对 split 的 575x872 竖框反解的，不能照搬。
本脚本为每种 A 框几何单独反解 object-position X%，并给出可达性判断。
"""
import io, sys
sys.stdout = io.TextIOWrapper(open('_dh_hero.log', 'wb'), encoding='utf-8', write_through=True)

SRC_W, SRC_H = 1280, 704
CX = 0.6135          # 头肩中心：帧间差分 0.6153 与肤色 0.6120 的均值

def solve(name, box_w, box_h):
    scale = max(box_w / SRC_W, box_h / SRC_H)
    sw, sh = SRC_W * scale, SRC_H * scale
    ox, oy = sw - box_w, sh - box_h
    print('[%s] 内容区 %dx%d' % (name, box_w, box_h))
    print('   scale=%.4f  scaled=%.1fx%.1f  横向溢出=%.1fpx  纵向溢出=%.1fpx' % (scale, sw, sh, ox, oy))
    if ox <= 0.5:
        print('   -> 横向无溢出，object-position X 无效果，只能靠源帧预裁')
        return
    p = (CX * sw - box_w / 2.0) / ox
    print('   理论解 p=%.3f (%.1f%%)' % (p, p * 100))
    pc = max(0.0, min(1.0, p))
    # 该 p 下人物中心在框内的相对位置
    off = ox * pc
    rel = (CX * sw - off) / box_w
    # 默认 50% 时的相对位置，用于对比改善幅度
    off50 = ox * 0.5
    rel50 = (CX * sw - off50) / box_w
    print('   采用 %.0f%%  ->  人物中心落在框内 %.3f（偏离正中 %+.1fpx）' % (pc * 100, rel, (rel - 0.5) * box_w))
    print('   对比 50%%  ->  人物中心落在框内 %.3f（偏离正中 %+.1fpx）' % (rel50, (rel50 - 0.5) * box_w))
    if p > 1.0:
        print('   ⚠ 理论解越界（框太宽，横向可裁量不足），100%% 已是极限')
    print()

# split 布局：A 框 588 宽，padding 9 左 + 4 右 => 575；高 1080-46-144-18=872
solve('split  (p1/p3/p4)', 575, 872)
# hero 布局：A 框 428 宽 => 428-9-4=415；高 1080-645-156=279 => 279-18=261
solve('hero   (p5) 原 428', 415, 261)
solve('hero   (p5) 候选 380', 367, 261)
solve('hero   (p5) 候选 353', 340, 261)
print('结论：两种布局必须各用一套 object-position。')
