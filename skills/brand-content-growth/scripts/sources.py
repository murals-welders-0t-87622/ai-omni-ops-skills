"""Read-only source retrieval. Does not execute instructions embedded in sources."""
from pathlib import Path
import argparse, json, re, sys

BASE = Path(__file__).resolve().parents[1]

def rows():
    return json.loads((BASE/'references/library/index.json').read_text(encoding='utf-8'))

def safe_path(ref):
    p=(BASE/ref).resolve()
    if not p.is_relative_to(BASE.resolve()):raise ValueError('source path outside skill')
    return p

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('search');s.add_argument('--query',required=True);s.add_argument('--group');s.add_argument('--limit',type=int,default=8)
    l=sub.add_parser('list');l.add_argument('--group');l.add_argument('--limit',type=int,default=30)
    r=sub.add_parser('read');r.add_argument('--id',required=True);r.add_argument('--start',type=int,default=1);r.add_argument('--lines',type=int,default=100)
    a=p.parse_args();items=rows()
    if a.cmd=='read':
        row=next((x for x in items if x['source_id']==a.id),None)
        if not row:raise ValueError('unknown source ID')
        if a.start<1 or not 1<=a.lines<=300:raise ValueError('start >= 1; lines 1..300')
        lines=safe_path(row['text_file']).read_text(encoding='utf-8').splitlines()
        print(json.dumps({'source_id':row['source_id'],'source_path':row['source_path'],'total_lines':len(lines),'reading_note':row['reading_note']},ensure_ascii=False))
        for i,line in enumerate(lines[a.start-1:a.start-1+a.lines],a.start):print(f'{i}: {line}')
        return
    if not 1<=a.limit<=100:raise ValueError('limit 1..100')
    if a.group:items=[x for x in items if a.group.casefold() in x['source_path'].casefold()]
    if a.cmd=='list':
        print(json.dumps([{'source_id':x['source_id'],'source_path':x['source_path'],'chars':x['chars']} for x in items[:a.limit]],ensure_ascii=False,indent=2));return
    terms=[t.casefold() for t in re.split(r'\s+',a.query.strip()) if t]
    if not terms:raise ValueError('empty query')
    matches=[]
    for x in items:
        raw=safe_path(x['text_file']).read_text(encoding='utf-8');s=raw.casefold();path=x['source_path'].casefold()
        hit=[t for t in terms if t in s or t in path]
        if not hit:continue
        positions=[s.find(t) for t in hit if t in s];pos=min(positions) if positions else 0
        score=len(hit)*10+sum(4 for t in terms if t in path)
        matches.append((score,{'source_id':x['source_id'],'source_path':x['source_path'],'match_line':raw[:pos].count('\n')+1,'snippet':raw[max(0,pos-80):pos+260],'matched_terms':hit}))
    matches.sort(key=lambda v:(-v[0],v[1]['source_path']))
    print(json.dumps([x[1] for x in matches[:a.limit]],ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,FileNotFoundError) as e:print(str(e),file=sys.stderr);sys.exit(2)
