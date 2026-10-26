"""Install, update, inspect and roll back the managed skill set. Python 3.10+, stdlib only."""
import argparse, datetime, hashlib, json, os, re, shutil, sys, uuid
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
STATE='.omni-skills-state.json'
BACKUPS='.omni-skills-backups'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.tmp');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');t.replace(p)
def digest(d):
    if d.is_symlink():raise ValueError('Symlink target requires manual review')
    if not d.is_dir():return None
    out={}
    for f in sorted(d.rglob('*')):
        if f.is_symlink():raise ValueError('Symlink file requires manual review')
        if not f.is_file() or '__pycache__' in f.parts or f.suffix=='.pyc':continue
        out[f.relative_to(d).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
    return out
def default_target():
    # Follow current documented user scope; explicit --target supports older hosts.
    return Path.home()/'.agents/skills'
def safe_child(base,name):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name):raise ValueError('Invalid skill id')
    p=base/name
    if p.is_symlink() or not p.resolve().is_relative_to(base.resolve()):raise ValueError('Target escapes root')
    return p
def release_check(repo=REPO):
    m=read(repo/'release-manifest.json')
    actual={f.relative_to(repo).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in repo.rglob('*') if f.is_file() and not any(x in {'.git','__pycache__','.omni-skills-backups','.local'} for x in f.relative_to(repo).parts) and f.name not in {'release-manifest.json'} and f.suffix!='.pyc'}
    if actual!=m['files']:raise ValueError('Release hash mismatch; validate and rebuild manifest before install')
    return m
def selection(reg,profile,names):
    rows={r['id']:r for r in reg['skills']};want=set(names or reg['profiles'][profile]);todo=list(want)
    while todo:
        n=todo.pop()
        if n not in rows:raise ValueError('Unknown skill: '+n)
        for dep in rows[n]['dependencies']:
            if dep not in want:want.add(dep);todo.append(dep)
    return [rows[n] for n in sorted(want)]
def check_other_scopes(target,rows):
    candidates=[Path.home()/'.agents/skills',Path.home()/'.codex/skills']
    if target.resolve() not in [p.resolve() for p in candidates]:return []
    warnings=[]
    for c in candidates:
        if c.resolve()==target.resolve():continue
        for r in rows:
            if (c/r['id']/'SKILL.md').exists():warnings.append(str(c/r['id']))
    return warnings
