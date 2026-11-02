# -*- coding: utf-8 -*-
"""设计令牌 vs 参考视频实测 · 数值回归比对
不依赖浏览器渲染，直接校验 tokens 里的数字是否等于实测值×1.5。
"""
import io, sys, re, json
sys.stdout = io.TextIOWrapper(open('_regress.log', 'wb'), encoding='utf-8', write_through=True)

C = open('design-tokens.css', encoding='utf-8').read()

def num(pat, default=None):
    m = re.search(pat, C)
    return float(m.group(1)) if m else default

# 实测原生值 (1280x720) -> 期望 1920 值 = 原生 × 1.5
MEAS = [
    # 名称,           tokens 正则,                     原生实测, 容差
    ('字幕字号',      r'--sub-size:\s*(\d+)px',          26,   3),
    ('字幕距底',      r'--sub-bottom-gap:\s*(\d+)px',    49,   3),
    ('字幕描边',      r'--sub-stroke:\s*(\d+)px',         2,   1),
    ('左框白边',      r'--frame-a-border:\s*(\d+)px',     6,   1),
    ('左框圆角',      r'--frame-a-radius:\s*(\d+)px',     6,   2),
    ('右框黑边',      r'--frame-b-border:\s*(\d+)px',     2,   1),
]
print('=' * 88)
print('令牌 ←→ 实测 回归比对（期望值 = 原生 × 1.5）')
print('=' * 88)
P = F = 0
for name, pat, native, tol in MEAS:
    got = num(pat)
    exp = native * 1.5
    ok = got is not None and abs(got - exp) <= tol
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-9s tokens=%-6s 期望=%-6.1f (原生%3d×1.5)  %s'
          % (name, ('%gpx' % got) if got else 'N/A', exp, native,
             '✓' if ok else '✗ 偏差 %.1f' % (abs(got - exp) if got else 999)))

# SPLIT 栏宽：改用绝对像素校验（曾用百分比导致两框叠压，已废弃比例令牌）
print()
print('SPLIT 栏宽绝对像素校验（禁用百分比后）')
for nm, pat, native, tol in [
    ('A 框宽',  r'--split-a-width:\s*(\d+)px',   392, 3),
    ('B 框宽',  r'--split-b-width:\s*(\d+)px',   812, 3),
    ('中缝',    r'--split-gutter:\s*(\d+)px',     26, 2),
]:
    got = num(pat)
    exp = native * 1.5
    ok = got is not None and abs(got - exp) <= tol
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-7s tokens=%-7s 期望=%-6.1f (原生%3d×1.5)  %s'
          % (nm, ('%gpx' % got) if got else 'N/A', exp, native, '✓' if ok else '✗'))
ok = re.search(r'--frame-a-width-ratio', C) is None
P, F = (P + 1, F) if ok else (P, F + 1)
print('  百分比令牌已彻底移除                          %s' % ('✓' if ok else '✗ 仍存在'))

# 阴影四向：必须不等 且 右/下 > 左，上=0
print()
print('阴影非对称性校验（实测 左16 右34 下32 上0）')


def parse_shadow(name):
    """逐行解析三层阴影，返回 (左, 右, 下) 偏移绝对值"""
    m = re.search(r'--%s:(.*?);' % name, C, re.S)
    if not m:
        return None
    lv = rv = bv = 0
    for ln in [x.strip().rstrip(',') for x in m.group(1).strip().split('\n') if x.strip()]:
        p = ln.split()
        if len(p) < 3:
            continue
        ox, oy = p[0], p[1]
        if ox.startswith('-') and oy == '0':            # 左：负X，Y=0
            lv = int(ox.lstrip('-').rstrip('px'))
        elif ox.rstrip('px').isdigit() and oy == '0':   # 右：正X，Y=0
            rv = int(ox.rstrip('px'))
        elif ox == '0' and oy.endswith('px'):           # 下：X=0，正Y
            bv = int(oy.rstrip('px'))
    return lv, rv, bv


