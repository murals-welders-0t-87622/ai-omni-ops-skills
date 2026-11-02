# -*- coding: utf-8 -*-
"""
VAD 语音时长域字幕对齐（零外部模型依赖）

为什么不用 proportional：
  proportional 把「句间停顿」也算进可分配时长，误差随句序累积，
  实测 PART02/PART03 偏差达 3~4s。

本方案：
  1. ffmpeg silencedetect 取真实停顿区间
  2. 只保留语音区间，构成「语音时长域」（总长 T）
  3. 在语音域内按字数比例分配每条短句 -> 天然跳过停顿
  4. 映射回真实时间轴
  5. 句末边界吸附到最近的静音中点（阈值 0.35s）进一步提精
  6. 按段累加 offset（真实音频时长 + 段间留白），输出全片 timing.json

用法：
  python vad_align.py --dir <任务目录>          # 全部段
  python vad_align.py --dir <任务目录> 1,2      # 指定段

前置：任务目录下需有 audio/PARTNN.wav + audio/script_NN.json
      （可选）remotion/src/shotsReal.ts —— 存在时自动沿用其段首偏移，
      保证字幕时间轴与镜位完全同源。
输出：remotion/src/timing.json
"""
import json
import os
import re
import subprocess
import sys
import time

_ARGV = sys.argv[1:]
BASE = os.path.dirname(os.path.abspath(__file__))
if '--dir' in _ARGV:
    _i = _ARGV.index('--dir')
    if _i + 1 < len(_ARGV):
        BASE = _ARGV[_i + 1]
        del _ARGV[_i:_i + 2]
AUDIO = os.path.join(BASE, 'audio')
OUT = os.path.join(BASE, 'remotion', 'src', 'timing.json')

NOISE = os.environ.get('VAD_NOISE', '-32dB')
MIND = os.environ.get('VAD_MIN', '0.08')
GAP = float(os.environ.get('SEG_GAP', '0.35'))     # 段间留白
SNAP = float(os.environ.get('SNAP_TOL', '0.35'))   # 锚点吸附容差
MAXLINE = int(os.environ.get('MAX_LINE', '12'))    # 底部字幕单行字数上限
PUNC = re.compile(r'[\s，。、！？；：""''（）《》,.!?;:]+')


def log(m):
    print('[%s] %s' % (time.strftime('%H:%M:%S'), m), flush=True)


def nchars(s):
    return len(PUNC.sub('', s))


def duration(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def vad(path):
    """返回 (silences=[(s,e)], mids=[静音中点])"""
    cmd = ['ffmpeg', '-hide_banner', '-nostats', '-i', path,
           '-af', 'silencedetect=noise=%s:d=%s' % (NOISE, MIND), '-f', 'null', '-']
    out = subprocess.run(cmd, capture_output=True, text=True).stderr
    starts = [float(m.group(1)) for m in re.finditer(r'silence_start:\s*([\d.]+)', out)]
    ends = [float(m.group(1)) for m in re.finditer(r'silence_end:\s*([\d.]+)', out)]
    sil, mids = [], []
    for i in range(min(len(starts), len(ends))):
        s, e = starts[i], ends[i]
        if e > s:
            sil.append((s, e))
            mids.append((s + e) / 2)
    return sil, mids


def speech_segments(sil, total):
    """停顿取反 -> 语音区间"""
    segs = []
    cur = 0.0
    for (s, e) in sil:
        if s > cur + 0.02:
            segs.append((cur, s))
        cur = max(cur, e)
    if total > cur + 0.02:
        segs.append((cur, total))
    # 丢弃 <0.15s 的碎片（并入相邻影响很小，直接去掉更稳定）
    segs = [(s, e) for (s, e) in segs if e - s >= 0.15]
    if not segs:
        segs = [(0.0, total)]
    return segs


def to_real(u, segs):
    """语音域时间 u -> 真实时间"""
    acc = 0.0
    for (s, e) in segs:
        d = e - s
        if u <= acc + d + 1e-9:
            return s + (u - acc)
        acc += d
    return segs[-1][1]


SPLIT_AT = re.compile(r'(?<=[，。、；：！？])')


def split_long(text, start, end):
    """单行超 MAXLINE 字时，按标点切成 ≤MAXLINE 的片段，时长按字数比例分摊"""
    if len(text) <= MAXLINE:
        return [{'text': text, 'start': start, 'end': end}]
    parts = [p for p in SPLIT_AT.split(text) if p]
    merged, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) > MAXLINE:
            merged.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        merged.append(cur)
    if len(merged) <= 1:
        return [{'text': text, 'start': start, 'end': end}]
    ws = [max(len(PUNC.sub('', m)), 1) for m in merged]
    C = sum(ws)
    span = max(end - start, 0.2)
    out, acc = [], 0.0
    for w, m in zip(ws, merged):
        s0 = start + span * acc / C
        acc += w
        s1 = start + span * acc / C
        out.append({'text': m, 'start': round(s0, 3), 'end': round(s1, 3)})
    return out


RE_SPAN = re.compile(r"'(\d+)-(\d+)':\s*\{\s*startSec:\s*([\d.]+),\s*endSec:\s*([\d.]+)\s*\}")


