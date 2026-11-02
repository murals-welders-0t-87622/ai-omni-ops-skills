# -*- coding: utf-8 -*-
"""
_pv_check.py · 动态预览页渲染验证
1) 每页在 3 个时点截图（入场中 / 动效中 / 稳定态）
2) 读 DOM 几何，机械检测 frame-a 与 frame-b 是否分离
3) 顺带检查文字是否溢出 frame-b（clip 判定）
"""
import io, os, sys, glob, traceback

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_pv_check.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

try:
    from playwright.sync_api import sync_playwright
except Exception:
    traceback.print_exc(file=sys.stdout)
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = [
    ('p1-s02-three-voices.html', 5040),
    ('p2-s07-thousand-x.html',   3880),
    ('p3-s19-socket.html',       5000),
    ('p4-s42-auto-route.html',   3680),
    ('p5-s01-opening.html',      3560),
]

GEOM_JS = """() => {
    const st = document.querySelector('.stage');
    const sr = st.getBoundingClientRect();
    const a  = st.querySelector('.frame-a');
    const b  = st.querySelector('.frame-b');
    const g  = (e) => { const r = e.getBoundingClientRect();
        return [r.left-sr.left, r.top-sr.top, r.right-sr.left, r.bottom-sr.top]; };
    // 检查 frame-b 内部是否有内容溢出（scroll > client 即溢出）
    const ov = [b.scrollWidth - b.clientWidth, b.scrollHeight - b.clientHeight];
    return { a: a ? g(a) : null, b: b ? g(b) : null, ov: ov,
             k: parseFloat(getComputedStyle(
                    document.querySelector('.scaler')).transform.split(',')[0].replace('matrix(','')) };
}"""

fails = []
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page(viewport={'width': 1600, 'height': 950},
                     device_scale_factor=1)
    for name, total in PAGES:
        url = 'file:///' + os.path.join(HERE, name).replace('\\', '/')
        pg.goto(url)
        pg.wait_for_timeout(300)

        tag = name.split('-')[0]
        # 三个时点：入场中 / 动效中段 / 稳定态
        for label, wait in (('a-enter', 250), ('b-mid', int(total * .5)),
                            ('c-settle', int(total * .95))):
            pg.goto(url)                      # 重新加载，保证时间轴从 0 起
            pg.wait_for_timeout(wait)
            pg.screenshot(path=os.path.join(HERE, '_pv_%s_%s.png' % (tag, label)))

        d = pg.evaluate(GEOM_JS)
        k = d['k'] or 1.0
        a, b, ov = d['a'], d['b'], d['ov']
        print('=' * 66)
        print('%s   缩放 k=%.4f' % (name, k))
        if a: print('  frame-a  L%7.1f T%7.1f R%7.1f B%7.1f' % tuple(a))
        if b: print('  frame-b  L%7.1f T%7.1f R%7.1f B%7.1f' % tuple(b))

        if a and b:
            # ★ getBoundingClientRect 返回的是 transform 之后的视口坐标，
            #   .scaler 上有 scale(k)，因此必须除以 k 才回到 1920 设计坐标系。
            #   曾漏掉这一步 → 39px 被读成 30.5px 而误判 FAIL（断言错，页面对）。
            a = [v / k for v in a]
            b = [v / k for v in b]
            print('  换算回设计坐标 ÷%.4f：' % k)
            print('    frame-a  L%7.1f T%7.1f R%7.1f B%7.1f' % tuple(a))
            print('    frame-b  L%7.1f T%7.1f R%7.1f B%7.1f' % tuple(b))
            hgap = b[0] - a[2]                  # B.left - A.right
            vgap = a[1] - b[3]                  # A.top  - B.bottom（竖向布局）
            if hgap > 5:
                print('  → 横向间距 %.1fpx' % hgap)
                ok = abs(hgap - 39) <= 2
                print('     %s 目标 39px' % ('OK ' if ok else 'FAIL'))
                if not ok: fails.append('%s 横向间距 %.1f≠39' % (name, hgap))
                # SPLIT 页还要核对四边绝对像素，防止令牌被人改动
                for lbl, got, exp in (('A.left', a[0], 24), ('A.right', a[2], 612),
                                      ('B.left', b[0], 651), ('A.top', a[1], 46),
                                      ('B.top', b[1], 58)):
                    good = abs(got - exp) <= 2
                    print('     %s %-8s %6.1f  期望 %d' %
                          ('OK ' if good else 'FAIL', lbl, got, exp))
                    if not good: fails.append('%s %s=%.1f≠%d' % (name, lbl, got, exp))
            elif vgap > 5:
                print('  → 竖向间距 %.1fpx' % vgap)
                ok = abs(vgap - 39) <= 2
                print('     %s 目标 39px' % ('OK ' if ok else 'FAIL'))
                if not ok: fails.append('%s 竖向间距 %.1f≠39' % (name, vgap))
            else:
                print('  → FAIL 两框叠压！h=%.1f v=%.1f' % (hgap, vgap))
                fails.append('%s 叠压 h=%.1f v=%.1f' % (name, hgap, vgap))
        else:
            print('  (单框页，无需间距检查)')

        if ov[0] > 1 or ov[1] > 1:
            print('  → FAIL frame-b 内容溢出 dx=%d dy=%d' % (ov[0], ov[1]))
            fails.append('%s frame-b 溢出 %s' % (name, ov))
        else:
            print('  → 内容无溢出 OK')

    br.close()

print('=' * 66)
if fails:
    print('失败 %d 项：' % len(fails))
    for f in fails: print('  ✗', f)
else:
    print('全部通过：5 页几何分离正确、内容无溢出。')
