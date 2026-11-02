#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_render60.py — 把 60 个纯 CSS 合成页渲染成视频片段

为什么不能复用 render_frames.py：
  旧脚本靠 gsap.globalTimeline.seek(t) 驱动，但新版 60 页是
  「纯 CSS @keyframes + <video>」，没有 GSAP。若直接截图会得到
  「动画随机进度 + 视频黑帧」的废片。

确定性 seek 的两把钥匙：
  1. CSS 动画 -> Web Animations API：
     document.getAnimations() 拿到全部 Animation 对象，
     置 a.pause() 后写 a.currentTime = t*1000（毫秒），
     即可把任意 CSS 动画钉到精确进度。
  2. <video> -> video.currentTime = 段内偏移 + 帧内时间
     数字人必须叠加 data-off（该镜在音频段内的起点），否则
     每镜都从 0 秒开始播，唇形对不上旁白。
     seek 后必须等 'seeked' 事件，不能 sleep 猜。

15fps 抽帧 -> 管道喂 ffmpeg -> 输出 30fps（与旧管线一致）。
"""
import io
import json
import os
import subprocess
import sys
import traceback

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
WORK = os.path.join(BASE, '_seg60')
COMP = os.path.join(BASE, 'compositions')
os.makedirs(WORK, exist_ok=True)
LOG = os.path.join(BASE, '_render60.log')
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

FFMPEG = 'ffmpeg'
FPS = 15          # 抽帧率
OUT_FPS = 30      # 输出帧率
W, H = 1920, 1080

TL = json.load(open('_timeline.json', encoding='utf-8'))

# 把 CSS 动画钉到精确进度；返回原始值方便调试
PIN_JS = """(t) => {
  const anims = document.getAnimations();
  for (const a of anims) {
    try {
      a.pause();
      // 无限循环动画（如光标闪烁）取模，避免 currentTime 溢出后停在末态
      const d = (a.effect && a.effect.getTiming) ? a.effect.getTiming().duration : null;
      const it = (a.effect && a.effect.getTiming) ? a.effect.getTiming().iterations : 1;
      let ms = t * 1000;
      if (it === Infinity && typeof d === 'number' && d > 0) ms = ms % d;
      a.currentTime = ms;
    } catch (e) {}
  }
  return anims.length;
}"""

# 视频精确 seek：等 seeked 事件，绝不 sleep 猜
SEEK_JS = """async (t) => {
  const vs = Array.from(document.querySelectorAll('video'));
  await Promise.all(vs.map(v => new Promise(res => {
    const off = parseFloat(v.dataset.off || '0') || 0;
    let target = off + t;
    const dur = isFinite(v.duration) ? v.duration : 0;
    // 素材短于需求时回绕，避免定格黑帧
    if (dur > 0.05) target = target % dur;
    v.pause();
    if (Math.abs(v.currentTime - target) < 0.004) return res(1);
    const done = () => { v.removeEventListener('seeked', done); res(1); };
    v.addEventListener('seeked', done);
    try { v.currentTime = target; } catch (e) { res(0); }
    setTimeout(() => res(0), 900);   // 兜底，不让单帧卡死整片
  })));
  return vs.length;
}"""

READY_JS = """async () => {
  const vs = Array.from(document.querySelectorAll('video'));
  await Promise.all(vs.map(v => new Promise(res => {
    if (v.readyState >= 2) return res(1);
    const ok = () => { v.removeEventListener('loadeddata', ok); res(1); };
    v.addEventListener('loadeddata', ok);
    setTimeout(() => res(0), 5000);
  })));
  return vs.map(v => v.readyState);
}"""

# 字幕逐句切换：data-cues 里存了本镜时间窗内的全部 SRT 分句及其镜内相对起点，
# 每帧取「起点 <= t 的最后一句」。若只静态显示第一句，长镜头会出现
# 字幕停住不动而旁白已经念到下一句的穿帮。
SUB_JS = """(t) => {
  const el = document.querySelector('.subtitle');
  if (!el) return '';
  let cs = el.__cues;
  if (!cs) {
    try { cs = JSON.parse(el.dataset.cues || '[]'); } catch (e) { cs = []; }
    el.__cues = cs;
  }
  let cur = '';
  for (const c of cs) { if (c.t <= t + 0.001) cur = c.x; }
  if (el.textContent !== cur) el.textContent = cur;
  return cur;
}"""


def render(pg, item, force=False):
    sid, num = item['sid'], item['num']
    dur = item['dur']
    out = os.path.join(WORK, 'scene-%s.mp4' % num)
    if os.path.exists(out) and os.path.getsize(out) > 2000 and not force:
        print('[%s] SKIP 已存在' % sid)
        return True

    html = os.path.join('compositions', 'scene-%s.html' % num)
    if not os.path.exists(html):
        print('[%s] MISS 页面缺失 %s' % (sid, html))
        return False

    nframes = max(1, int(round(dur * FPS)))
    pg.goto('file:///' + os.path.abspath(html).replace('\\', '/'),
            wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(300)
    rs = pg.evaluate(READY_JS)
    nanim = pg.evaluate(PIN_JS, 0.0)

    proc = subprocess.Popen(
        [FFMPEG, '-y', '-loglevel', 'error',
         '-f', 'image2pipe', '-framerate', str(FPS), '-i', 'pipe:0',
         '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
         '-r', str(OUT_FPS), '-preset', 'fast', '-crf', '20', out],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    clip = {'x': 0, 'y': 0, 'width': W, 'height': H}
    nsub = 0
    try:
        for i in range(nframes):
            t = i / float(FPS)
            pg.evaluate(PIN_JS, t)      # CSS 动画钉进度
            pg.evaluate(SEEK_JS, t)     # video 精确 seek
            s = pg.evaluate(SUB_JS, t)  # 字幕切到当前分句
            if s:
                nsub += 1
            proc.stdin.write(pg.screenshot(type='png', clip=clip))
        proc.stdin.close()
        err = proc.stderr.read().decode('utf-8', 'replace')
        proc.wait()
    except BaseException as e:
        print('[%s] ERROR %r' % (sid, e))
        print(traceback.format_exc())
        try:
            proc.kill()
        except Exception:
            pass
        return False

    if not os.path.exists(out) or os.path.getsize(out) < 2000:
        print('[%s] FFMPEG FAIL %s' % (sid, err[-300:]))
        return False
    print('[%s] OK %5.2fs %3d帧 anim=%d 有字幕帧=%d/%d video=%s %.2fMB'
          % (sid, dur, nframes, nanim, nsub, nframes, rs,
             os.path.getsize(out) / 1048576.0))
    return True


def main():
    from playwright.sync_api import sync_playwright
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    force = '--force' in sys.argv
    if args:
        # 显式指定镜号时不再过滤 skip：skip 镜已由 _gen_echo.py 生成回声页，
        # 需要能被单独渲染（否则 03/13/34/62 永远进不了渲染队列）。
        todo = [x for x in TL if x['num'] in args or x['sid'] in args]
        todo = [x for x in todo
                if os.path.exists(os.path.join(COMP, 'scene-%s.html' % x['num']))]
    else:
        # 不带参数 = 渲染全片，凡有合成页的镜头都渲染（含回声页）
        todo = [x for x in TL
                if os.path.exists(os.path.join(COMP, 'scene-%s.html' % x['num']))]

    print('=' * 56)
    print('渲染 %d 镜  抽帧 %dfps -> 输出 %dfps' % (len(todo), FPS, OUT_FPS))
    ok = bad = 0
    with sync_playwright() as p:
        br = p.chromium.launch(headless=True, args=[
            '--autoplay-policy=no-user-gesture-required',
            '--no-sandbox', '--disable-dev-shm-usage',
            '--hide-scrollbars', '--force-device-scale-factor=1',
            '--disable-gpu',
        ])
        pg = br.new_page(viewport={'width': W, 'height': H}, device_scale_factor=1)
        pg.on('pageerror', lambda e: print('   PAGEERROR %s' % str(e)[:160]))
        for x in todo:
            if render(pg, x, force):
                ok += 1
            else:
                bad += 1
        br.close()
    print('\n渲染完成 ok=%d fail=%d' % (ok, bad))
    sys.exit(0 if bad == 0 else 1)


if __name__ == '__main__':
    main()
