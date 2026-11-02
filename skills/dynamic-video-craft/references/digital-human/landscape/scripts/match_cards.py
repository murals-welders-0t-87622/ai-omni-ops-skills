# -*- coding: utf-8 -*-
"""
match_cards.py — 卡片动效映射工具

用途：
  1. 从 references/cards/ 生成 78 张卡片索引
  2. 把卡片 ID 写进 STORYBOARD.md 的每个 SHOT（在「动效」字段后插入「卡片动效」）

设计原则：
  - 本脚本**不做自动语义匹配**。卡片归属必须逐镜人工判定后写进 mapping.json，
    脚本只负责校验 + 写入。原因见 references/card-motion-mapping.md §六.1：
    用"数字"这类宽泛词自动匹配会把 number-counter 塞进 20+ 个无关镜头。
  - 幂等：先清理再插入，可重复运行。

用法：
  python scripts/match_cards.py --index  --cards references/cards --out _卡片索引.md
  python scripts/match_cards.py --clean  --storyboard STORYBOARD.md
  python scripts/match_cards.py --apply  --storyboard STORYBOARD.md \
         --cards references/cards --map mapping.json
  python scripts/match_cards.py --report --storyboard STORYBOARD.md --out _卡片动效映射表.md
"""
import argparse
import io
import json
import os
import re
import sys

CARD_FIELD = '- **卡片动效**'
KEYS = {'name', '标题', '优先级', '代码', '一句话', '适用', '时长', '能量', '类别'}
SHOT_RE = re.compile(r'^###\s+SHOT\s+([\d\-]+)\s*｜\s*(.+)$')


# ---------- 卡片索引 ----------

