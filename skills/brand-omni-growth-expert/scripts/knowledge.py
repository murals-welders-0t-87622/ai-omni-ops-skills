"""Read-only search/read over the packaged expert library; no external requests."""
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'references/knowledge'

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('search');q.add_argument('--query',default='');q.add_argument('--package',default='');q.add_argument('--limit',type=int,default=8)
    r=s.add_parser('read');r.add_argument('--path',required=True);r.add_argument('--start',type=int,default=1);r.add_argument('--lines',type=int,default=100)
    s.add_parser('packages');a=p.parse_args()
    if a.cmd=='packages':print((ROOT/'references/source-packages.json').read_text(encoding='utf-8'));return
    if a.cmd=='read':
        f=(LIB/a.path).resolve()
        if not f.is_relative_to(LIB.resolve()) or not f.is_file():p.error('Path must be an existing file inside knowledge')
        ls=f.read_text(encoding='utf-8').splitlines();start=max(a.start,1)
        print('\n'.join(f'{i+1}: {v}' for i,v in enumerate(ls) if start-1<=i<start-1+min(max(a.lines,1),300)));return
    hits=[]
    for f in LIB.rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(LIB).as_posix()
        if a.package and a.package.lower() not in rel.lower():continue
        ls=f.read_text(encoding='utf-8',errors='replace').splitlines()
        ix=[i for i,l in enumerate(ls) if a.query.lower() in l.lower()][:2]
        if ix:hits.append({'path':rel,'lines':[{'line':i+1,'text':ls[i][:250]} for i in ix]})
        if len(hits)>=min(max(a.limit,1),30):break
    print(json.dumps(hits,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
