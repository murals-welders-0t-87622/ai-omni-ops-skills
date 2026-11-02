# -*- coding: utf-8 -*-
"""SRT -> Scene 拆镜（touge 方法 7 步）
规则:
  - Tutorial 节奏: 目标 2-6s/镜, 中位约 3.2s
  - 在语义标记处强制断开: 注意/但是/所以/因为/其实/问题是/关键是/第一/第二/第三/你想想/你猜
  - 数据点、对比、新概念、列表开始 -> 断
  - 输出: 镜号 | 起 | 止 | 时长 | cue范围 | 合并后的旁白
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(open('_scenes.txt', 'wb'), encoding='utf-8', write_through=True)

raw = open('SCRIPT.srt', encoding='utf-8-sig').read().replace('\r\n', '\n')


def sec(t):
    h, m, rest = t.split(':')
    s, ms = rest.split(',')
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


cues = []
for b in [x for x in raw.split('\n\n') if x.strip()]:
    L = [x for x in b.split('\n') if x.strip()]
    tm = [x for x in L if '-->' in x]
    if not tm:
        continue
    i = L.index(tm[0])
    a, bb = tm[0].split('-->')
    cues.append({'n': len(cues) + 1, 'st': sec(a.strip()), 'ed': sec(bb.strip()),
                 'tx': ' '.join(L[i + 1:]).strip()})

# 强制断点：这些词出现在 cue 开头 -> 该 cue 必须作为新 Scene 起点
HARD = ('注意', '但是', '所以', '因为', '其实', '问题是', '关键是',
        '第一', '第二', '第三', '你想想', '你猜怎么着', '为什么是现在',
        '我算过', '我见过', '重点在路由', '给老板', '拾光判断',
        '真正受益的', '今天有条消息', '先用大白话', '这才是', '这才像')
# 章节级断点（更强，用于 crossfade）
SECT = ('今天有条消息', '先用大白话', '我见过', '我常跟你说', '重点在路由',
        '国家数据局', 'OpenRouter', '为什么是现在', '词元', '给老板', '拾光判断')

TARGET, MAX_D = 3.9, 6.6
scenes = []
cur = []
for c in cues:
    starts_hard = any(c['tx'].startswith(w) for w in HARD)
    if cur and starts_hard:
        scenes.append(cur); cur = [c]; continue
    if cur:
        dur = c['ed'] - cur[0]['st']
        if dur > MAX_D or (dur >= TARGET and len(cur) >= 3):
            scenes.append(cur); cur = [c]; continue
    cur.append(c)
if cur:
    scenes.append(cur)

# 合并过短镜头(<2.2s)到相邻
merged = []
for s in scenes:
    d = s[-1]['ed'] - s[0]['st']
    if merged and d < 2.2:
        prev_d = merged[-1][-1]['ed'] - merged[-1][0]['st']
        if prev_d + d <= MAX_D:
            merged[-1].extend(s); continue
    merged.append(s)
scenes = merged

print('Scene 数 = %d   总时长 = %.2fs' % (len(scenes), cues[-1]['ed']))
ds = [s[-1]['ed'] - s[0]['st'] for s in scenes]
ds_sorted = sorted(ds)
print('镜长: 中位=%.2fs 平均=%.2fs 最短=%.2fs 最长=%.2fs'
      % (ds_sorted[len(ds) // 2], sum(ds) / len(ds), min(ds), max(ds)))
print('覆盖 cue 数 = %d / %d' % (sum(len(s) for s in scenes), len(cues)))
print('2-6s 区间占比 = %.0f%%' % (100 * sum(1 for d in ds if 2 <= d <= 6) / len(ds)))
print()
out = []
for i, s in enumerate(scenes, 1):
    st, ed = s[0]['st'], s[-1]['ed']
    txt = ''.join(x['tx'] for x in s)
    is_sect = any(s[0]['tx'].startswith(w) for w in SECT)
    out.append({'id': i, 'start': round(st, 3), 'end': round(ed, 3),
                'dur': round(ed - st, 2),
                'cues': [s[0]['n'], s[-1]['n']], 'text': txt, 'section': is_sect})
    print('S%02d | %7.3f-%7.3f | %4.2fs | cue %3d-%3d |%s %s'
          % (i, st, ed, ed - st, s[0]['n'], s[-1]['n'],
             ' ★' if is_sect else '  ', txt))

json.dump(out, open('_scenes.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n-> _scenes.json')
