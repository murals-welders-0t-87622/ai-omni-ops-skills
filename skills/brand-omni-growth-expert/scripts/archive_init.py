#!/usr/bin/env python3
"""Create one brand task's local archive without moving or overwriting files."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

AREAS = {
    'overview': (('全局概览',), ('经营数据', '目标与计划', '经营复盘')),
    'brand': (('品牌增长',), ('品牌资料', '产品与服务', '市场与竞品', '增长报告', '战略与计划', '复盘')),
    'content': (('公域获客', '内容获客', '内容规划'), ('内容战略', '策略', '选题计划', '数据复盘')),
    'douyin': (('公域获客', '内容获客', '抖音视频号'), ('素材', '选题', '文案', '制作', '成片', '发布与复盘')),
    'xiaohongshu': (('公域获客', '内容获客', '小红书'), ('素材', '选题', '文案', '制作', '成片', '发布与复盘')),
    'wechat': (('公域获客', '内容获客', '公众号'), ('素材', '选题', '文案', '制作', '成片', '发布与复盘')),
    'geo': (('公域获客', 'GEO获客'), ('问题词', '平台观察', '知识与证据', '内容优化', '复测')),
    'leads': (('公域获客', '全网获客'), ('公开需求', '线索核验', '承接方案', '复盘')),
    'tencent-ads': (('公域获客', '投流获客', '腾讯广告'), ('账户与报表', '诊断', '计划与素材', '执行回执', '复盘')),
    'ocean-ads': (('公域获客', '投流获客', '巨量广告'), ('账户与报表', '诊断', '计划与素材', '执行回执', '复盘')),
    'influencers': (('公域获客', '达人合作'), ('达人调研', '合作方案', '内容素材', '发布回执', '效果复盘')),
    'private-ops': (('私域复购', '私域运营'), ('经营数据', '战略', '策略', '活动执行', '会员与客户分群', '复盘')),
    'sales': (('私域复购', 'AI销售'), ('客户需求', '商机与方案', '跟进与服务', '成交与复购', '复盘')),
    'detail': (('电商板块', '详情页'), ('产品资料', '卖点', '主图', '详情页', '商品视频', '复盘')),
    'taobao': (('电商板块', '淘宝天猫运营'), ('店铺数据', '战略目标', '经营策略', '商品内容', '执行记录', '经营复盘')),
}
CONTENT = {'douyin', 'xiaohongshu', 'wechat'}
RESERVED = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?$', re.I)

def is_link_or_junction(path):
    try:
        return path.is_symlink() or bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)
    except FileNotFoundError:
        return False

def component(value):
    if (not value or value in ('.', '..') or value != value.strip() or value.endswith('.')
            or any(c in value for c in '<>:"/\\|?*') or any(ord(c) < 32 for c in value)
            or RESERVED.fullmatch(value)):
        raise ValueError('任务名称包含不适合作为文件夹的字符或保留名称')
    return value

def day(value):
    if not re.fullmatch(r'\d{8}', value):
        raise ValueError('日期应为 YYYYMMDD')
    dt.datetime.strptime(value, '%Y%m%d')
    return value

def build(root, area, mode, name, date, end=None):
    root = Path(root).expanduser()
    if is_link_or_junction(root) or not root.is_dir():
        raise ValueError('品牌根目录必须是已存在的普通目录')
    root = root.resolve(strict=True)
    component(name)
    base, folders = AREAS[area]
    if mode == 'work':
        if area not in CONTENT:
            raise ValueError('作品模式仅用于抖音视频号、小红书或公众号')
        parts = (*base, day(date), name)
    elif mode == 'period':
        start, finish = day(date), day(end or date)
        if start > finish:
            raise ValueError('开始日期不能晚于结束日期')
        parts = (*base, '周期', f'{start}-{finish}', name)
    else:
        parts = (*base, '项目', name)
    task = root.joinpath(*parts)
    dirs = [task / folder for folder in folders]
    for target in [task, *dirs]:
        current = root
        for segment in target.relative_to(root).parts:
            component(segment)
            current = current / segment
            if is_link_or_junction(current):
                raise ValueError('路径包含符号链接，拒绝创建')
            if current.exists() and not current.is_dir():
                raise ValueError('目标路径与已有文件冲突')
    return task, dirs

def main():
    parser = argparse.ArgumentParser(description='为单个品牌任务建立本地档案目录，不覆盖或移动已有内容。')
    parser.add_argument('--brand-root', required=True, help='已存在、已确认的本品牌工作目录')
    parser.add_argument('--area', required=True, choices=AREAS)
    parser.add_argument('--mode', choices=['work', 'project', 'period'], default='project')
    parser.add_argument('--name', required=True, help='作品或任务名称，不包含路径')
    parser.add_argument('--date', default=dt.date.today().strftime('%Y%m%d'), help='作品日期或周期开始，YYYYMMDD')
    parser.add_argument('--end', help='周期结束，YYYYMMDD')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        task, dirs = build(args.brand_root, args.area, args.mode, args.name, args.date, args.end)
        new_dirs = [str(p) for p in dirs if not p.exists()]
        if not args.dry_run:
            for directory in dirs:
                directory.mkdir(parents=True, exist_ok=True)
        print(json.dumps({'task': str(task), 'directories': [str(p) for p in dirs], 'dry_run': args.dry_run, 'new_directories': new_dirs}, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'无法创建：{exc}\n')

if __name__ == '__main__':
    main()
