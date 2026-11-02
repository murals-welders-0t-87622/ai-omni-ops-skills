# -*- coding: utf-8 -*-
"""
60 个合成页机械校验：几何断言 + 数字人居中复验 + 截图
★ 陷阱：合成页不缩放（body 就是 1920×1080），无需 ÷k
"""
import io, sys, os, glob, json, asyncio

sys.stdout = io.TextIOWrapper(open('_comp_check.log', 'wb'), encoding='utf-8', write_through=True)

from playwright.async_api import async_playwright

PAGES = sorted(glob.glob('compositions/scene-*.html'))
SHOT = '_comp_shots'
os.makedirs(SHOT, exist_ok=True)

# 期望几何（design-tokens.css 实测值）
EXP = dict(a_left=24, a_top=46, a_width=588, gutter=39,
           b_left=651, b_width=1218, b_top=58)

JS = """() => {
  const st = document.querySelector('.stage');
  const a = document.querySelector('.frame-a');
  const b = document.querySelector('.frame-b');
  const im = document.querySelector('.frame-a > video, .frame-a > img');
  const r = e => { const q = e.getBoundingClientRect();
    return {l:q.left, t:q.top, w:q.width, h:q.height, r:q.right, bo:q.bottom}; };
  const sub = document.querySelector('.subtitle');
  return {
    lay: st.className.replace('stage','').trim(),
    sid: st.dataset.sid, dur: st.dataset.dur,
    seg: st.dataset.seg || null,
    dh: st.dataset.dh || null,
    dhoff: st.dataset.dhOff || null,
    stage: r(st), a: a ? r(a) : null, b: r(b),
    objpos: im ? getComputedStyle(im).objectPosition : null,
    objfit: im ? getComputedStyle(im).objectFit : null,
    abox: a ? getComputedStyle(a).boxSizing : null,
    nb: document.querySelectorAll('.frame-b *').length,
    subsize: sub ? getComputedStyle(sub).fontSize : null,
    ncues: sub ? (JSON.parse(sub.dataset.cues || '[]')).length : 0
  };
}"""

