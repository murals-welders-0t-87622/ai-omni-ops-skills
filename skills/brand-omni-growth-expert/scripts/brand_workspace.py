"""Initialize a brand workspace and file or find evidence in its private knowledge tree."""
import argparse
from contextlib import contextmanager
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from archive_init import AREAS, CONTENT, CONTENT_SECTIONS, component, is_link_or_junction

REFS = Path(__file__).resolve().parents[1] / 'references'
MARKER = '.omni-brand-id'
PRINCIPLES = '第一性原理'
BRAND_LIBRARIES = ('品牌资料库', 'IP资料库', '产品资料库', '人力资产知识库', '行业与竞品', '增长报告')
KINDS = ('用户资料', '运营方法', '经验与反馈')
TEXT_TYPES = {'.md', '.txt', '.csv', '.json', '.jsonl', '.srt', '.vtt'}


def checked(root, *parts):
    path = root
    for part in parts:
        path = path / component(part)
        if is_link_or_junction(path):
            raise ValueError(f'目录包含链接或重解析点：{path}')
    return path


@contextmanager
def staging(directory):
    directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.omni-writing-', dir=directory)
    os.close(fd)
    temporary = Path(name)
    try:
        yield temporary
    finally:
        temporary.unlink(missing_ok=True)


def publish(staged, destination):
    # Both paths are on the same volume. A competing writer never loses its file.
    try:
        if os.name == 'nt':
            staged.rename(destination)
        else:
            os.link(staged, destination)
        return True
    except FileExistsError:
        return False


def put_new(path, data):
    if path.exists():
        return False
    with staging(path.parent) as temp:
        temp.write_bytes(data)
        return publish(temp, path)


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def workspace(root, brand_id, create):
    root = Path(root).expanduser().absolute()
    if not root.is_dir() or root == Path(root.anchor) or any(is_link_or_junction(p) for p in (root, *root.parents)):
        raise ValueError('请选择已核对的本品牌工作目录')
    marker = checked(root, MARKER)
    expected = (component(brand_id) + '\n').encode()
    if create:
        put_new(marker, expected)
    if not marker.is_file() or marker.read_bytes() != expected:
        raise ValueError('工作区品牌与当前连接不一致，或尚未初始化')
    return root


def sections():
    source = (REFS / 'operating-principles.md').read_text(encoding='utf-8')
    return dict(part.split('\n', 1) for part in source.split('\n## ')[1:])


def initialize(root):
    changes = 0
    for area, (parts, _) in AREAS.items():
        checked(root, *parts).mkdir(parents=True, exist_ok=True)
        if area in CONTENT:
            for section in CONTENT_SECTIONS:
                checked(root, *parts, section).mkdir(parents=True, exist_ok=True)
    for section, principle in sections().items():
        parts = section.split('/')
        group = ('知识库', *parts)
        for kind in (*KINDS, PRINCIPLES):
            checked(root, *group, kind).mkdir(parents=True, exist_ok=True)
        docs = {'经营原理': f'# {section}的经营原理\n\n{principle.strip()}\n'}
        if section == '品牌增长':
            for library in BRAND_LIBRARIES:
                checked(root, *group, library).mkdir(parents=True, exist_ok=True)
            docs['经营原理'] = (REFS / 'brand-growth-first-principles.md').read_text(encoding='utf-8')
            docs['品牌差异化访谈'] = (REFS / 'brand-differentiation.md').read_text(encoding='utf-8')
        for title, content in docs.items():
            data = content.encode()
            revision = hashlib.sha256(data).hexdigest()[:12]
            dest = checked(root, *group, PRINCIPLES, f'{title}-{revision}.md')
            if put_new(dest, data):
                changes += 1
            elif dest.read_bytes() != data:
                raise ValueError(f'本地原理快照有修改，已保留，请核对：{dest}')
    return {'knowledgeRoot': str(root/'知识库'), 'sections': len(sections()), 'newPrincipleFiles': changes}


