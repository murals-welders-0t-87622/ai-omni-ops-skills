# -*- coding: utf-8 -*-
"""
预览页 vs 生产页 并排目视对比（人工验收的唯一手段）

为什么必须有这一步：
  用户的原始质问是「5 个 demo 一个都没实现，其他效果非常拉跨」。
  上一版三层验收（几何 / 像素 / 渲染日志）全绿，成片依然平庸 ——
  机械断言能挡住"错"，挡不住"平庸"。
  富度门禁（_rich_check.py）解决了"数量"，但节点数达标 ≠ 画面好看。
  唯一无法自动化的环节就是把两张图放在一起看。

对比对：
  previews/p1-s02-three-voices.html   <->  compositions/scene-02.html
  previews/p2-s07-thousand-x.html     <->  compositions/scene-07.html
  previews/p3-s19-socket.html         <->  compositions/scene-19.html
  previews/p4-s42-auto-route.html     <->  compositions/scene-42.html
  previews/p5-s01-opening.html        <->  compositions/scene-01.html

★ 预览页的动画挂在 .run 门控下（靠 _shell.js 点击播放才加 class），
  所以截图前必须手动给容器加 .run，否则预览页会是"未入场"的空白态，
  对比就毫无意义 —— 这是本脚本最容易踩的坑。
"""
import io
import os
import sys
import asyncio

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.stdout = io.TextIOWrapper(open('_side_by_side.log', 'wb'),
                              encoding='utf-8', write_through=True)

from playwright.async_api import async_playwright
from PIL import Image, ImageDraw

PAIRS = [
    ('previews/p1-s02-three-voices.html', 'compositions/scene-02.html', 'S02 三种声音'),
    ('previews/p2-s07-thousand-x.html',   'compositions/scene-07.html', 'S07 千倍增长'),
    ('previews/p3-s19-socket.html',       'compositions/scene-19.html', 'S19 插座类比'),
    ('previews/p4-s42-auto-route.html',   'compositions/scene-42.html', 'S42 自动路由'),
    ('previews/p5-s01-opening.html',      'compositions/scene-01.html', 'S01 开场'),
]
OUT = '_side_by_side'
os.makedirs(OUT, exist_ok=True)

# 让预览页的 .run 门控动画入场，并把所有动画 seek 到 70% 处
SEEK = '''(frac) => {
  // 预览页：补上 _shell.js 才会加的 .run
  document.querySelectorAll('.stage, .preview, .card, body > div')
    .forEach(e => e.classList.add('run'));
  const as = document.getAnimations();
  for (const a of as) {
    a.pause();
    const d = a.effect.getTiming().duration;
    const it = a.effect.getTiming().iterations;
    let ms = (typeof d === 'number' ? d : 1000) * frac;
    if (it === Infinity && typeof d === 'number' && d > 0) ms = ms % d;
    a.currentTime = ms;
  }
  return as.length;
}'''


async def shot(pg, path, out, frac=0.7):
    await pg.goto('file:///' + os.path.abspath(path).replace('\\', '/'))
    await pg.wait_for_timeout(400)
    n = await pg.evaluate(SEEK, frac)
    await pg.wait_for_timeout(160)
    # 优先截 .stage（去掉预览外壳的 HUD），没有就整页
    el = await pg.query_selector('.stage')
    if el:
        await el.screenshot(path=out)
    else:
        await pg.screenshot(path=out)
    return n


def stitch(a, b, title, out):
    """上下叠放：上=预览页(目标) 下=生产页(实际)，等宽缩放"""
    ia, ib = Image.open(a).convert('RGB'), Image.open(b).convert('RGB')
    W = 1400
    ia = ia.resize((W, int(ia.height * W / ia.width)), Image.LANCZOS)
    ib = ib.resize((W, int(ib.height * W / ib.width)), Image.LANCZOS)
    band = 46
    cv = Image.new('RGB', (W, ia.height + ib.height + band * 2 + 8), (26, 22, 18))
    d = ImageDraw.Draw(cv)
    y = 0
    d.text((14, 14), '%s  ▸ 预览页 previews/（目标）' % title, fill=(240, 226, 200))
    y += band
    cv.paste(ia, (0, y)); y += ia.height + 8
    d.text((14, y + 14), '%s  ▸ 生产页 compositions/（实际）' % title, fill=(160, 220, 170))
    y += band
    cv.paste(ib, (0, y))
    cv.save(out)


async def main():
    print('=== 预览页 vs 生产页 并排对比 ===')
    async with async_playwright() as pw:
        br = await pw.chromium.launch(headless=True, args=[
            '--autoplay-policy=no-user-gesture-required',
            '--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
        ])
        pg = await br.new_page(viewport={'width': 1920, 'height': 1080},
                               device_scale_factor=1)
        for prev, comp, title in PAIRS:
            if not (os.path.exists(prev) and os.path.exists(comp)):
                print('[SKIP] %s  (缺文件)' % title)
                continue
            tag = os.path.basename(comp).replace('.html', '')
            pa = os.path.join(OUT, '%s_prev.png' % tag)
            pb = os.path.join(OUT, '%s_comp.png' % tag)
            na = await shot(pg, prev, pa)
            nb = await shot(pg, comp, pb)
            merged = os.path.join(OUT, 'cmp_%s.png' % tag)
            stitch(pa, pb, title, merged)
            print('[OK] %-12s 预览动画=%-3d 生产动画=%-3d -> %s'
                  % (title, na, nb, merged))
        await br.close()
    print('=== 完成，输出目录 %s ===' % OUT)


asyncio.run(main())
