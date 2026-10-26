from pathlib import Path
import hashlib,json,re,sys

BASE=Path(__file__).resolve().parents[1]

def verify():
    errors=[]
    index=json.loads((BASE/'references/library/index.json').read_text(encoding='utf-8'))
    ids=set()
    for x in index:
        if x['source_id'] in ids:errors.append('duplicate source ID')
        ids.add(x['source_id']);p=(BASE/x['text_file']).resolve()
        if not p.is_relative_to(BASE) or not p.is_file():errors.append('missing/unsafe source '+x['source_id']);continue
        if hashlib.sha256(p.read_bytes()).hexdigest()!=x['text_sha256']:errors.append('source hash mismatch '+x['source_id'])
    links=0
    for md in BASE.rglob('*.md'):
        # Library raw texts are .txt, not executable instructions or package navigation.
        text=md.read_text(encoding='utf-8')
        for ref in re.findall(r'\]\(([^)]+)\)',text):
            if ref.startswith(('http:','https:','mailto:','#')) or '<' in ref:continue
            path=ref.split('#')[0]
            target=(md.parent/path).resolve();links+=1
            if not target.is_relative_to(BASE) or not target.exists():errors.append(str(md.relative_to(BASE))+': broken '+ref)
    for md in (BASE/'SKILL.md',*list((BASE/'references').glob('0*.md'))):
        for sid in re.findall(r'\bS[0-9a-f]{12}\b',md.read_text(encoding='utf-8')):
            if sid not in ids:errors.append('unknown cited source '+sid)
    result={'passed':not errors,'sources':len(index),'links_checked':links,'errors':errors}
    print(json.dumps(result,ensure_ascii=False,indent=2));return result

if __name__=='__main__':sys.exit(0 if verify()['passed'] else 1)