async def main():
    fails, rows = [], []
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={'width': 1920, 'height': 1080})
        for i, f in enumerate(PAGES):
            await pg.goto('file:///' + os.path.abspath(f).replace('\\', '/'))
            await pg.wait_for_timeout(1600)   # 等动效进入稳定态
            d = await pg.evaluate(JS)
            sid = d['sid']
            lay = d['lay'].replace('layout-', '')

            def bad(msg):
                fails.append('%s [%s] %s' % (sid, lay, msg))

            # 通用断言
            if d['stage']['w'] != 1920 or d['stage']['h'] != 1080:
                bad('舞台非 1920x1080: %.0fx%.0f' % (d['stage']['w'], d['stage']['h']))
            if d['nb'] == 0:
                bad('B 框为空 —— 违反"画面不允许空一大片"')
            if d['ncues'] == 0:
                bad('无字幕 cue')
            if d['subsize'] != '38px':
                bad('字幕字号=%s 应为 38px(tokens)' % d['subsize'])

            # ---- 纯 B-roll 版式（P2/P4，无数字人素材）----
            if lay.startswith('solo-'):
                if d['a'] is not None:
                    bad('纯 B-roll 页不应存在 frame-a')
                if d['dh'] is not None:
                    bad('纯 B-roll 页不应绑定数字人 %s' % d['dh'])
                # B 框必须在画布内且足够大，否则就是"空一大片"
                bb = d['b']
                if bb['l'] < -1 or bb['t'] < -1 or bb['r'] > 1921 or bb['bo'] > 1081:
                    bad('B 框出界 (%.0f,%.0f,%.0f,%.0f)' % (bb['l'], bb['t'], bb['r'], bb['bo']))
                area = bb['w'] * bb['h'] / (1920.0 * 1080.0)
                if area < 0.24:
                    bad('B 框仅占画面 %.0f%%，过小' % (area * 100))
                rows.append('%s %-11s B(%.0f,%.0f,%.0fx%.0f) 占比%.0f%% cues=%d'
                            % (sid, lay, bb['l'], bb['t'], bb['w'], bb['h'], area * 100, d['ncues']))
                if i % 6 == 0:
                    await pg.screenshot(path=os.path.join(SHOT, '%s.png' % sid))
                continue

            # ---- 以下为有数字人的布局 ----
            if d['a'] is None:
                bad('布局 %s 缺 frame-a' % lay)
                continue
            if d['dh'] is None:
                bad('有 frame-a 但未绑定 data-dh（唇形无法对齐音频段）')
            if d['abox'] != 'border-box':
                bad('frame-a 非 border-box')
            if d['objfit'] != 'cover':
                bad('object-fit 非 cover: %s' % d['objfit'])

            # 锚点按布局分别断言（铁律 10）
            op = (d['objpos'] or '').split()[0] if d['objpos'] else ''
            want = '90%' if lay == 'hero' else '68%'
            if op != want:
                bad('锚点错: %s 应为 %s' % (op, want))

            # SPLIT 专项：绝对几何 + 中缝
            if lay == 'split':
                g = d['b']['l'] - d['a']['r']
                if abs(d['a']['l'] - EXP['a_left']) > 1: bad('A.left=%.1f' % d['a']['l'])
                if abs(d['a']['t'] - EXP['a_top']) > 1:  bad('A.top=%.1f' % d['a']['t'])
                if abs(d['a']['w'] - EXP['a_width']) > 1: bad('A.w=%.1f' % d['a']['w'])
                if abs(d['b']['l'] - EXP['b_left']) > 1: bad('B.left=%.1f' % d['b']['l'])
                if abs(d['b']['w'] - EXP['b_width']) > 1: bad('B.w=%.1f' % d['b']['w'])
                if abs(g - EXP['gutter']) > 1: bad('中缝=%.1f 应为 39' % g)
                rows.append('%s split  A(%.0f,%.0f,%.0f)  gutter=%.1f' % (sid, d['a']['l'], d['a']['t'], d['a']['w'], g))
            elif lay == 'hero':
                # 水平居中断言
                lft, rgt = d['a']['l'], 1920 - d['a']['r']
                if abs(lft - rgt) > 1.5: bad('HERO 未水平居中 %.1f vs %.1f' % (lft, rgt))
                # 竖向中缝
                vg = d['a']['t'] - d['b']['bo']
                if abs(vg - 39) > 2: bad('HERO 竖向中缝=%.1f 应为 39' % vg)
                if abs(d['a']['w'] - 353) > 1: bad('HERO A.w=%.1f 应为 353' % d['a']['w'])
                rows.append('%s hero   居中 %.1f/%.1f  竖缝=%.1f  A.w=%.0f' % (sid, lft, rgt, vg, d['a']['w']))
            else:
                # FULL / CENTER：A/B 不得重叠
                ov_x = min(d['a']['r'], d['b']['r']) - max(d['a']['l'], d['b']['l'])
                ov_y = min(d['a']['bo'], d['b']['bo']) - max(d['a']['t'], d['b']['t'])
                if lay == 'center' and ov_x > 0 and ov_y > 0:
                    bad('CENTER A/B 重叠 %.0fx%.0f' % (ov_x, ov_y))
                rows.append('%s %-6s A(%.0f,%.0f,%.0fx%.0f)' % (sid, lay, d['a']['l'], d['a']['t'], d['a']['w'], d['a']['h']))

            # 抽样截图（每 6 镜一张，避免产出爆炸）
            if i % 6 == 0:
                await pg.screenshot(path=os.path.join(SHOT, '%s.png' % sid))
        await br.close()

    print('=== 逐镜几何 ===')
    for r in rows: print('  ' + r)
    print('\n=== 结果 ===')
    print('检查页数: %d' % len(PAGES))
    print('失败项: %d' % len(fails))
    for f in fails: print('  FAIL ' + f)
    print('\n%s' % ('全部通过' if not fails else '存在失败项，必须归零'))
    json.dump(dict(pages=len(PAGES), fails=fails), open('_comp_check.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

asyncio.run(main())
