"""Append project-scoped routing guidance without replacing user instructions."""
import argparse
from pathlib import Path

START = '<!-- omni-growth-routing:start -->'
END = '<!-- omni-growth-routing:end -->'
BLOCK = '''<!-- omni-growth-routing:start -->
## AI 品牌增长业务技能

处理本工作区的品牌增长业务时，依据用户目标及当前品牌上下文，先使用品牌全域增长总统筹，再按实际环节选择对应领域技能；不要要求用户手动指定每项技能。用户只要求选题时交付选题；要求视频成片时，从平台运营衔接创意制作调度和匹配的视频技能，检查真实产物并按品牌归档。按用户已授权的范围执行；缺少必要能力或证据时如实报告，不将文档或计划当作成片。
<!-- omni-growth-routing:end -->'''

def configure(workspace):
    workspace = Path(workspace).expanduser().resolve(strict=True)
    if not workspace.is_dir() or workspace == Path(workspace.anchor):
        raise ValueError('请选择实际业务工作区目录')
    path = workspace / 'AGENTS.md'
    if path.is_symlink():
        raise ValueError('AGENTS.md 是符号链接，需先核对目标')
    existing = path.read_text(encoding='utf-8-sig') if path.exists() else ''
    if START in existing or END in existing:
        if START not in existing or END not in existing:
            raise ValueError('现有路由标记不完整；保留文件并人工检查')
        return 'existing', path
    # Exclusive creation prevents accidental overwrite when a file appears concurrently.
    if not path.exists():
        with path.open('x', encoding='utf-8', newline='\n') as f: f.write(BLOCK + '\n')
    else:
        # Preserve original bytes and use append only; never replace existing guidance.
        with path.open('ab') as f: f.write((('\n\n' if not existing.endswith('\n\n') else '') + BLOCK + '\n').encode('utf-8'))
    return 'added', path

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('workspace', help='用户实际开展品牌业务的工作区')
    args=parser.parse_args()
    try:
        status,path=configure(args.workspace)
        print(f'{status}: {path}')
    except (OSError,ValueError) as exc:
        parser.exit(1, f'{exc}\n')
