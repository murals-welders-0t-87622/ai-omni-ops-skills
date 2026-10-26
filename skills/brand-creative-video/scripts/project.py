#!/usr/bin/env python3
"""本地品牌视频工程管理；绝不自行调用生成供应商。"""
from pathlib import Path
from contextlib import contextmanager
import argparse,datetime,hashlib,json,os,re,shutil,sys,uuid

SKILL=Path(__file__).resolve().parents[1]
ACTIVE={'reserved','submitted','queued','running','outcome_unknown'}
STATES={'submitted','queued','running','generated','reviewed','failed','outcome_unknown'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def save(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(tmp,path)
def emit(x):print(json.dumps(x,ensure_ascii=False,indent=2))
def within(root,value):
    root=Path(root).resolve();p=Path(value);p=(root/p).resolve() if not p.is_absolute() else p.resolve()
    if not p.is_relative_to(root):raise ValueError('Path must stay within project: '+str(value))
    return p
def load(root):
    root=Path(root).resolve();return root,read(root/'project.json'),read(root/'assets/assets.json'),read(root/'storyboard/shots.json')
def events(root):
    path=root/'runs/events.jsonl'
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()] if path.exists() else []
def append(root,obj):
    with (root/'runs/events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(obj,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
@contextmanager
def locked(root):
    p=root/'state/.write-lock'
    try:fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    except FileExistsError:raise ValueError('Project locked. Reconcile current writer/unfinished checkpoint; do not blindly remove lock or resubmit.')
    try:
        os.write(fd,json.dumps({'pid':os.getpid(),'time':now()}).encode());os.close(fd);yield
    finally:p.unlink(missing_ok=True)
def init(root,brand,title,max_seconds,example=None):
    root=Path(root).resolve()
    if max_seconds<=0:raise ValueError('Maximum duration must be positive')
    if root.exists() and any(root.iterdir()):raise ValueError('Nonempty project directory; resume or choose a new directory')
    for p in ['research','brief','scripts','assets/characters','assets/scenes','assets/props','assets/logos','assets/keyframes','storyboard/prompts','runs/requests','runs/responses','runs/raw','edit','exports','qa','state']:(root/p).mkdir(parents=True,exist_ok=True)
    project={'schema_version':'1.0','project_id':'prj_'+uuid.uuid4().hex,'created_at':now(),'brand':brand,'title':title,'stage':'script-review','delivery':{'max_seconds':max_seconds,'aspect_ratio':'9:16','width':1080,'height':1920,'fps':24},'authorization':{'generation':{'allowed':False,'providers':[],'max_jobs':0,'max_retries_per_shot':0,'evidence':None},'publish':{'allowed':False}},'episodes':[],'provider_profile':'brief/provider-profile.json','runtime_schema_evidence':None}
    assets=[];shots=[]
    if example:
        seed=read(SKILL/'assets/examples'/example/'seed.json');assets=seed['assets'];shots=seed['shots'];project['episodes']=seed['episodes'];project['sample_status']='工程演练样例，未生成媒体，不代表用户批准'
        for e in project['episodes']:
            if e['duration']>max_seconds:raise ValueError('Example exceeds requested maximum duration')
        shutil.copyfile(SKILL/'assets/examples'/example/'scripts.json',root/'scripts/review-r1.json')
    save(root/'project.json',project);save(root/'assets/assets.json',assets);save(root/'storyboard/shots.json',shots)
    shutil.copyfile(SKILL/'references/provider-profiles/runninghub-seedance-mini.json',root/'brief/provider-profile.json')
    save(root/'research/reference-ledger.json',[])
    save(root/'edit/timeline.json',{'version':'r1','episodes':[{'id':e['id'],'duration':e['duration'],'clips':[{'shot_id':s['id'],'start':s['start'],'end':s['end'],'source':None,'source_in':(s.get('trim') or {}).get('in',0),'source_out':(s.get('trim') or {}).get('out'),'source_sha256':None} for s in shots if s['episode_id']==e['id']]} for e in project['episodes']]})
    (root/'runs/events.jsonl').touch()
    for s in shots:
        save(root/'storyboard/prompts'/(s['id']+'-r1.json'),{'shot_id':s['id'],'status':'draft','reference_assets':s.get('asset_refs',[]),'keyframe_id':s.get('keyframe_id'),'image_prompt':s.get('image_prompt'),'video_prompt':s.get('prompt'),'audio':s.get('audio'),'note':'图片待生成/审核；这些是实际镜头计划与原创提示词，不是供应商执行回执'})
    save(root/'state/checkpoint.json',{'time':now(),'stage':'script-review','verified':['工程已创建','样例仅文字资产计划'] if example else ['工程已创建'],'pending':['用户本次要推进的制作阶段','资产文件与视觉审核','当前工具schema与生成范围'],'next':'回读项目与脚本，按用户授权推进；不自动生成'})
    return {'root':str(root),'project_id':project['project_id'],'episodes':len(project['episodes']),'assets':len(assets),'shots':len(shots),'media_generated':False}
def validate(root,for_generation=False,shot_id=None):
    root,p,assets,shots=load(root);errors=[];warnings=[];am={a['id']:a for a in assets};sm={s['id']:s for s in shots};em={e['id']:e for e in p['episodes']}
    profile=read(within(root,p['provider_profile']))
    if len(am)!=len(assets):errors.append('Duplicate asset IDs')
    if len(sm)!=len(shots):errors.append('Duplicate shot IDs')
    if not em:warnings.append('No episodes yet; add script and shot plan before production')
    selected=[sm[shot_id]] if shot_id in sm else shots
    if shot_id and shot_id not in sm:errors.append('Unknown shot ID: '+shot_id)
    for e in em.values():
        ss=sorted([s for s in shots if s['episode_id']==e['id']],key=lambda s:s['start'])
        last=0
        for s in ss:
            if abs(s['start']-last)>.0001:errors.append(f'{e["id"]}: timeline gap/overlap at {s["id"]}')
            if s['end']<=s['start']:errors.append(s['id']+': nonpositive duration')
            last=s['end']
        if abs(last-e['duration'])>.0001:errors.append(e['id']+': duration mismatch')
        if e['duration']>p['delivery']['max_seconds']+.0001:errors.append(e['id']+': exceeds maximum including end card')
    for s in selected:
        sid=s['id']
        if s['episode_id'] not in em:errors.append(sid+': unknown episode')
        refs=list(s.get('asset_refs',[]))+([s['keyframe_id']] if s.get('keyframe_id') else [])
        for ref in refs:
            if ref not in am:errors.append(sid+': unknown asset '+ref)
        for key in ['entry_state','action','camera','exit_state','audio']:
            if not s.get(key):errors.append(sid+': missing '+key)
        if s.get('kind')=='generated':
            if not s.get('prompt') or not s.get('image_prompt'):errors.append(sid+': missing image/video prompt')
            if not s.get('keyframe_id'):errors.append(sid+': missing keyframe binding')
            duration=s.get('generation_duration',0);trim=s.get('trim',{})
            if duration not in profile.get('durationSeconds',[]):errors.append(sid+': requested duration outside selected provider capability')
            if not (0<=trim.get('in',-1)<trim.get('out',0)<=duration):errors.append(sid+': invalid trim range')
            if abs((trim.get('out',0)-trim.get('in',0))-(s['end']-s['start']))>.001:errors.append(sid+': edit duration differs from trim')
            if not profile.get('supportsMultiImageReferences') and re.search(r'@(图片|图|image)\s*[2-9]',s.get('prompt',''),re.I):errors.append(sid+': single-image profile cannot receive extra reference slots')
            if for_generation and em.get(s['episode_id'],{}).get('script_status')!='approved':errors.append(sid+': script not approved within current scope')
            if for_generation:
                for ref in refs:
                    a=am.get(ref)
                    if not a:continue
                    if a.get('status')!='approved':errors.append(sid+': asset not visually approved '+ref);continue
                    if not a.get('file') or not a.get('sha256'):errors.append(sid+': missing real asset file/hash '+ref);continue
                    try:
                        f=within(root,a['file'])
                        if not f.is_file() or sha(f)!=a['sha256']:errors.append(sid+': missing/changed file '+ref)
                    except ValueError as ex:errors.append(str(ex))
        if s.get('status')=='stale':(errors if for_generation else warnings).append(sid+': dependent asset changed; review binding first')
    for a in assets:
        if a.get('master_id') and a['master_id'] not in am:errors.append(a['id']+': unknown master')
        for dep in a.get('depends_on',[]):
            if dep not in am:errors.append(a['id']+': unknown dependency '+dep)
        if a.get('status')=='planned':warnings.append(a['id']+': image not generated')
    visiting=set();done=set()
    def walk_asset(aid):
        if aid in visiting:errors.append('Asset dependency cycle: '+aid);return
        if aid in done or aid not in am:return
        visiting.add(aid)
        for dep in am[aid].get('depends_on',[])+([am[aid]['master_id']] if am[aid].get('master_id') else []):walk_asset(dep)
        visiting.remove(aid);done.add(aid)
    for aid in am:walk_asset(aid)
    if for_generation:
        auth=p.get('authorization',{}).get('generation',{})
        if not auth.get('allowed') or not auth.get('evidence') or not auth.get('providers') or auth.get('max_jobs',0)<=0:errors.append('Generation scope/provider/job budget not recorded from user authorization')
        binding=p.get('runtime_schema_evidence')
        if not isinstance(binding,dict) or not binding.get('path') or not binding.get('sha256'):errors.append('Current provider tool schema not bound')
        else:
            try:
                f=within(root,binding['path'])
                if not f.is_file() or sha(f)!=binding['sha256']:errors.append('Provider schema file missing or changed')
            except ValueError as ex:errors.append(str(ex))
    return {'valid':not errors,'errors':errors,'warnings':warnings,'shot_count':len(selected),'media_reviewed':False,'note':'Structural checks do not replace visual, audio or user authorization verification'}
def status(root):
    root,p,assets,shots=load(root);ev=events(root);latest={}
    for x in ev:latest[x['shot_id']]=x
    return {'project_id':p['project_id'],'stage':p['stage'],'episodes':p['episodes'],'asset_status':dict(__import__('collections').Counter(a['status'] for a in assets)),'shots':[{'id':s['id'],'state':latest.get(s['id'],{}).get('state',s.get('status','planned')),'job_id':latest.get(s['id'],{}).get('job_id')} for s in shots],'reconcile_before_submit':[x for x in latest.values() if x['state'] in ACTIVE]}
def reserve(root,shot_id,request,provider):
    root,p,assets,shots=load(root);request=within(root,request)
    if not request.is_file():raise ValueError('Save actual intended request inside project first')
    with locked(root):
        v=validate(root,True,shot_id)
        if not v['valid']:raise ValueError('; '.join(v['errors']))
        auth=p['authorization']['generation']
        if provider not in auth['providers']:raise ValueError('Provider outside authorized scope')
        ev=events(root);mine=[x for x in ev if x['shot_id']==shot_id]
        if mine and mine[-1]['state'] in ACTIVE:raise ValueError('Unreconciled task exists; query existing job, do not resubmit')
        request_hash=sha(request)
        prior=next((x for x in reversed(mine) if x.get('request_sha256')==request_hash and x['state'] in ['generated','reviewed']),None)
        if prior:return {'existing':True,'event':prior,'submitted':False}
        tries=[x for x in ev if x['state']=='reserved']
        if len(tries)>=auth['max_jobs']:raise ValueError('Authorized job limit reached')
        shot_tries=[x for x in tries if x['shot_id']==shot_id]
        if len(shot_tries)>auth.get('max_retries_per_shot',0):raise ValueError('Retry scope exhausted; reconcile failure and user authorization')
        shot=next(s for s in shots if s['id']==shot_id);used=set(shot['asset_refs']+[shot['keyframe_id']])
        row={'time':now(),'event_id':uuid.uuid4().hex,'shot_id':shot_id,'shot_revision':shot['revision'],'asset_snapshot':[{k:a.get(k) for k in ['id','revision','sha256','file']} for a in assets if a['id'] in used],'state':'reserved','provider':provider,'request':request.relative_to(root).as_posix(),'request_sha256':request_hash,'job_id':None,'note':'Local intent only; host has not reported actual supplier submission'};append(root,row)
        save(root/'state/checkpoint.json',{'time':now(),'stage':'reserved','shot_id':shot_id,'next':'Execute actual authorized tool once, save raw receipt and register job; on uncertain return reconcile first'})
        return row
def event(root,shot_id,state,job_id,evidence):
    root,p,assets,shots=load(root)
    if shot_id not in {s['id'] for s in shots}:raise ValueError('Unknown shot')
    evidence=within(root,evidence)
    if not evidence.is_file():raise ValueError('Actual evidence file required')
    if state!='outcome_unknown' and not job_id:raise ValueError('Real job ID required')
    if job_id and job_id not in evidence.read_text(encoding='utf-8',errors='replace'):raise ValueError('Job ID absent from evidence; reconcile before registering')
    with locked(root):
        ev=events(root);mine=[x for x in ev if x['shot_id']==shot_id]
        if not mine:raise ValueError('No local submission intent to reconcile')
        prev=mine[-1]
        if prev['state']=='reserved' and job_id and any(x.get('job_id')==job_id for x in mine[:-1]):raise ValueError('Old job cannot attach to a new reservation; reconcile the old task separately')
        if prev.get('job_id') and job_id and prev['job_id']!=job_id:raise ValueError('Job mismatch; do not attach a different task')
        fp=sha(evidence)
        if any(x['state']==state and x.get('job_id')==job_id and x.get('evidence_sha256')==fp for x in mine):return {'deduplicated':True,'state':state}
        if state=='reviewed' and prev['state']!='generated':raise ValueError('Review requires generated output first')
        row={**{k:prev[k] for k in ['provider','request','request_sha256','shot_revision','asset_snapshot'] if k in prev},'reservation_id':prev.get('reservation_id',prev['event_id']),'time':now(),'event_id':uuid.uuid4().hex,'shot_id':shot_id,'state':state,'job_id':job_id or prev.get('job_id'),'evidence':evidence.relative_to(root).as_posix(),'evidence_sha256':fp};append(root,row)
        save(root/'state/checkpoint.json',{'time':now(),'stage':state,'shot_id':shot_id,'job_id':row['job_id'],'next':'Read raw evidence and inspect actual output; do not infer review from supplier success'})
        return row
def invalidate(root,asset_id,reason):
    root,p,assets,shots=load(root);am={a['id']:a for a in assets}
    if asset_id not in am:raise ValueError('Unknown asset')
    dirty={asset_id};changed=True
    while changed:
        changed=False
        for a in assets:
            if a['id'] not in dirty and (a.get('master_id') in dirty or set(a.get('depends_on',[]))&dirty):dirty.add(a['id']);changed=True
    affected=[]
    with locked(root):
        for a in assets:
            if a['id'] in dirty:a['status']='stale'
        for s in shots:
            if set(s.get('asset_refs',[])+([s['keyframe_id']] if s.get('keyframe_id') else []))&dirty:s['status']='stale';affected.append(s['id'])
        save(root/'assets/assets.json',assets);save(root/'storyboard/shots.json',shots)
        save(root/'state/last-invalidation.json',{'time':now(),'asset':asset_id,'reason':reason,'dependent_assets':sorted(dirty),'affected_shots':affected,'original_media_deleted':False})
    return {'affected_assets':sorted(dirty),'affected_shots':affected,'original_media_deleted':False}
def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for n in ['init','validate','status','reserve','event','invalidate']:
        q=sub.add_parser(n);q.add_argument('--root',required=True)
        if n=='init':q.add_argument('--brand',required=True);q.add_argument('--title',required=True);q.add_argument('--max-seconds',type=float,default=30);q.add_argument('--example',choices=['demo-two'])
        if n=='validate':q.add_argument('--for-generation',action='store_true');q.add_argument('--shot')
        if n=='reserve':q.add_argument('--shot',required=True);q.add_argument('--request',required=True);q.add_argument('--provider',required=True)
        if n=='event':q.add_argument('--shot',required=True);q.add_argument('--state',choices=sorted(STATES),required=True);q.add_argument('--job-id');q.add_argument('--evidence',required=True)
        if n=='invalidate':q.add_argument('--asset',required=True);q.add_argument('--reason',required=True)
    a=p.parse_args()
    if a.command=='init':result=init(a.root,a.brand,a.title,a.max_seconds,a.example)
    elif a.command=='validate':result=validate(a.root,a.for_generation,a.shot)
    elif a.command=='status':result=status(a.root)
    elif a.command=='reserve':result=reserve(a.root,a.shot,a.request,a.provider)
    elif a.command=='event':result=event(a.root,a.shot,a.state,a.job_id,a.evidence)
    else:result=invalidate(a.root,a.asset,a.reason)
    emit(result)
    if a.command=='validate' and not result['valid']:sys.exit(1)
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as e:print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
