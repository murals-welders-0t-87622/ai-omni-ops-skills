"""Read-only lookup of external style sources; entries are not installed capabilities."""
import argparse,json
from pathlib import Path

def search(query='',source='all',download_available=False,category='',aspect=''):
    catalog=json.loads((Path(__file__).resolve().parents[1]/'assets/style-sources.json').read_text('utf8'))
    terms=query.casefold().split();rows=[]
    for row in catalog['entries']:
        if source!='all' and row['source']!=source:continue
        if download_available and row.get('availability')!='download-available':continue
        if category and row.get('category')!=category:continue
        if aspect and row.get('aspect')!=aspect:continue
        haystack=' '.join(str(v) for v in row.values()).casefold()
        if all(term in haystack for term in terms):rows.append(row)
    return {'warning':'Source index only; verify current license, availability and actual implementation before use.','count':len(rows),'entries':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--query',default='');p.add_argument('--source',choices=['all','motiongit','lemo'],default='all');p.add_argument('--download-available',action='store_true');p.add_argument('--category',choices=['open','talk','explainer','product','art','preview'],default='');p.add_argument('--aspect',default='');a=p.parse_args()
    print(json.dumps(search(a.query,a.source,a.download_available,a.category,a.aspect),ensure_ascii=False,indent=2))
