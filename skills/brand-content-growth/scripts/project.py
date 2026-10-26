"""Local drafts and semantic checks; never calls MCP or a media supplier."""
from pathlib import Path
from datetime import datetime
import json,argparse,sys

BASE=Path(__file__).resolve().parents[1]
TASKS={f'T{i}' for i in range(1,7)}
METHODS={f'M{i:02d}' for i in range(1,19)}

def ratio(numerator,denominator):
    if numerator is None or denominator in (None,0):return None
    if isinstance(numerator,bool) or isinstance(denominator,bool):raise ValueError('boolean is not a metric')
    if numerator<0 or denominator<0:raise ValueError('negative count')
    return numerator/denominator

def project_file(root,ref):
    if not isinstance(ref,str) or not ref.strip():raise ValueError('missing file reference')
    p=(root/ref).resolve()
    if not p.is_relative_to(root.resolve()):raise ValueError('file outside project')
    if not p.is_file() or p.stat().st_size==0:raise ValueError('file missing or empty: '+ref)
    return p

def validate(data,root,stage):
    errors=[];warnings=[]
    def need(v,label):
        if v is None or v=='' or v==[]:errors.append(label+' missing')
    def file(ref,label):
        try:project_file(root,ref)
        except ValueError as e:errors.append(label+': '+str(e))
    if data.get('schema_version')!='brand-content-local-1.0':errors.append('unsupported schema_version')
    need(data.get('brand',{}).get('name'),'brand.name')
    authority=data.get('authority',{})
    if authority.get('mode')=='server' and not authority.get('task_id'):errors.append('server authority requires a real task reference')
    if data.get('upstream',{}).get('report_status')!='available':warnings.append('growth report unavailable/unverified: retain research gap, do not invent it')
    ev=data.get('evidence',[]);evidence={x.get('id'):x for x in ev}
    if len(evidence)!=len(ev) or None in evidence:errors.append('evidence IDs missing or duplicate')
    cards=data.get('value_cards',[]);values={x.get('id'):x for x in cards}
    if len(values)!=len(cards) or None in values:errors.append('value card IDs missing or duplicate')
    strategy=data.get('strategy',{})
    for k in ('business_bottleneck','priority_user','priority_scenario','value_proposition','primary_task','handoff_path','measurement_plan'):need(strategy.get(k),'strategy.'+k)
    if strategy.get('primary_task') not in TASKS:errors.append('strategy.primary_task must be T1..T6')
    if not cards:errors.append('at least one explicit pain-solution-scenario card required')
    for x in cards:
        for k in ('user','scenario','pain','solution','difference','limits'):need(x.get(k),'value_card.'+k)
        refs=x.get('evidence_ids',[])
        if not refs:warnings.append(str(x.get('id'))+' has no evidence; treat as hypothesis')
        for ref in refs:
            if ref not in evidence:errors.append('unknown evidence: '+str(ref))
        if x.get('status')=='supported' and (not refs or all(evidence.get(r,{}).get('kind')=='hypothesis' for r in refs)):errors.append('supported value card lacks non-hypothetical evidence')
    items=data.get('content_items',[])
    ids=[x.get('id') for x in items]
    if len(set(ids))!=len(ids) or None in ids:errors.append('content IDs missing or duplicate')
    if stage in ('script','release'):
        if not items:errors.append('content item required')
        for x in items:
            for k in ('title','narrative_structure','format','brand_role','next_step','measurement'):need(x.get(k),'content.'+k)
            if x.get('value_card_id') not in values:errors.append('content must link to a value card')
            if x.get('primary_task') not in TASKS:errors.append('content primary_task invalid')
            if not x.get('strategy_ids') or any(m not in METHODS for m in x['strategy_ids']):errors.append('content strategy_ids invalid')
            file(x.get('script_path'),'script')
            for claim in x.get('claims',[]):
                refs=claim.get('evidence_ids',[])
                if claim.get('status')!='verified' or not refs:errors.append('factual claim pending verification: '+str(claim.get('text')))
                elif any(r not in evidence or evidence[r].get('kind') in ('hypothesis','user_preference') for r in refs):errors.append('claim has invalid factual evidence')
            if stage=='release':
                for asset in x.get('assets',[]):
                    file(asset.get('path'),'asset')
                    if asset.get('rights_status')!='cleared':errors.append('public use rights not cleared')
                    if asset.get('is_product_proof') and asset.get('sku_status')!='verified':errors.append('product proof SKU unverified')
    if stage=='release':
        # Release here means readiness for publication, not authority to perform it.
        publish=data.get('permissions',{}).get('publication',{})
        if not publish.get('authorized') or not publish.get('scope_ref'):errors.append('publication authorization missing')
        artifacts=data.get('artifacts',[])
        for x in items:
            produced=[a for a in artifacts if a.get('content_id')==x.get('id') and a.get('kind')=='video' and a.get('status')=='reviewed']
            if not produced:errors.append('reviewed video missing for '+str(x.get('id')))
            for a in produced:
                file(a.get('path'),'video')
                need(a.get('content_approval_ref'),'content approval')
                for k in ('technical_record','visual_record','audio_record'):file(a.get('qa',{}).get(k),'qa.'+k)
        warnings.append('file records do not prove technical, audiovisual, legal or commercial quality; inspect actual evidence')
    if stage=='review':
        if not data.get('metrics'):errors.append('metrics required or explicitly report unavailable instead of claiming measured review')
        for m in data.get('metrics',[]):
            for k in ('name','source_ref','window','unit','attribution'):need(m.get(k),'metric.'+k)
            try:
                computed=ratio(m.get('numerator'),m.get('denominator'))
                if m.get('rate') is not None and (computed is None or abs(m['rate']-computed)>1e-9):errors.append('metric rate conflicts with numerator/denominator')
            except (ValueError,TypeError):errors.append('invalid metric count')
    return {'stage':stage,'errors':errors,'warnings':warnings,'passed':not errors}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('init');i.add_argument('--root',required=True);i.add_argument('--brand',required=True)
    c=sub.add_parser('check');c.add_argument('--root',required=True);c.add_argument('--stage',choices=['strategy','script','release','review'],required=True)
    a=p.parse_args();root=Path(a.root).resolve()
    if a.cmd=='init':
        if root.exists():raise ValueError('target already exists; inspect and continue rather than overwrite')
        data=json.loads((BASE/'assets/project-template.json').read_text(encoding='utf-8'))
        data['brand']['name']=a.brand;data['project_key']=root.name
        data['created_at']=datetime.now().astimezone().isoformat()
        root.mkdir(parents=True)
        (root/'project.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'created':str(root/'project.json'),'mode':'local_draft','external_calls':0},ensure_ascii=False));return 0
    data=json.loads((root/'project.json').read_text(encoding='utf-8'));result=validate(data,root,a.stage)
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passed'] else 1

if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,FileNotFoundError) as e:print(str(e),file=sys.stderr);sys.exit(2)
