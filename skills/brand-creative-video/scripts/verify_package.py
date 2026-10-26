#!/usr/bin/env python3
"""Verify only the actual public package; private source coverage is not inherited."""
from pathlib import Path
import json,hashlib,re,sys

SKILL=Path(__file__).resolve().parents[1]
def verify(root=SKILL):
    root=Path(root);errors=[]
    for path in ['SKILL.md','agents/openai.yaml','scripts/project.py','scripts/library.py','scripts/prepare_request.py','references/source-manifest.json','references/document-index.json','references/case-index.jsonl','assets/examples/demo-two/seed.json']:
        if not (root/path).is_file():errors.append('Missing '+path)
    idx=json.loads((root/'references/document-index.json').read_text(encoding='utf-8'))
    for item in idx['files']:
        p=(root/item['path']).resolve()
        if not p.is_relative_to(root.resolve()) or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:errors.append('Method hash mismatch '+item['path'])
    for p in [root/'SKILL.md',*(root/'references').glob('*.md')]:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if re.match(r'^(https?:|#|mailto:)',link):continue
            dest=(p.parent/link.split('#')[0]).resolve()
            if not dest.exists():errors.append('Broken reference '+str(p.relative_to(root))+' -> '+link)
    cases=[json.loads(line) for line in (root/'references/case-index.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    if len({c['id'] for c in cases})!=len(cases):errors.append('Duplicate case IDs')
    for c in cases:
        if not (root/c['sourcePath']).is_file() or not c['text'].strip():errors.append('Invalid case locator '+c['id'])
    return {'valid':not errors,'errors':errors,'distribution':'public-methods','indexed_documents':len(idx['files']),'indexed_cases':len(cases),'note':'Own method/engineering checks; no private original-text coverage or real media acceptance implied.'}
if __name__=='__main__':
    result=verify();print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(0 if result['valid'] else 1)
