"""Validate installed entry points, dependency closure, source coverage and release integrity."""
import argparse, ast, hashlib, json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IGNORE={'.git','__pycache__','.local','.omni-skills-backups'}
def files(root=ROOT):
    return [p for p in root.rglob('*') if p.is_file() and not any(x in IGNORE for x in p.relative_to(root).parts) and p.suffix!='.pyc' and p.name!='release-manifest.json']
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root=ROOT):return {'schemaVersion':1,'version':json.loads((root/'registry/skills.json').read_text(encoding='utf-8'))['version'],'files':{p.relative_to(root).as_posix():h(p) for p in sorted(files(root))}}
def architecture_errors(reg,lock):
    errors=[]
    expected={'layers':lock['layers'],'businessFlow':lock['businessFlow']}
    if reg.get('businessFramework')!=expected:errors.append('Business framework changed; obtain user confirmation before updating architecture-lock')
    actual={r['id']:{k:r[k] for k in ['path','kind','dependencies']} for r in reg['skills']}
    fixed={r['id']:{k:r[k] for k in ['path','kind','dependencies']} for r in lock['skills']}
    if actual!=fixed:errors.append('Skill roles, paths, dependencies or entry set changed; user-confirmed architecture decision required')
    return errors
def validate(root=ROOT):
    reg=json.loads((root/'registry/skills.json').read_text(encoding='utf-8')); rows={r['id']:r for r in reg['skills']};errors=[];references=[]
    if len(rows)!=len(reg['skills']):errors.append('Duplicate registry skills')
    lock=json.loads((root/'registry/architecture-lock.json').read_text(encoding='utf-8'))
    errors+=architecture_errors(reg,lock)
    discovered={p.parent.name for p in (root/'skills').rglob('SKILL.md')}
    if discovered!=set(rows):errors.append('Unexpected or missing nested SKILL.md entrypoints')
    def visit(n,stack=()):
        if n in stack:errors.append('Dependency cycle: '+n);return
        if n not in rows:errors.append('Missing dependency: '+n);return
        for dep in rows[n]['dependencies']:visit(dep,stack+(n,))
    for n,r in rows.items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',n):errors.append('Invalid name: '+n)
        d=(root/r['path']).resolve()
        if not d.is_relative_to((root/'skills').resolve()):errors.append('Path escape: '+n);continue
        f=d/'SKILL.md';s=f.read_text(encoding='utf-8') if f.exists() else '';visit(n)
        if not re.match(r'---\s*\nname:\s*'+re.escape(n)+r'\s*\n',s) or not re.search(r'^description:\s*\S',s,re.M):errors.append('Invalid frontmatter: '+n)
        if not (d/'agents/openai.yaml').exists():errors.append('Missing UI metadata: '+n)
        if 'allow_implicit_invocation: false' in (d/'agents/openai.yaml').read_text(encoding='utf-8'):errors.append('Implicit selection disabled: '+n)
        # Entry points must have usable local references. Source archives keep their original absent media links.
        checks=[f]
        if n=='brand-omni-growth-expert':checks+=list((d/'references').glob('*.md'))
        for md in checks:
            for raw in re.findall(r'\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
                raw=raw.strip('<>').split('#')[0]
                if not raw or re.match(r'[a-z]+://|mailto:',raw):continue
                dest=(md.parent/raw).resolve()
                if not dest.is_relative_to((root/'skills').resolve()) or not dest.exists():errors.append('Broken entry link: '+md.relative_to(root).as_posix()+' -> '+raw)
        for py in (d/'scripts').glob('*.py'):
            try:ast.parse(py.read_text(encoding='utf-8-sig'))
            except SyntaxError as e:errors.append('Invalid Python '+str(py)+': '+str(e))
    sources=json.loads((root/'registry/source-files.json').read_text(encoding='utf-8'))
    for r in sources:
        if r['disposition']!='reference-only':continue
        f=root/r['path']
        if not f.exists() or h(f)!=r['sha256']:errors.append('Source coverage/hash mismatch: '+r['source'])
    active=json.loads((root/'registry/active-source-files.json').read_text(encoding='utf-8'))
    for r in active:
        f=root/r['path']
        if not f.exists() or h(f)!=r['sha256']:errors.append('Adapted active-source hash mismatch: '+r['path'])
    learning=json.loads((root/'registry/learning-sources.json').read_text(encoding='utf-8'))
    ids=set()
    for item in learning['sources']:
        if item['id'] in ids:errors.append('Duplicate learning source: '+item['id'])
        ids.add(item['id'])
        if not item.get('coverage') or not item.get('status'):errors.append('Missing reading coverage or status: '+item['id'])
        for path in item.get('adoptions',[]):
            f=(root/path).resolve()
            if not f.is_relative_to(root.resolve()) or not f.is_file():errors.append('Invalid learning adoption target: '+item['id'])
    # Only names/line numbers are reported, never secret values.
    patterns=[('credential',r'\b(?:ocp_|gh[pousr]_|github_pat_|sk-proj-)[A-Za-z0-9_-]{16,}'),('bearer',r'(?i)Bearer\s+[A-Za-z0-9_.-]{24,}'),('private-key',r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----'),('url-password',r'https?://[^\s/@:]+:[^\s/@]+@')]
    for f in files(root):
        if f.suffix.lower() not in {'.md','.txt','.json','.jsonl','.yaml','.yml','.py','.ps1','.js','.mjs','.toml','.vue','.ts','.tsx','.html','.env','.ini','.php'}:continue
        s=f.read_text(encoding='utf-8-sig',errors='replace')
        for kind,pat in patterns:
            if re.search(pat,s):errors.append('Sensitive pattern '+kind+': '+f.relative_to(root).as_posix())
    return {'skills':len(rows),'publicSourceCards':len(sources),'learningSources':len(ids),'architecture':'preserved' if not architecture_errors(reg,lock) else 'changed','releaseFiles':len(files(root)),'errors':errors}
def main():
    p=argparse.ArgumentParser();p.add_argument('--write-manifest',action='store_true');a=p.parse_args();out=validate()
    if out['errors']:print(json.dumps(out,ensure_ascii=False,indent=2));return 1
    m=manifest()
    if a.write_manifest:(ROOT/'release-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    else:
        old=json.loads((ROOT/'release-manifest.json').read_text(encoding='utf-8')) if (ROOT/'release-manifest.json').exists() else None
        if old!=m:out['errors'].append('Release manifest differs; review changes then use --write-manifest')
    print(json.dumps(out,ensure_ascii=False,indent=2));return bool(out['errors'])
if __name__=='__main__':raise SystemExit(main())
