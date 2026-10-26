#!/usr/bin/env python3
"""依据已核单图应用快照准备请求；不上传、不提交、不扣费。"""
import argparse,json,sys,re
from pathlib import Path
import project

def prepare(root,shot_id,uploaded_image,upload_receipt,resolution='720p'):
    root,p,assets,shots=project.load(root);s=next((s for s in shots if s['id']==shot_id),None)
    if not s or s.get('kind')!='generated':raise ValueError('Select an existing generated shot, not a design end card')
    check=project.validate(root,True,shot_id)
    if not check['valid']:raise ValueError('; '.join(check['errors']))
    profile=project.read(project.within(root,p['provider_profile']))
    if profile['id']!='runninghub-seedance-mini-2069739201603661825':raise ValueError('This builder only supports the explicitly bound single-image application; use current schema for another adapter')
    receipt=project.within(root,upload_receipt)
    if not receipt.is_file() or uploaded_image not in receipt.read_text(encoding='utf-8',errors='replace'):raise ValueError('Actual upload receipt must contain the image reference')
    if re.match(r'^[A-Za-z]:[\\/]',uploaded_image) or uploaded_image.startswith(('../','./','/')) or not uploaded_image.strip():raise ValueError('Remote image reference required; local paths are not upload references')
    if resolution not in profile['advertisedResolutions']:raise ValueError('Resolution not exposed by selected application')
    ratio=p['delivery']['aspect_ratio']
    if ratio not in profile['aspectRatios']:raise ValueError('Aspect ratio not supported')
    node=profile['parameterNode'];image=profile['imageNode']
    req={'nodeInfoList':[{'nodeId':image['nodeId'],'fieldName':image['fieldName'],'fieldValue':uploaded_image},{'nodeId':node,'fieldName':'prompt','fieldValue':s['prompt']},{'nodeId':node,'fieldName':'duration','fieldValue':str(s['generation_duration'])},{'nodeId':node,'fieldName':'ratio','fieldValue':ratio},{'nodeId':node,'fieldName':'resolution','fieldValue':resolution}]}
    dest=root/'runs/requests'/(shot_id+'-'+s['revision']+'-'+project.sha(receipt)[:10]+'.json')
    if dest.exists() and project.read(dest)!=req:raise ValueError('Request revision collision; use a new revision instead of overwriting')
    project.save(dest,req)
    project.save(dest.with_suffix('.meta.json'),{'prepared_at':project.now(),'provider_id':profile['id'],'shot_id':shot_id,'upload_receipt':receipt.relative_to(root).as_posix(),'upload_receipt_sha256':project.sha(receipt),'image_reference':uploaded_image,'keyframe_id':s['keyframe_id'],'request_sha256':project.sha(dest),'submitted':False,'actual_cost':None,'note':'Offline prepared request only. No API base/query route guessed, no credentials included.'})
    return {'request':str(dest),'submitted':False,'duration':s['generation_duration'],'native_resolution_requested':resolution,'final_delivery':p['delivery']}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--shot',required=True);p.add_argument('--uploaded-image',required=True);p.add_argument('--upload-receipt',required=True);p.add_argument('--resolution',default='720p');a=p.parse_args();project.emit(prepare(a.root,a.shot,a.uploaded_image,a.upload_receipt,a.resolution))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
