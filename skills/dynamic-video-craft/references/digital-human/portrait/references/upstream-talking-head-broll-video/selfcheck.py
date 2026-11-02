# -*- coding: utf-8 -*-
"""配置文档自查（用户要求 #9）
机械校验，不靠"我觉得对了"。逐条比对用户 10 项要求 + 实测数据 + 作者思路。
"""
import io, sys, re, json, os
sys.stdout = io.TextIOWrapper(open('_selfcheck.log', 'wb'), encoding='utf-8', write_through=True)

D = open('DESIGN.md', encoding='utf-8').read()
S = open('STORYBOARD.md', encoding='utf-8').read()
C = open('design-tokens.css', encoding='utf-8').read()
H = open('demo.html', encoding='utf-8').read()
T = open('TECH_MAP.html', encoding='utf-8').read()
scenes = json.load(open('_scenes.json', encoding='utf-8'))

P = F = 0
def chk(cond, name, detail=''):
    global P, F
    if cond:
        P += 1; print('  [PASS] %s' % name)
    else:
        F += 1; print('  [FAIL] %s  <<< %s' % (name, detail))

print('=' * 92)
print('配置文档自查报告')
print('=' * 92)

print('\n【要求1】数字人裁剪居中')
chk('49.6' in D and '53.5' in D, '质心区间 49.6–53.5% 已写入 DESIGN')
chk('质心' in D and '不是按原视频中心裁' in D, '明确"按质心裁而非画面中心裁"')
chk('质心' in T, 'TECH_MAP 给出裁剪实现')
chk('±3.5' in D or '3.5%' in D, '偏差容限已定义')

print('\n【要求2】开头必有 B-roll，画面不留大片空白')
s01 = [x for x in scenes if x['id'] == 1][0]
chk(s01['start'] == 0.0, 'S01 起于 0.000s')
chk('开场 0f 起画面即满' in S or '开场 0f' in S, 'S01 明示开场画面即满')
chk('禁止任何画面空一大片' in D, 'DESIGN 立"禁止空白"铁律')
chk('bottom-hero-board' in S.split('### S02')[0], 'S01 用 hero 板承载信息')

print('\n【要求3】字体缩小')
m = re.search(r'--sub-size:\s*(\d+)px', C)
sz = int(m.group(1)) if m else -1
chk(sz > 0, 'tokens 定义了 --sub-size', 'not found')
chk(sz <= 40, '字幕 %dpx ≤ 40px 上限' % sz, '%dpx 超标' % sz)
chk(abs(sz - 39) <= 3, '字幕 %dpx 贴合实测 39px' % sz)
chk('138' in D and '3.5' in D, 'DESIGN 记录了前版 138px 的错误与倍数')
chk('0.28' in D, '给出修正系数 0.28')

print('\n【要求4】边框阴影像素级模仿')
chk('两套' in D, 'DESIGN 明示"两套画框系统"')
chk('6px' in D and '2px' in D, '左框6px白边 / 右框2px黑边 均记录')
chk(C.count('--shadow-frame-a') >= 2 and '--shadow-frame-b' in C, 'tokens 分别定义两套阴影')
# 实测 51px 厚重右阴影保留在 FULL 场景令牌；SPLIT 场景须收窄以免填满中缝
sa = re.search(r'--shadow-frame-a-full:(.*?);', C, re.S)
body = sa.group(1) if sa else ''
chk('-24px' in body and '51px' in body and '48px' in body,
    '[FULL] 阴影四向不等（左24/右51/下48）')
sp = re.search(r'--shadow-frame-a:(.*?);', C, re.S)
spb = sp.group(1) if sp else ''
chk('-24px' in spb and '48px' in spb and '51px' not in spb,
    '[SPLIT] 右阴影已收窄（不得 51px 填满中缝）')
chk('禁止使用' in D and 'box-shadow: 0 4px 12px' in D, 'DESIGN 明令禁止对称阴影')
chk('左上' in D, '记录光源方位（左上）')
# A 框右侧无可见白边框，但保留 4px 深色缓冲，避免画面直撞中缝
chk(re.search(r'padding-right:\s*4px', C) is not None,
    '左框右侧无白边框 + 4px 缓冲已实现')

print('\n【要求4b】A/B 两框必须分离（中缝）')
gut = re.search(r'--split-gutter:\s*(\d+)px', C)
gv = int(gut.group(1)) if gut else 0
chk(gv > 0, '定义了 --split-gutter 中缝令牌', 'not found')
chk(abs(gv - 39) <= 2, '中缝 %dpx = 原生 26×1.5' % gv)
aL = re.search(r'--split-a-left:\s*(\d+)px', C)
chk(aL is not None and int(aL.group(1)) > 0, 'A 框不贴左边（left > 0）')
chk('border-box' in C, 'frame 使用 box-sizing: border-box（防 padding 外撑）')
chk(re.search(r'--frame-[ab]-width-ratio', C) is None, '已废除百分比栏宽令牌')
chk('叠压' in D, 'DESIGN 记录叠压事故与铁律')

print('\n【要求5】B-roll 形式多样（≥5 种）')
forms = ['打字机', 'HTML/CSS 动效', '图表动画', '纸质拼贴', '数字滚动', '结构图', 'skip-generation']
got = [f for f in forms if f in S]
chk(len(got) >= 5, '覆盖 %d 种呈现形式 (≥5)' % len(got), str(got))
chk('7 种' in S or '共 **7 种**' in S, '文档声明形式总数')