# FULL 场景保留实测原值（右 51px 厚重投影）
fl, fr, fb = parse_shadow('shadow-frame-a-full') or (0, 0, 0)
# SPLIT 场景右阴影必须收窄，否则填满中缝（本项曾出错）
sl, sr, sb = parse_shadow('shadow-frame-a') or (0, 0, 0)
bl, br_, bb = parse_shadow('shadow-frame-b') or (0, 0, 0)
gut = num(r'--split-gutter:\s*(\d+)px') or 0

tests = [
    ('[FULL] 左阴影 %dpx ≈ 16×1.5=24' % fl, abs(fl - 24) <= 4),
    ('[FULL] 右阴影 %dpx ≈ 34×1.5=51' % fr, abs(fr - 51) <= 5),
    ('[FULL] 下阴影 %dpx ≈ 32×1.5=48' % fb, abs(fb - 48) <= 5),
    ('[FULL] 右 > 左（%d > %d）光源在左' % (fr, fl), fr > fl),
    ('[FULL] 下 > 左（%d > %d）光源在上' % (fb, fl), fb > fl),
    ('[SPLIT] 左阴影 %dpx ≈ 24 保持一致' % sl, abs(sl - 24) <= 4),
    ('[SPLIT] 下阴影 %dpx ≈ 48 保持一致' % sb, abs(sb - 48) <= 5),
    ('[SPLIT] A 右阴影 %d > 0（仍有立体感）' % sr, sr > 0),
    ('[SPLIT] A右+B左 %d+%d ≤ 中缝%d/2' % (sr, bl, gut), sr + bl <= gut / 2),
    ('无 "0 4px" 对称写法', '0 4px 12px' not in C),
]
for n, ok in tests:
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-40s %s' % (n, '✓' if ok else '✗'))

# 颜色
print()
print('颜色校验')
cols = [('画布 #E7D5B7', '#E7D5B7'), ('纸浅 #F4E7D6', '#F4E7D6'),
        ('纸深 #DFCDB4', '#DFCDB4')]
for n, c in cols:
    ok = c in C
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-16s %s' % (n, '✓' if ok else '✗'))
white = re.findall(r'background:\s*(#fff\b|#ffffff\b|white\b)', C, re.I)
ok = len(white) == 0
P, F = (P + 1, F) if ok else (P, F + 1)
print('  %-16s %s %s' % ('无纯白背景', '✓' if ok else '✗', white))

# 动效帧数
print()
print('动效参数（30fps）')
for n, pat, exp in [('入场', r'--d-enter:\s*(\d+)', 12), ('错开', r'--d-stagger:\s*(\d+)', 4),
                    ('图表', r'--d-chart:\s*(\d+)', 24), ('数字', r'--d-number:\s*(\d+)', 27)]:
    g = num(pat)
    ok = g == exp
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-6s %sf (%.2fs) 期望 %df  %s' % (n, g, (g or 0) / 30, exp, '✓' if ok else '✗'))

# 分镜数据
print()
print('分镜数据校验')
sc = json.load(open('_scenes.json', encoding='utf-8'))
ds = sorted(x['dur'] for x in sc)
checks = [
    ('Scene 数 %d ∈ [60,80]' % len(sc), 60 <= len(sc) <= 80),
    ('中位镜长 %.2fs ∈ [2.8,4.2]' % ds[len(ds)//2], 2.8 <= ds[len(ds)//2] <= 4.2),
    ('最短 %.2fs ≥ 2.0' % ds[0], ds[0] >= 2.0),
    ('最长 %.2fs ≤ 6.6' % ds[-1], ds[-1] <= 6.6),
    ('cue 覆盖 271', sum(x['cues'][1]-x['cues'][0]+1 for x in sc) == 271),
    ('时长 %.2f = 240.88' % sc[-1]['end'], abs(sc[-1]['end']-240.88) < 0.01),
]
for n, ok in checks:
    P, F = (P + 1, F) if ok else (P, F + 1)
    print('  %-28s %s' % (n, '✓' if ok else '✗'))

print()
print('=' * 88)
print('回归结果：通过 %d / 失败 %d' % (P, F))
print('=' * 88)
print('\n' + ('>>> 令牌与实测一致，设计系统成立。' if F == 0
              else '>>> 有 %d 项偏离实测，需修正 tokens。' % F))