def file_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(262144), b''):
            digest.update(chunk)
    return digest.hexdigest()


def collect(root, area, subpath, source, origin, kind):
    parts = tuple(subpath.split('/'))
    if any(part in (PRINCIPLES, MARKER) or part.startswith('.') for part in parts):
        raise ValueError('资料需存入业务分类，原理变更由技能维护流程处理')
    if not origin.strip():
        raise ValueError('需要记录资料来源')
    path = Path(source)
    if not path.is_file() or is_link_or_junction(path):
        raise ValueError('资料必须是可读取的文件')
    name = component(path.name)
    if name.startswith('.'):
        raise ValueError('请选择业务资料文件')
    folder = checked(root, '知识库', *area.split('/'), *parts, kind)
    with staging(folder) as temp:
        with path.open('rb') as src, temp.open('wb') as dst:
            shutil.copyfileobj(src, dst)
        digest = file_hash(temp)
        target = checked(folder, f'{path.stem} · {digest[:12]}{path.suffix}')
        if not publish(temp, target) and file_hash(target) != digest:
            raise ValueError('历史版本校验失败，已保留现场')
    origin_id = hashlib.sha256(encode([target.name, origin.strip()])).hexdigest()
    meta = {'file': name, 'sha256': digest, 'origin': origin.strip(), 'kind': kind,
            'recordedAt': dt.datetime.now(dt.timezone.utc).isoformat()}
    receipt = checked(folder, '.source-' + origin_id + '.json')
    put_new(receipt, encode(meta))
    return {'file': str(target.relative_to(root)), 'receipt': str(receipt.relative_to(root)), 'sha256': digest}


def search(root, area, query, limit):
    if not query.strip() or not 1 <= limit <= 200:
        raise ValueError('请输入关键词，结果上限为 1 至 200')
    key = query.strip().casefold()
    base = checked(root, '知识库', *(area.split('/') if area else ()))
    hits = []
    for parent, folders, files in os.walk(base):
        directory = Path(parent)
        folders[:] = sorted(f for f in folders if not f.startswith('.') and not is_link_or_junction(directory/f))
        for name in sorted(files):
            path = directory/name
            if name.startswith('.') or is_link_or_junction(path) or not path.is_file():
                continue
            match = {'file': str(path.relative_to(root))}
            if path.suffix.lower() in TEXT_TYPES:
                with path.open(encoding='utf-8-sig', errors='replace') as stream:
                    for i, line in enumerate(stream, 1):
                        pos = line.casefold().find(key)
                        if pos >= 0:
                            match.update(line=i, excerpt=line[max(0,pos-50):pos+150].strip())
                            break
            if 'line' in match or key in name.casefold():
                hits.append(match)
                if len(hits) == limit:
                    return hits
    return hits


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--brand-root', required=True)
    cli.add_argument('--brand-id', required=True, help='取自当前品牌 MCP')
    commands = cli.add_subparsers(dest='action', required=True)
    commands.add_parser('init')
    add = commands.add_parser('add')
    add.add_argument('--area', choices=sections(), required=True)
    add.add_argument('--category', required=True, help='业务分类，可用 / 追加多层')
    add.add_argument('--file', required=True)
    add.add_argument('--origin', required=True)
    add.add_argument('--kind', choices=KINDS, required=True)
    find = commands.add_parser('search')
    find.add_argument('--area', choices=sections())
    find.add_argument('--query', required=True)
    find.add_argument('--limit', type=int, default=20)
    args = cli.parse_args()
    try:
        root = workspace(args.brand_root, args.brand_id, args.action == 'init')
        if args.action == 'init':
            result = initialize(root)
        elif args.action == 'add':
            result = collect(root, args.area, args.category, args.file, args.origin, args.kind)
        else:
            result = search(root, args.area, args.query, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        cli.exit(2, f'品牌知识库操作未完成：{exc}\n')


if __name__ == '__main__':
    main()
