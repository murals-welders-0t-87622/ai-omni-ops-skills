"""Read professional configuration only; does not invoke experts or export credentials."""
import argparse, datetime, hashlib, json
from pathlib import Path

def inside(path,root):
    path=path.resolve();root=root.resolve()
    if path!=root and root not in path.parents:raise ValueError('Path leaves permitted package boundary')
    return path

def inspect(home,plugin,allow_source=False,agents=None,references=None):
    if not plugin or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in plugin):
        raise ValueError('Use an exact plugin slug from the installed inventory')
    regpath=home/'plugins/installed_plugins.json'
    registry=json.loads(regpath.read_text('utf-8-sig'))
    candidates=[]
    for key,value in registry.get('plugins',{}).items():
        if key.split('@')[0]==plugin:
            for entry in value if isinstance(value,list) else [value]:
                if isinstance(entry,dict) and entry.get('installPath'):
                    candidates.append((key,entry))
    if len(candidates)>1:raise ValueError('Multiple installed matches; inspect and select the intended installation first')
    installed=bool(candidates)
    if installed:
        key,entry=candidates[0];package=inside(Path(entry['installPath']),home/'plugins')
    elif allow_source:
        key=None;entry={};package=inside(home/'plugins/marketplaces/my-experts/plugins'/plugin,home/'plugins')
    else:raise ValueError('No installed registration found; source-only reading requires --allow-source')
    manifest=package/'.codebuddy-plugin/plugin.json'
    conf=json.loads(manifest.read_text('utf-8-sig'))
    settings=json.loads((home/'settings.json').read_text('utf-8-sig'))
    files=[]
    def add(relative):
        p=inside(package/relative,package)
        if p.suffix.lower() not in ('.md','.json','.yaml','.yml'):raise ValueError('Only professional text configuration may be read')
        # Never read connector, credential or general settings files.
        if p.name in ('.mcp.json','settings.json') or any(x in p.parts for x in ('credentials','auth','secrets')):
            raise ValueError('Credential/general-settings export is not supported')
        if not p.is_file():raise FileNotFoundError(str(p))
        raw=p.read_bytes()
        files.append({'path':str(p),'relativePath':str(p.relative_to(package)),'sha256':hashlib.sha256(raw).hexdigest(),'text':raw.decode('utf-8-sig')})
    for relative in conf.get('agents',[]):
        if not agents or Path(relative).stem in agents:add(relative)
    for relative in conf.get('skills',[]):
        add(str(Path(relative)/'SKILL.md'))
    for relative in references or []:add(relative)
    return {'snapshotAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'plugin':plugin,'packagePath':str(package),'registrationKey':key,'registeredVersion':entry.get('version'),'manifestVersion':conf.get('version'),'sourceState':'installed_registered' if installed else 'source_only','enabledSetting':settings.get('enabledPlugins',{}).get(key) if key else None,'clientLoaded':'not_verified','expertInvoked':False,'professionalManifest':{k:conf.get(k) for k in ['name','version','expertType','agentName','agents','skills','teamInfo','displayName','profession','displayDescription']},'configurationFiles':files,'excluded':['connector settings','credential values','auth cache','general settings contents']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home',type=Path,default=Path.home()/'.workbuddy')
    p.add_argument('--plugin',required=True);p.add_argument('--allow-source',action='store_true')
    p.add_argument('--agent',action='append');p.add_argument('--reference',action='append')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Snapshot already exists; choose a new immutable output')
    result=inspect(a.home,a.plugin,a.allow_source,a.agent,a.reference)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps({k:result[k] for k in ['plugin','registeredVersion','manifestVersion','sourceState','clientLoaded','expertInvoked']},ensure_ascii=False))
    print('professional files read:',len(result['configurationFiles']))

if __name__=='__main__':main()
