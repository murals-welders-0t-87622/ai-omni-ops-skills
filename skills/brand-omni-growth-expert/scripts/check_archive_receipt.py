"""Compare an archive create receipt with a same-brand read-back, offline."""
import argparse
import json
from pathlib import Path


def payload(response):
    if not isinstance(response, dict) or 'error' in response:
        raise ValueError('invalid or failed RPC response')
    response = response.get('result', response)
    if not isinstance(response, dict) or response.get('isError'):
        raise ValueError('failed MCP result')
    if 'content' in response:
        texts = [x.get('text') for x in response['content'] if x.get('type') == 'text']
        if len(texts) != 1:
            raise ValueError('expected one JSON text result')
        response = json.loads(texts[0])
    if not isinstance(response, dict) or response.get('status') != 'success':
        raise ValueError('business response not successful')
    return response.get('data')


def check(create_response, read_response, expected):
    kind = expected.get('kind')
    if kind not in ('plan', 'material'):
        raise ValueError('kind must be plan or material')
    fields = ['brandId', 'workspaceScope', 'title']
    if kind == 'plan':
        fields.append('htmlContent')
    else:
        fields.append('materialType')
        if 'textContent' in expected:
            fields.append('textContent')
    if any(not isinstance(expected.get(f), str) or not expected[f] for f in fields):
        raise ValueError('expected identity and content fields must be nonempty')
    created = payload(create_response)
    result = payload(read_response)
    if not isinstance(created, dict) or not isinstance(created.get('id'), str) or not created['id']:
        raise ValueError('create receipt missing record ID')
    if not isinstance(result, dict):
        raise ValueError('read-back must be an object')
    if kind == 'plan' and 'status' in result:
        status = result.get('status')
        if status == 'found' and isinstance(result.get('item'), dict):
            items = [result['item']]
        elif status in ('deleted', 'not_found_unknown') and result.get('item') is None:
            items = []
        else:
            raise ValueError('invalid keyed plan read-back')
    elif isinstance(result.get('items'), list):
        items = result['items']
    else:
        raise ValueError('read-back must contain an items list or keyed plan result')
    matches = [x for x in items if isinstance(x, dict) and x.get('id') == created['id']]
    if len(matches) > 1:
        raise ValueError('duplicate IDs in read-back')
    if not matches:
        return {'state': 'not_found_in_this_read', 'file_bytes_verified': False, 'durability_verified': False}
    item = matches[0]
    mismatches = [f for f in fields if created.get(f) != expected[f] or item.get(f) != expected[f]]
    return {'state': 'mismatch' if mismatches else 'record_fields_match',
            'mismatched_fields': mismatches,
            'file_bytes_verified': False,
            'durability_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('create', type=Path)
    parser.add_argument('read', type=Path)
    parser.add_argument('expected', type=Path)
    args = parser.parse_args()
    try:
        docs = [json.loads(p.read_text(encoding='utf-8')) for p in (args.create, args.read, args.expected)]
        result = check(*docs)
    except (ValueError, OSError, json.JSONDecodeError) as error:
        parser.exit(2, f'Cannot check receipt: {error}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['state'] == 'record_fields_match' else 1


if __name__ == '__main__':
    raise SystemExit(main())
