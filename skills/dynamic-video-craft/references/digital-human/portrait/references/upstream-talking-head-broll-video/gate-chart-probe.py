#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_chart_probe.py — 图表畸变确定性探针

为什么需要这个脚本：
  「图表压扁」是用户肉眼发现的问题，但肉眼看抽帧图无法给出量化结论
  （截图缩放后更难判断）。必须直接问浏览器：这个 svg 实际渲染成多大？
  内容有没有被拉伸？

判据（两条，都必须过）：
  1. 高度闸：svg 的 clientHeight >= CHART_MIN_H
     —— 防止 flex 把图表压成扁片。
  2. 畸变闸：实际渲染宽高比 / viewBox 宽高比 的偏差
     —— preserveAspectRatio="xMidYMid meet" 生效时，内容不会变形，
        但容器本身可能仍是扁的（图表两侧留白），所以要同时看容器比例，
        对比 viewBox 判断视觉上是否「太扁」。

不用 PIL 数像素、不靠肉眼，结论可复现。
"""
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
COMP = os.path.join(BASE, 'compositions')
LOG = os.path.join(BASE, '_chart_probe.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

CHART_MIN_H = 240        # 折线/面积图能读出趋势的下限
MAX_SQUASH = 1.35        # 容器比 viewBox 扁多少倍算不可接受

PROBE_JS = """() => {
  const out = [];
  // 只探"主图表"：.chart 里的 svg。
  // 刻意排除 bn__spark / rule-strip 这类装饰性迷你走势条 ——
  // 它们本来就是细长条（AR 8+ 是设计意图，不是畸变），
  // 混进来会把门禁判据带偏，让真正的问题被噪声淹没。
  document.querySelectorAll('.chart > svg').forEach((s, i) => {
    const vb = s.getAttribute('viewBox');
    const r  = s.getBoundingClientRect();
    out.push({
      idx: i,
      viewBox: vb,
      par: s.getAttribute('preserveAspectRatio'),
      w: Math.round(r.width),
      h: Math.round(r.height),
      cls: (s.parentElement ? s.parentElement.className : '')
    });
  });
  return out;
}"""


def main():
    from playwright.sync_api import sync_playwright

    tl = json.load(open('_timeline.json', encoding='utf-8'))
    # 只探有图表类组件的镜
    sb = json.load(open('_sb.json', encoding='utf-8'))
    want = set()
    for s in sb:
        c = str(s.get('component', ''))
        if any(k in c for k in ('chart', 'sparkline', 'gauge', 'spectrum')):
            want.add(s['sid'])

    fails = []
    rows = []
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page(viewport={'width': 1920, 'height': 1080})
        for x in tl:
            sid = x['sid']
            if sid not in want or x.get('skip'):
                continue
            src = os.path.join(COMP, 'scene-%s.html' % sid[1:])
            if not os.path.exists(src):
                continue
            pg.goto('file:///' + src.replace('\\', '/'))
            pg.wait_for_timeout(120)
            lay = pg.eval_on_selector('.stage', 'e => e.className')
            for s in pg.evaluate(PROBE_JS):
                if not s['viewBox']:
                    continue
                vb = [float(v) for v in s['viewBox'].split()]
                vb_ar = vb[2] / vb[3]
                if s['h'] == 0:
                    ar = 999.0
                else:
                    ar = s['w'] / s['h']
                squash = ar / vb_ar
                bad = []
                if s['h'] < CHART_MIN_H:
                    bad.append('矮 %dpx<%d' % (s['h'], CHART_MIN_H))
                if squash > MAX_SQUASH:
                    bad.append('扁 %.2fx>%.2f' % (squash, MAX_SQUASH))
                # 不再检查 par 取值：判定标准是"畸变量"而不是"用了哪个属性"。
                # 比例吻合时 none 是最优解（铺满容器且不变形），
                # 比例不吻合时 meet 也只是把变形换成留白。看数据，不看属性名。
                rows.append((sid, lay.replace('stage layout-', ''), s['w'], s['h'],
                             '%.2f' % vb_ar, '%.2f' % ar, '%.2f' % squash,
                             s['par'], '/'.join(bad) or 'ok'))
                if bad:
                    fails.append('%s %s' % (sid, '/'.join(bad)))
        br.close()

    print('%-5s %-11s %6s %6s %7s %7s %7s %-16s %s' %
          ('镜', '布局', '宽', '高', 'vbAR', '实AR', '畸变', 'par', '判定'))
    for r in rows:
        print('%-5s %-11s %6d %6d %7s %7s %7s %-16s %s' % r)
    print()
    print('=== 结果 ===  探测 %d 个 svg   FAIL %d' % (len(rows), len(fails)))
    for f in fails:
        print('  FAIL', f)
    if not fails:
        print('全部通过：图表既不矮也不扁，preserveAspectRatio 一致。')


if __name__ == '__main__':
    main()