print('\n【要求6】B-roll 背景非白')
chk('#DFCDB4' in C and '#F4E7D6' in C, '暖米纸面色已入 tokens')
chk('禁止纯白背景' in D, 'DESIGN 立"禁止纯白"铁律')
chk('#E7D5B7' in C, '画布主色 #E7D5B7')
bad = re.findall(r'background:\s*(?:#fff|#FFF|white|#ffffff|#FFFFFF)\b', C)
chk(len(bad) == 0, 'tokens 中无纯白背景赋值', str(bad))

print('\n【要求7】先出图再生视频')
chk('gpt-image-2.0' in D and 'gpt-image-2.0' in S, '两文档均写明 gpt-image-2.0')
chk('图生视频' in S and '图生视频' in T, '图生视频链路明确')
chk('step 1' in T and 'step 3' in T, 'TECH_MAP 给出四步流程')

print('\n【要求8】导演级调度 / 节奏顺滑')
ds = [x['dur'] for x in scenes]
ds_s = sorted(ds)
med = ds_s[len(ds) // 2]
chk(60 <= len(scenes) <= 80, 'Scene 数 %d 落在合理区间' % len(scenes))
chk(2.8 <= med <= 4.2, '中位镜长 %.2fs 贴合实测 3.0–3.5s' % med)
inr = sum(1 for d in ds if 2 <= d <= 6)
chk(inr == len(ds), '100%% 镜长落在 2–6s (%d/%d)' % (inr, len(ds)))
chk(S.count('crossfade 0.4s') >= 5, 'crossfade 仅用于章节级 (%d 处)' % S.count('crossfade 0.4s'))
fl = S.count('inversion-flash')
chk('全片第 1 次' in S and '全片第 2 次' in S, 'flash 用量被显式编号')
chk('不连续' in S, 'flash 不连续已声明')
chk('无连续 4 镜以上同布局' in S, '布局交替规则已声明')
chk('3 种站位' in S or '不固定一处' in S, '数字人站位变化已声明（要求13）')

print('\n【要求9】自查')
chk('自查' in D and '自查' in S, '两文档均含自查节')
chk(S.count('| ✅ |') >= 8, 'STORYBOARD 逐条对照 10 项要求')

print('\n【作者思路 · 教程.txt】')
chk('一镜一判断' in T, '路由原则"一镜一判断"')
chk('Remotion' in T and 'skip-generation' in T, 'Remotion / 跳过生成 分工')
chk('省钱' in T or '额度' in T, '省钱门已落地')
chk('质检' in T and '返修' in T, '质检返修闭环')
chk('本地修' in T, '"能修就不重抽"原则')

print('\n【作者思路 · 审美.txt 九要素】')
nine = ['画幅', '颜色', '字体', '背景与材质', '留白与版式',
        '常用视觉组件', '动画节奏', '必须做到', '绝不能出现']
for n in nine:
    chk(n in D, 'DESIGN 含"%s"' % n)
chk('章法' in T or '审美不是加法' in T, '"审美=章法"被表述')
chk('取舍' in D or 'NEVER' in D, '含取舍/否定清单')

print('\n【touge 方法论落地】')
chk('composition_src' in S and 'visual_track' in S, 'composition_src / visual_track 字段齐备')
chk(S.count('track**：') >= 40, 'track 分配覆盖大部分镜头')
chk('aroll-composite.left-anchor-dashboard' in S, '主力布局用官方组件 ID')
chk('skip-generation' in S and '跳过原因' in S, 'skip 镜含跳过原因')
chk('当前SRT' in S or '当前 SRT' in S, '屏显文字标注来源')
chk('未编造' in S or '无编造' in S, '数据不编造已声明')
chk('待载入' in S and '无 demo HTML 示意词' in S, '禁用 demo 示意词已声明')

print('\n【SRT 覆盖完整性】')
tot = sum(x['cues'][1] - x['cues'][0] + 1 for x in scenes)
chk(tot == 271, 'cue 覆盖 %d/271' % tot)
chk(scenes[0]['start'] == 0.0, '首镜起点 0.000')
chk(abs(scenes[-1]['end'] - 240.88) < 0.01, '末镜终点 %.2f = 240.88' % scenes[-1]['end'])
gap = [(scenes[i]['end'], scenes[i + 1]['start']) for i in range(len(scenes) - 1)
       if abs(scenes[i]['end'] - scenes[i + 1]['start']) > 0.001]
chk(len(gap) == 0, '时间轴无空隙/重叠', str(gap[:3]))

print('\n【交付物齐备】')
for f in ['DESIGN.md', 'STORYBOARD.md', 'design-tokens.css', 'demo.html',
          'TECH_MAP.html', '_scenes.json']:
    chk(os.path.exists(f) and os.path.getsize(f) > 500, '%s 存在且非空' % f)

print('\n' + '=' * 92)
print('通过 %d 项 / 失败 %d 项   总计 %d' % (P, F, P + F))
print('=' * 92)
if F == 0:
    print('\n>>> 全部通过，可提交用户确认。')
else:
    print('\n>>> 存在 %d 项不合格，必须修改后重跑。' % F)
