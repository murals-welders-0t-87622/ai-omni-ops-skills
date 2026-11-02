# -*- coding: utf-8 -*-
"""
_rich_check.py — 富度门禁（第四层验收）

为什么需要这一层：
  几何断言(_comp_check.py) 只能证明"框没画错"；
  像素统计只能证明"有颜色在动"；
  两者都无法发现「页面内容是空的」——
  一个 <video> 铺满 B 框 + 两行小字，几何合法、颜色正确、动画在动，
  但富度只有预览页的 18%，成片观感就是"非常拉垮"。

本脚本断言 5 项，任一不过即 FAIL，禁止进入渲染：
  n_dom   B 框内 DOM 元素数        ≥ DOM_MIN
  n_anim  getAnimations() 数量     ≥ ANIM_MIN
  n_kf    页面可见 @keyframes 数   ≥ KF_MIN
  hit     分镜表点名的组件 class 是否在 DOM 中命中
  ratio   n_dom / 预览页基线中位数 ≥ RATIO_MIN

输出不只给"失败项 0"，还给全片数值分布——
中位数掉到基线一半就是系统性简化，即使每镜都"勉强达标"也要返工。
"""
import io
import json
import os
import re
import sys
import glob
import statistics

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

LOG = os.path.join(BASE, '_rich_check.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

COMP = os.path.join(BASE, 'compositions')
PREV = os.path.join(BASE, 'previews')

# ---- 门槛（依据：预览页实测 DOM 43~65、keyframes 2~9） ----
DOM_MIN = 12
ANIM_MIN = 3
KF_MIN = 2
RATIO_MIN = 0.8
# 回声页（skip 镜）门槛：它复用前镜内容，DOM 应与前镜同量级。
# 取 20 是因为最薄的组件（concentric 补层后 27）打八折仍在此之上，
# 若回声页只有 4~6 个节点，说明"复用前镜"根本没生效。
ECHO_DOM_MIN = 20

TL = json.load(open('_timeline.json', encoding='utf-8'))
SB = {s['sid']: s for s in json.load(open('_sb.json', encoding='utf-8'))}


def norm_comp(raw):
    """分镜表 component 字段 -> 组件名列表

    原始形如：`broll-hero.big-number` + `broll-charts.area-chart`
              `broll-thinking.card-grid`（3 项 + 结论条）
              `broll-thinking.compare-table` + 收束条      ← 注意这个

    ★★ 必须与 _gen_rich.py 的 comps_of() 用**完全相同**的正则白名单。
       旧实现是「按 + 切分后全部保留」，于是「收束条」「3 项」这类
       中文修饰语被当成组件名，门禁报「组件未命中: 收束条(未登记)」——
       这是判据自身的 bug，不是页面的问题。
       教训同 COMP_CLASS 命名事故：同一个字段绝不允许两个脚本各写一套解析。
    """
    if not raw:
        return []
    return re.findall(r'broll-[a-z0-9]+\.[a-z-]+', raw.replace('`', ''))


# 组件名 -> 该组件在页面上应留下的 class 痕迹（任一命中即算实现）
# 缺项说明该组件还没实现，会被 hit 断言拦下。
# 组件名 → 该组件在 DOM 里必须留下的 class 痕迹。
# 命名约定（与 compositions/_rich.css 严格对应）：
#   broll-hero.big-type      -> .c-big-type
#   broll-thinking.card-grid -> .c-card-grid
# ★ 这张表是"组件真的被渲染出来了"的唯一机械证据。
#   若改了 _rich.css 的类名而忘了同步这里，门禁会误报"组件未命中"。
COMP_CLASS = {
    'broll-hero.big-number': ['c-big-number'],
    'broll-hero.big-type': ['c-big-type'],
    'broll-hero.inversion-flash': ['c-inversion-flash'],
    'broll-thinking.card-grid': ['c-card-grid'],
    'broll-thinking.compare-table': ['c-compare-table'],
    'broll-charts.area-chart': ['c-area-chart'],
    'broll-charts.line-chart': ['c-line-chart'],
    'broll-charts.sparkline': ['c-sparkline'],
    'broll-charts.gauge': ['c-gauge'],
    'broll-abstract.analogy': ['c-analogy'],
    'broll-abstract.versus': ['c-versus'],
    'broll-abstract.equation': ['c-equation'],
    'broll-abstract.spectrum': ['c-spectrum'],
    'broll-abstract.iceberg': ['c-iceberg'],
    'broll-abstract.black-box': ['c-black-box'],
    'broll-structure.flow-chart': ['c-flow-chart'],
    'broll-structure.concentric': ['c-concentric'],
    'broll-structures2.hub-spoke': ['c-hub-spoke'],
    'broll-structures2.layered-stack': ['c-layered-stack'],
    'broll-flows.loop': ['c-loop'],
    'broll-flows.branching': ['c-branching'],
    'broll-flows.swimlane': ['c-swimlane'],
    'broll-flows.complex': ['c-complex'],
    'broll-ui.terminal': ['c-terminal'],
}

JS = r'''
() => {
  const b = document.querySelector('.frame-b');
  const st = document.querySelector('.stage');
  const anims = document.getAnimations();
  // 收集 DOM 里出现的所有 class（用于组件命中判定）
  const cls = new Set();
  document.querySelectorAll('*').forEach(e => {
    (e.className && typeof e.className === 'string' ? e.className : '')
      .split(/\s+/).forEach(c => { if (c) cls.add(c); });
  });
  return {
    n_dom: b ? b.querySelectorAll('*').length : 0,
    n_anim: anims.length,
    n_media: b ? b.querySelectorAll('video,img').length : 0,
    classes: Array.from(cls),
    lay: st ? st.className : '',
    // 回声页专用：.echo 类必须存在，否则不会静置降透明
    has_echo: !!document.querySelector('.echo'),
  };
}
'''


def count_kf(page_path):
    """统计该页可见的 @keyframes 数：页内 <style> + 它引用的 CSS 文件。"""
    html = open(page_path, encoding='utf-8').read()
    total = len(re.findall(r'@keyframes', html))
    for href in re.findall(r'<link[^>]+href="([^"]+)"', html):
        p = os.path.normpath(os.path.join(os.path.dirname(page_path), href))
        if os.path.exists(p):
            total += len(re.findall(r'@keyframes', open(p, encoding='utf-8').read()))
    return total


def preview_baseline():
    """读预览页 DOM 节点数作为基线。优先读 _preview_baseline.json，
    没有就现场统计 previews/p*.html 的 body 标签数。"""
    bj = os.path.join(BASE, '_preview_baseline.json')
    if os.path.exists(bj):
        d = json.load(open(bj, encoding='utf-8'))
        vals = [v['n_dom'] for v in d.values()]
        if vals:
            return statistics.median(vals), d
    vals = []
    for p in sorted(glob.glob(os.path.join(PREV, 'p*.html'))):
        h = open(p, encoding='utf-8').read()
        body = h.split('<body>')[-1]
        vals.append(len(re.findall(r'<(?!/)(?!!)[a-z]', body)))
    return (statistics.median(vals) if vals else 0), {}


def main():
    from playwright.sync_api import sync_playwright

    base_dom, _ = preview_baseline()
    print('=== 富度门禁 ===')
    print('门槛: DOM>=%d  anim>=%d  keyframes>=%d  ratio>=%.2f' %
          (DOM_MIN, ANIM_MIN, KF_MIN, RATIO_MIN))
    print('预览页 DOM 基线（中位数）: %.0f' % base_dom)
    print()

    todo = []
    for x in TL:
        p = os.path.join(COMP, 'scene-%s.html' % x['num'])
        if os.path.exists(p):
            todo.append((x, p))

    fails = []
    rows = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, args=[
            '--autoplay-policy=no-user-gesture-required',
            '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
        ])
        pg = br.new_page(viewport={'width': 1920, 'height': 1080},
                         device_scale_factor=1)
        for x, p in todo:
            sid = x['sid']
            is_echo = bool(SB.get(sid, {}).get('skip'))
            pg.goto('file:///' + p.replace('\\', '/'))
            pg.wait_for_timeout(180)
            # 采样点取镜头 60% 处：动画已入场、未收尾
            pg.evaluate('''(t) => {
                for (const a of document.getAnimations()) {
                    a.pause();
                    const d = a.effect.getTiming().duration;
                    const it = a.effect.getTiming().iterations;
                    let ms = t * 1000;
                    if (it === Infinity && typeof d === 'number' && d > 0) ms = ms % d;
                    a.currentTime = ms;
                }
            }''', x['dur'] * 0.6)
            d = pg.evaluate(JS)
            n_kf = count_kf(p)
            ratio = d['n_dom'] / base_dom if base_dom else 0

            bad = []
            # ★★ 回声页（skip 镜）走独立判据。
            #   这 4 镜（S03/S13/S34/S62）没有自己的 component，
            #   设计上就是复用前一镜的 B-roll 并整体静置降透明，
            #   让"人说话"占主导。用富度门槛考它们是判据用错了对象：
            #   它们的正确性标准是"内容确实复用了前镜、且确实停在动画末态"。
            if is_echo:
                if d['n_dom'] < ECHO_DOM_MIN:
                    bad.append('回声页 DOM=%d<%d（未复用前镜内容？）'
                               % (d['n_dom'], ECHO_DOM_MIN))
                if not d.get('has_echo'):
                    bad.append('回声页缺 .echo 类（不会静置降透明）')
            else:
                if d['n_dom'] < DOM_MIN:
                    bad.append('DOM=%d<%d' % (d['n_dom'], DOM_MIN))
                if d['n_anim'] < ANIM_MIN:
                    bad.append('anim=%d<%d' % (d['n_anim'], ANIM_MIN))
                if n_kf < KF_MIN:
                    bad.append('kf=%d<%d' % (n_kf, KF_MIN))
                if ratio < RATIO_MIN:
                    bad.append('ratio=%.2f<%.2f' % (ratio, RATIO_MIN))
                # 零信息版式：B 框里只有媒体 + 极少文字节点
                if d['n_media'] >= 1 and d['n_dom'] <= 6:
                    bad.append('零信息版式(仅媒体铺满)')
            # 组件命中
            comps = norm_comp(SB.get(sid, {}).get('component', ''))
            miss = []
            for c in comps:
                want = COMP_CLASS.get(c)
                if want is None:
                    miss.append('%s(未登记)' % c)
                elif not any(w in d['classes'] for w in want):
                    miss.append(c)
            if miss:
                bad.append('组件未命中: ' + ', '.join(miss))

            rows.append((sid, d['n_dom'], d['n_anim'], n_kf, ratio))
            flag = 'FAIL' if bad else 'ok  '
            print('%s %s DOM=%-3d anim=%-2d kf=%-2d ratio=%.2f %s' %
                  (flag, sid, d['n_dom'], d['n_anim'], n_kf, ratio,
                   ('  <- ' + ' / '.join(bad)) if bad else ''))
            if bad:
                fails.append((sid, bad))
        br.close()

    print()
    print('=== 数值分布（比"失败项 0"更能说明问题）===')
    for i, name in ((1, 'DOM 节点'), (2, 'animations'), (3, 'keyframes')):
        vals = [r[i] for r in rows]
        print('  %-12s 最小 %-4d 中位 %-4d 最大 %-4d 均值 %.1f' %
              (name, min(vals), int(statistics.median(vals)), max(vals),
               sum(vals) / len(vals)))
    rs = [r[4] for r in rows]
    print('  %-12s 最小 %.2f 中位 %.2f 最大 %.2f' %
          ('ratio', min(rs), statistics.median(rs), max(rs)))
    print()
    print('=== 结果 ===  检查 %d 镜   FAIL %d 镜' % (len(rows), len(fails)))
    if fails:
        print('禁止进入渲染。需返工的镜头：')
        for sid, bad in fails[:40]:
            print('  %s  %s' % (sid, ' / '.join(bad)))
    else:
        print('全部通过，可进入渲染。')


if __name__ == '__main__':
    main()
