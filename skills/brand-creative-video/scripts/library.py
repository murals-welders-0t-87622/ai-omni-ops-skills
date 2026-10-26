#!/usr/bin/env python3
"""离线检索；所有正文保留，输出窗口不改变来源。"""
from pathlib import Path
import argparse,json,re,sys

SKILL=Path(__file__).resolve().parents[1]
def emit(x):print(json.dumps(x,ensure_ascii=False,indent=2))
def docs():return json.loads((SKILL/'references/document-index.json').read_text(encoding='utf-8'))['files']
def cases():
    with (SKILL/'references/case-index.jsonl').open(encoding='utf-8') as f:
        for line in f:
            if line.strip():yield json.loads(line)
def tokens(s):return [x.lower() for x in re.split(r'\s+',s.strip()) if x]
def score(text,words):
    text=text.lower();return sum(min(text.count(w),30) for w in words)
def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['search','docs']:
        q=sub.add_parser(name);q.add_argument('--query',default='');q.add_argument('--stage');q.add_argument('--model');q.add_argument('--limit',type=int,default=10)
    q=sub.add_parser('read');q.add_argument('--id',required=True);q.add_argument('--start',type=int,default=1);q.add_argument('--lines',type=int,default=160)
    a=p.parse_args()
    if a.command=='read':
        item=next((x for x in docs() if x['id']==a.id),None)
        if item:
            text=(SKILL/item['path']).read_text(encoding='utf-8-sig');meta={'id':a.id,'sourcePath':item['path'],'totalSourceLines':item['lines']}
        else:
            item=next((x for x in cases() if x['id']==a.id),None)
            if not item:raise ValueError('Unknown reference ID')
            text=item['text'];meta={k:v for k,v in item.items() if k!='text'}
        rows=text.splitlines();start=max(1,a.start);end=min(len(rows),start+max(1,a.lines)-1)
        emit({**meta,'window':[start,end],'totalRecordLines':len(rows),'hasMore':end<len(rows),'content':'\n'.join(f'{i+1}: {rows[i]}' for i in range(start-1,end))});return
    words=tokens(a.query);out=[]
    source=docs() if a.command=='docs' else cases()
    for x in source:
        if a.command=='docs':
            if a.stage and a.stage not in x['stages']:continue
            text=x['path']+' '+json.dumps(x['headings'],ensure_ascii=False)
        else:
            text=x['title']+' '+x['text']
            if a.model and a.model.lower() not in str(x.get('model','')).lower():continue
        points=score(text,words)
        if words and not points:continue
        row={k:v for k,v in x.items() if k not in ['text','headings']};row['score']=points
        if a.command=='docs':row['matchingSections']=[h for h in x['headings'] if not words or score(h['title'],words)][:12]
        else:
            low=text.lower();pos=min([low.find(w) for w in words if w in low] or [0]);row['matchExcerpt']=text[max(0,pos-70):pos+220]
        out.append(row)
    out.sort(key=lambda x:(-x['score'],x['id']));emit({'matches':len(out),'returned':min(len(out),max(1,a.limit)),'items':out[:max(1,a.limit)],'note':'仅定位，不替代原文；用read读取全文或后续窗口。'})
if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as e:print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