def install(target,profile='all',names=None,dry=False,adopt=False,repo=REPO):
    release=release_check(repo);reg=read(repo/'registry/skills.json');rows=selection(reg,profile,names)
    target=target.expanduser().resolve()
    if target==Path(target.anchor) or target==Path.home().resolve() or target==repo.resolve():raise ValueError('Unsafe install root')
    old=read(target/STATE) if (target/STATE).exists() else {'schemaVersion':1,'skills':{}}
    plans=[]
    for r in rows:
        if not (repo/r['path']).resolve().is_relative_to((repo/'skills').resolve()):raise ValueError('Source path escapes skills root')
        n=r['id'];dest=safe_child(target,n);current=digest(dest);expected=digest(repo/r['path']);prior=old['skills'].get(n)
        if current==expected:action='unchanged'
        elif current is None:action='install'
        elif prior and current==prior['files']:action='update'
        elif not prior and adopt:action='adopt-with-backup'
        else:raise ValueError('Local or unmanaged changes; no files changed: '+n+' (review first; --adopt-existing only for reviewed unmanaged copies)')
        plans.append({'id':n,'action':action,'files':expected,'version':r['version'],'source':r['path']})
    warnings=check_other_scopes(target,rows)
    if warnings and not dry:raise ValueError('Duplicate skills exist in another user scope; choose that existing scope with --target and review: '+', '.join(warnings))
    if dry:return {'dryRun':True,'target':str(target),'plan':[{k:v for k,v in p.items() if k not in {'files'}} for p in plans],'otherScopeDuplicates':warnings}
    changes=[p for p in plans if p['action']!='unchanged']
    # First-time unchanged adoption still needs an ownership receipt for future safe updates.
    if not changes and all(p['id'] in old['skills'] for p in plans):return {'status':'unchanged','target':str(target)}
    tid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    backup=target/BACKUPS/tid;backup.mkdir(parents=True)
    journal={'schemaVersion':1,'id':tid,'status':'preparing','before':old,'after':json.loads(json.dumps(old)),'changed':[],'release':release['version']}
    write(backup/'transaction.json',journal)
    try:
        for p in changes:
            n=p['id'];stage=backup/'staged'/n;stage.parent.mkdir(exist_ok=True)
            shutil.copytree(repo/p['source'],stage,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            if digest(stage)!=p['files']:raise ValueError('Staged copy mismatch: '+n)
        for p in plans:journal['after']['skills'][p['id']]={'version':p['version'],'files':p['files'],'release':release['version']}
        journal['status']='applying';write(backup/'transaction.json',journal)
        for p in changes:
            n=p['id'];dest=safe_child(target,n);had=dest.exists()
            journal['changed'].append({'id':n,'hadPrevious':had,'installedFiles':p['files'],'phase':'pending'})
            write(backup/'transaction.json',journal)
            if had:
                prev=backup/'previous'/n;prev.parent.mkdir(exist_ok=True);dest.rename(prev)
            (backup/'staged'/n).rename(dest)
            journal['changed'][-1]['phase']='done';write(backup/'transaction.json',journal)
        write(target/STATE,journal['after']);journal['status']='complete';write(backup/'transaction.json',journal)
    except BaseException:
        rollback(target,tid,recover=True)
        raise
    return {'status':'installed','transaction':tid,'target':str(target),'changed':len(changes),'skills':len(plans)}
def rollback(target,tid,recover=False):
    target=target.expanduser().resolve()
    if not re.fullmatch(r'[A-Za-z0-9T-]+',tid):raise ValueError('Invalid transaction id')
    b=target/BACKUPS/tid
    if b.is_symlink() or not b.resolve().is_relative_to((target/BACKUPS).resolve()):raise ValueError('Unsafe transaction path')
    j=read(b/'transaction.json')
    if j['status']=='rolled-back':return {'status':'already-rolled-back'}
    if not recover and read(target/STATE)!=j['after']:raise ValueError('Newer installation state exists; roll back newest transaction first')
    for c in j['changed']:
        d=safe_child(target,c['id']);cur=digest(d)
        if cur is not None and cur!=c['installedFiles']:
            # pending entry may still hold untouched original files.
            old=j['before']['skills'].get(c['id'],{}).get('files')
            if not (recover and c['phase']=='pending' and not (b/'previous'/c['id']).exists()):raise ValueError('Rollback would overwrite local changes: '+c['id'])
    for c in reversed(j['changed']):
        d=safe_child(target,c['id']);prev=b/'previous'/c['id']
        if c['phase']=='pending' and c['hadPrevious'] and not prev.exists():continue
        if d.exists():
            retained=b/'rolled-forward'/c['id'];retained.parent.mkdir(exist_ok=True);d.rename(retained)
        if prev.exists():prev.rename(d)
    write(target/STATE,j['before']);j['status']='rolled-back';write(b/'transaction.json',j)
    return {'status':'rolled-back','transaction':tid}
def doctor(target,repo=REPO):
    release_check(repo);reg=read(repo/'registry/skills.json');state=read(target/STATE) if (target/STATE).exists() else {'skills':{}}
    rows=[]
    for r in reg['skills']:
        current=digest(safe_child(target,r['id']));owned=state['skills'].get(r['id'])
        rows.append({'id':r['id'],'status':'missing' if current is None else ('current' if current==digest(repo/r['path']) else ('managed-older' if owned and current==owned['files'] else 'local-changes'))})
    return {'target':str(target),'skills':rows,'tools':{n:bool(shutil.which(n)) for n in ['python','git','gh','node','ffmpeg']},'businessConnections':'Not probed; install success is not MCP readiness or business acceptance.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['install','doctor','rollback']);p.add_argument('--target',type=Path,default=default_target());p.add_argument('--profile',default='all');p.add_argument('--skill',action='append');p.add_argument('--dry-run',action='store_true');p.add_argument('--adopt-existing',action='store_true');p.add_argument('--transaction')
    a=p.parse_args()
    try:
        if a.command=='install':out=install(a.target,a.profile,a.skill,a.dry_run,a.adopt_existing)
        elif a.command=='doctor':out=doctor(a.target)
        else:
            if not a.transaction:p.error('--transaction required')
            out=rollback(a.target,a.transaction)
        print(json.dumps(out,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError) as e:print(str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