def real_span_offsets():
    """从 shotsReal.ts 读取各段起点，保证字幕时间轴与镜位完全同源"""
    p = os.path.join(BASE, 'remotion', 'src', 'shotsReal.ts')
    if not os.path.exists(p):
        return {}
    txt = open(p, encoding='utf-8').read()
    first = {}
    last = {}
    for m in RE_SPAN.finditer(txt):
        part = int(m.group(1))
        s, e = float(m.group(3)), float(m.group(4))
        first[part] = min(first.get(part, s), s)
        last[part] = max(last.get(part, e), e)
    return {'first': first, 'last': last}


def build():
    segs_arg = _ARGV[0] if (_ARGV and not _ARGV[0].startswith('--')) else None
    parts = [int(x) for x in segs_arg.split(',')] if segs_arg else list(range(1, 8))
    span = real_span_offsets()
    first = span.get('first', {})

    scenes = []
    offset = 0.0
    sid = 0
    meta = {'method': 'vad-speech-domain', 'noise': NOISE, 'mind': MIND,
            'gap': GAP, 'snap': SNAP, 'segments': []}

    for n in parts:
        wav = os.path.join(AUDIO, 'PART%02d.wav' % n)
        sj = os.path.join(AUDIO, 'script_%02d.json' % n)
        if not (os.path.exists(wav) and os.path.exists(sj)):
            log('PART%02d 缺文件，跳过' % n)
            continue

        # 字幕短句：底部素排规范要求「单行 ≤12 字」，
        # 因此从 script_%02d.json 中取 ≤12 字的短语（该文件同时含短语与整句）。
        sents = json.load(open(sj, encoding='utf-8'))['sentences']
        # 剔除旁白/导演提示语（如「（承接上句，聚焦…）」），这类不是口播内容
        sents = [s for s in sents if not re.search(r'[（(].*?[)）]', s)]
        # 以「显示长度」判定，避免去标点后误判（标点与空格同样占位）
        sub = [s.strip() for s in sents if 0 < len(s.strip()) <= MAXLINE]
        if len(sub) < 3:
            # 兜底：退化为「极小句」（被其他句子包含者即为更细粒度单元）
            sub = []
            for i, s in enumerate(sents):
                ni = PUNC.sub('', s)
                if not ni:
                    continue
                if any(i != j and len(PUNC.sub('', t)) > len(ni)
                       and ni in PUNC.sub('', t) for j, t in enumerate(sents)):
                    sub.append(s)
        if not sub:
            sub = [s for s in sents if PUNC.sub('', s)]

        total = duration(wav)
        # 段首偏移对齐 shotsReal.ts 实测镜位（无实测数据时回退为累加）
        if n in first:
            offset = first[n]
        seg_off = offset
        sil, mids = vad(wav)
        speech = speech_segments(sil, total)
        T = sum(e - s for s, e in speech)

        weights = [nchars(s) for s in sub]
        C = sum(weights) or 1

        used = set()
        acc = 0.0
        rows = []
        for w, text in zip(weights, sub):
            u0 = T * acc / C
            acc += w
            u1 = T * acc / C
            st = to_real(u0, speech)
            en = to_real(u1, speech)
            # 句末吸附到最近静音中点
            best, bd = None, SNAP
            for k, m in enumerate(mids):
                if k in used:
                    continue
                d = abs(m - en)
                if d < bd:
                    best, bd = k, d
            if best is not None:
                used.add(best)
                en = mids[best]
            en = max(en, st + 0.15)
            rows.append({'text': text, 'start': st, 'end': en})

        # 单调递增修正
        prev = 0.0
        for r in rows:
            r['start'] = max(r['start'], prev)
            r['end'] = max(r['end'], r['start'] + 0.15)
            prev = r['end']

        for r in rows:
            sid += 1
            for piece in split_long(r['text'], r['start'], r['end']):
                scenes.append({
                    'id': 's%d' % sid,
                    'text': piece['text'],
                    'startSec': round(piece['start'] + seg_off, 3),
                    'durationSec': round(piece['end'] - piece['start'], 3),
                })

        snapped = len(used)
        log('PART%02d 时长%.2fs 语音%.2fs 停顿%d句 短句%d条 锚点吸附%d'
            % (n, total, T, len(sil), len(rows), snapped))
        meta['segments'].append({'part': n, 'audioSec': round(total, 2),
                                 'speechSec': round(T, 2),
                                 'silences': len(sil), 'lines': len(rows),
                                 'snapped': snapped,
                                 'offset': round(seg_off, 3)})
        # 下一段偏移：优先沿用 shotsReal.ts 的实测段首，保证与镜位同源
        nxt = first.get(n + 1)
        offset = nxt if nxt is not None else offset + total + GAP

    data = {'totalSec': round(offset, 2), 'scenes': scenes,
            '_meta': dict(meta, generated=time.strftime('%Y-%m-%d %H:%M:%S'))}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    log('写出 %s：%d 条字幕，总时长 %.2fs' % (OUT, len(scenes), offset))


if __name__ == '__main__':
    build()
