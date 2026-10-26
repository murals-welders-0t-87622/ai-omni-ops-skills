"""Refresh indexes of our own public method files; does not change architecture or external evidence."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    p=R/'registry/source-files.json';rows=json.loads(p.read_text(encoding='utf-8'))
    for row in rows:
        f=R/row['path']
        if not f.is_file():raise ValueError('Source card missing: '+row['path'])
        row['sha256']=h(f)
    write(p,rows);write(R/'skills/brand-omni-growth-expert/references/source-files.json',rows)
    bc=R/'skills/brand-content-growth';rows=[]
    for f in sorted((bc/'references').glob('[0-9]*.md')):
        dst=bc/'references/library/texts'/f.name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(f.read_bytes())
        rows.append({'source_id':'METHOD-'+f.stem.split('-')[0],'source_path':f.name,'text_file':dst.relative_to(bc).as_posix(),'text_sha256':h(dst),'chars':len(f.read_text(encoding='utf-8')),'reading_note':'本仓通用方法整理，不是原课程全文；引用外部原文需另行取得并核读。','source_kind':'original-method-synthesis'})
    write(bc/'references/library/index.json',rows)
    cv=R/'skills/brand-creative-video';docs=[]
    for f in sorted((cv/'references').glob('*.md')):
        s=f.read_text(encoding='utf-8');docs.append({'id':'DOC-'+hashlib.sha256(f.name.encode()).hexdigest()[:12],'path':f.relative_to(cv).as_posix(),'stages':['research','story','storyboard','assets','prompt','review'],'bytes':f.stat().st_size,'sha256':h(f),'lines':len(s.splitlines()),'headings':[{'line':i+1,'title':x.lstrip('# ')} for i,x in enumerate(s.splitlines()) if x.startswith('#')]})
    write(cv/'references/document-index.json',{'files':docs,'distribution':'curated-public-methods; original private/third-party texts not redistributed'})
    print(json.dumps({'publicSourceCards':len(json.loads(p.read_text(encoding='utf-8'))),'contentMethods':len(rows),'creativeMethods':len(docs)},ensure_ascii=False))
if __name__=='__main__':main()
