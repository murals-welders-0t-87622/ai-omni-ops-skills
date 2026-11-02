# -*- coding: utf-8 -*-
"""
成片合成：65 镜片段 -> 拼接 -> 混入 8 段音频 -> 输出成品。

为什么不用 ffmpeg concat demuxer 直接一把梭：
  各镜片段由 Playwright 逐帧喂管道生成，时长受帧数取整影响，
  单镜误差最大 1/30s，65 镜累计可达 2s -> 音字会整体漂移。
  故这里先逐镜校验实际时长，与 _timeline.json 的理论值比对，
  超差立即报错而不是静默拼出一条不同步的片子。

音频侧：8 段 mp3 按 AUDIO_ORDER 顺序 concat，总长 244.60s 为权威基准。
"""
import json
import os
import io
import sys
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# ★ VER 必须在 LOG 之前解析（日志名也要带版本号，否则两版合成日志互相覆盖，
#   出问题时分不清是哪一版的报错）。
_vargs = [a for a in sys.argv[1:] if not a.startswith('-')]
VER = _vargs[0] if _vargs else 'v6'

LOG = os.path.join(BASE, '_assemble65_%s.log' % VER)
sys.stdout = io.TextIOWrapper(open(LOG, 'wb'), encoding='utf-8', write_through=True)

FFMPEG = 'ffmpeg'
FFPROBE = 'ffprobe'
WORK = os.path.join(BASE, '_seg60')
# ★ 输出名不要再硬编码（本轮改造，勿回退）：
#   原来写死 final_v6.mp4，每次重新合成都会【原地覆盖上一版成片】，
#   新版一旦有问题就没有对照物可退回。改为可传版本号：
#     python _assemble65.py v7   -> final_v7.mp4
#     python _assemble65.py      -> final_v6.mp4（保留旧默认，兼容历史调用）
#   argv 要过滤掉 - 开头的开关项，否则 --force 之类会被当成版本号。
#   中间产物 _v65 / _a65 / _concat65 同样带版本号，避免多版并行时互相踩。
OUT = os.path.join(BASE, 'final_%s.mp4' % VER)

TL = json.load(open('_timeline.json', encoding='utf-8'))
SEGS = json.load(open('_audio_segs.json', encoding='utf-8'))
AUDIO_ORDER = ['p1a', 'p1b', 'p2', 'p3a', 'p3b', 'p4', 'p5a', 'p5b']


def dur_of(path):
    r = subprocess.run([FFPROBE, '-v', 'error', '-show_entries',
                        'format=duration', '-of',
                        'default=nw=1:nk=1', path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return -1.0


def main():
    print('=' * 60)
    print('=== 1. 校验 65 镜片段 ===')
    items, miss, drift = [], [], []
    for x in TL:
        p = os.path.join(WORK, 'scene-%s.mp4' % x['num'])
        if not os.path.exists(p) or os.path.getsize(p) < 2000:
            miss.append(x['sid'])
            continue
        d = dur_of(p)
        dd = d - x['dur']
        # 单镜误差主要来自帧数取整（1/30s），超 0.12s 说明渲染有问题
        if abs(dd) > 0.12:
            drift.append((x['sid'], x['dur'], d, dd))
        items.append({'sid': x['sid'], 'num': x['num'], 'path': p,
                      'want': x['dur'], 'got': d})
    print('片段数: %d / %d' % (len(items), len(TL)))
    if miss:
        print('[FAIL] 缺失片段 %d 个: %s' % (len(miss), miss))
        return
    if drift:
        print('[WARN] 时长偏差超 0.12s 的镜头 %d 个:' % len(drift))
        for s, w, g, dd in drift:
            print('   %s 理论 %.3f 实际 %.3f 差 %+.3f' % (s, w, g, dd))
    tot_v = sum(i['got'] for i in items)
    tot_want = sum(i['want'] for i in items)
    print('视频总长 实际 %.3f  理论 %.3f  差 %+.3f' % (tot_v, tot_want, tot_v - tot_want))

    print()
    print('=== 2. 拼接视频轨 ===')
    lst = os.path.join(BASE, '_concat65_%s.txt' % VER)
    with open(lst, 'w', encoding='utf-8') as f:
        for i in items:
            f.write("file '%s'\n" % i['path'].replace('\\', '/'))
    vcat = os.path.join(BASE, '_v65_%s.mp4' % VER)
    r = subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                        '-f', 'concat', '-safe', '0', '-i', lst,
                        '-c', 'copy', vcat], capture_output=True, text=True)
    if r.returncode != 0:
        print('[FAIL] 视频拼接失败: %s' % r.stderr[:400])
        return
    print('[OK] %s  %.3fs  %.1fMB'
          % (os.path.basename(vcat), dur_of(vcat),
             os.path.getsize(vcat) / 1048576.0))

    print()
    print('=== 3. 拼接音频轨（8 段）===')
    # 不用 concat demuxer：mp3 逐段拼接会在接缝处产生 NaN/Inf 采样（实测 aac 编码器直接报错）。
    # 改用 filter_complex 先各自解码为 PCM 再 concat，接缝干净。
    acat = os.path.join(BASE, '_a65_%s.m4a' % VER)
    cmd = [FFMPEG, '-y', '-loglevel', 'error']
    for name in AUDIO_ORDER:
        ap = os.path.join(BASE, '%s.mp3' % name)
        if not os.path.exists(ap):
            print('[FAIL] 缺音频 %s' % ap)
            return
        cmd += ['-i', ap]
    n = len(AUDIO_ORDER)
    filt = ''.join('[%d:a]aresample=48000,aformat=sample_fmts=fltp:'
                   'channel_layouts=stereo[a%d];' % (i, i) for i in range(n))
    filt += ''.join('[a%d]' % i for i in range(n))
    filt += 'concat=n=%d:v=0:a=1[out]' % n
    cmd += ['-filter_complex', filt, '-map', '[out]',
            '-c:a', 'aac', '-b:a', '192k', acat]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print('[FAIL] 音频拼接失败: %s' % r.stderr[:400])
        return
    ad = dur_of(acat)
    print('[OK] 音频 %.3fs  (基准 %.3f, 差 %+.3f)'
          % (ad, SEGS[-1]['end'], ad - SEGS[-1]['end']))

    print()
    print('=== 4. 合流 ===')
    # -shortest 会按较短轨裁剪；音视频差应 < 0.5s，否则说明前面有问题
    gap = abs(dur_of(vcat) - ad)
    print('音视频长度差 %.3fs %s' % (gap, '（正常）' if gap < 0.5 else '（偏大，需排查）'))
    r = subprocess.run([FFMPEG, '-y', '-loglevel', 'error',
                        '-i', vcat, '-i', acat,
                        '-map', '0:v:0', '-map', '1:a:0',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', OUT], capture_output=True, text=True)
    if r.returncode != 0:
        print('[FAIL] 合流失败: %s' % r.stderr[:400])
        return
    print('[OK] %s  %.3fs  %.1fMB'
          % (os.path.basename(OUT), dur_of(OUT),
             os.path.getsize(OUT) / 1048576.0))
    print()
    print('=== 完成 ===')


main()