def parse_frontmatter(raw):
    m = re.match(r'---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
    if not m:
        return {}
    meta, cur_key = {}, None
    for ln in m.group(1).split('\n'):
        if not ln.strip():
            continue
        pos = ln.find(':')
        if pos > 0 and ln[:pos].strip() in KEYS:
            cur_key = ln[:pos].strip()
            meta[cur_key] = ln[pos + 1:].strip()
        elif cur_key:
            meta[cur_key] = (meta.get(cur_key, '') + ' ' + ln.strip()).strip()
    return meta


def load_cards(card_dir):
    cards = []
    for fn in sorted(os.listdir(card_dir)):
        if not fn.endswith('.md'):
            continue
        meta = parse_frontmatter(io.open(os.path.join(card_dir, fn), encoding='utf-8').read())
        cards.append({
            'id': meta.get('name') or fn[:-3],
            'title': meta.get('标题', ''),
            'category': meta.get('类别', ''),
            'energy': meta.get('能量', ''),
            'priority': meta.get('优先级', ''),
            'summary': meta.get('一句话', ''),
            'usage': meta.get('适用', ''),
            'file': fn,
        })
    return cards


def cmd_index(card_dir, out):
    cards = load_cards(card_dir)
    w = io.open(out, 'w', encoding='utf-8')
    w.write('# 卡片动效索引（%d 张）\n\n' % len(cards))
    w.write('| 卡片 ID | 中文标题 | 类别 | 能量 | 优先级 | 一句话 |\n')
    w.write('|---|---|---|---|---|---|\n')
    for c in cards:
        s = (c['summary'] or '')[:80].replace('\n', ' ').replace('|', '／')
        w.write('| `%s` | %s | %s | %s | %s | %s |\n'
                % (c['id'], c['title'], c['category'], c['energy'], c['priority'], s))
    w.close()
    print('索引已生成：%s（%d 张）' % (out, len(cards)))


# ---------- STORYBOARD 处理 ----------

def read_shots(lines):
    """返回 [(start, end, sid, title)]"""
    shots, cur = [], None
    for i, ln in enumerate(lines):
        m = SHOT_RE.match(ln)
        if m:
            if cur:
                shots.append((cur[0], i, cur[1], cur[2]))
            cur = (i, m.group(1), m.group(2).strip())
    if cur:
        shots.append((cur[0], len(lines), cur[1], cur[2]))
    return shots


def cmd_clean(sb_path):
    lines = io.open(sb_path, encoding='utf-8').read().split('\n')
    kept = [l for l in lines if not l.startswith(CARD_FIELD)]
    io.open(sb_path, 'w', encoding='utf-8').write('\n'.join(kept))
    print('已清理 %d 行卡片动效字段' % (len(lines) - len(kept)))


def cmd_report(sb_path, out):
    lines = io.open(sb_path, encoding='utf-8').read().split('\n')
    shots = read_shots(lines)
    w = io.open(out, 'w', encoding='utf-8')
    w.write('# 卡片动效映射表 · %d 镜\n\n| 镜头 | 标题 | 卡片动效 |\n|---|---|---|\n' % len(shots))
    for start, end, sid, title in shots:
        t = re.sub(r'｜\s*`[^`]+`\s*（[^）]+）', '', title).strip()
        cards = ''
        for ln in lines[start:end]:
            if ln.startswith(CARD_FIELD):
                cards = ln.split('：', 1)[1].strip()
                break
        w.write('| %s | %s | %s |\n' % (sid, t, cards))
    w.close()
    print('映射表已生成：%s（%d 镜）' % (out, len(shots)))


def cmd_apply(sb_path, card_dir, map_path):
    cards = load_cards(card_dir)
    valid = {c['id'] for c in cards}
    mapping = json.load(io.open(map_path, encoding='utf-8'))

    # 校验
    bad = []
    for sid, ids in mapping.items():
        for cid in ids:
            if cid not in valid:
                bad.append((sid, cid))
    if bad:
        print('以下卡片 ID 在卡片库中不存在，请先修正 mapping：')
        for sid, cid in bad:
            print('  SHOT %s -> %s' % (sid, cid))
        print('\n可用 ID：' + ', '.join(sorted(valid)))
        sys.exit(1)

    lines = io.open(sb_path, encoding='utf-8').read().split('\n')
    lines = [l for l in lines if not l.startswith(CARD_FIELD)]   # 幂等清理
    shots = read_shots(lines)

    insertions = []
    for start, end, sid, title in shots:
        ids = mapping.get(sid)
        if not ids:
            print('  警告：SHOT %s 无映射，跳过' % sid)
            continue
        card_text = '%s：%s' % (CARD_FIELD, '、'.join('`%s`' % c for c in ids))
        insert_at = None
        for j in range(start, end):
            if lines[j].startswith('- **动效**'):
                insert_at = j + 1
                for k in range(j + 1, end):
                    if (lines[k].startswith('- **') or lines[k].startswith('### ')
                            or lines[k].startswith('---')):
                        insert_at = k
                        break
                break
        if insert_at is None:
            for j in range(start, end):
                if lines[j].startswith('- **字幕**'):
                    insert_at = j
                    break
            else:
                insert_at = end
        insertions.append((insert_at, card_text, sid, ids))

    insertions.sort(key=lambda x: x[0], reverse=True)
    for idx, text, sid, ids in insertions:
        lines.insert(idx, text)

    io.open(sb_path, 'w', encoding='utf-8').write('\n'.join(lines))

    print('已写入 %d 个镜头的卡片动效字段' % len(insertions))
    for idx, text, sid, ids in sorted(insertions, key=lambda x: x[2]):
        print('  %-6s %s' % (sid, '、'.join(ids)))


def main():
    ap = argparse.ArgumentParser(description='卡片动效映射工具')
    ap.add_argument('--index', action='store_true', help='生成卡片索引')
    ap.add_argument('--clean', action='store_true', help='清理 STORYBOARD 中的卡片动效字段')
    ap.add_argument('--apply', action='store_true', help='把 mapping 写入 STORYBOARD')
    ap.add_argument('--report', action='store_true', help='生成映射汇总表')
    ap.add_argument('--cards', help='references/cards 目录')
    ap.add_argument('--storyboard', help='STORYBOARD.md 路径')
    ap.add_argument('--map', help='mapping.json 路径')
    ap.add_argument('--out', help='输出文件路径')
    a = ap.parse_args()

    if a.index:
        cmd_index(a.cards, a.out)
    elif a.clean:
        cmd_clean(a.storyboard)
    elif a.apply:
        cmd_apply(a.storyboard, a.cards, a.map)
    elif a.report:
        cmd_report(a.storyboard, a.out)
    else:
        ap.print_help()


if __name__ == '__main__':
    main()
