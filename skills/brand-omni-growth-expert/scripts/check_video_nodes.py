#!/usr/bin/env python3
"""Offline check of selected video input nodes against a current MCP app detail receipt."""
import argparse
import json
import sys


def unwrap(response):
    if not isinstance(response, dict) or 'error' in response:
        raise ValueError('invalid or failed RPC response')
    response = response.get('result', response)
    if not isinstance(response, dict) or response.get('isError'):
        raise ValueError('failed MCP result')
    if 'content' in response:
        blocks = response['content']
        if not isinstance(blocks, list):
            raise ValueError('invalid MCP content')
        texts = [x.get('text') for x in blocks if isinstance(x, dict) and x.get('type') == 'text']
        if len(texts) != 1 or not isinstance(texts[0], str):
            raise ValueError('expected one JSON text result')
        response = json.loads(texts[0])
    if not isinstance(response, dict) or response.get('status') != 'success':
        raise ValueError('app detail was not successful')
    data = response.get('data')
    if not isinstance(data, dict) or not isinstance(data.get('item'), dict):
        raise ValueError('app detail missing item')
    return data['item']


def check(response, selection):
    app = unwrap(response)
    if not isinstance(selection, dict) or not isinstance(selection.get('appKey'), str) or not selection['appKey'].strip():
        raise ValueError('appKey is required')
    if app.get('key') != selection['appKey']:
        raise ValueError('app key differs from current detail')
    nodes = app.get('nodeInfoList')
    chosen = selection.get('nodes')
    if not isinstance(nodes, list) or not isinstance(chosen, list) or not chosen:
        raise ValueError('current node list and selected nodes are required')
    def node_identity(node):
        node_id = node.get('nodeId')
        field_name = node.get('fieldName')
        if isinstance(node_id, bool) or not isinstance(node_id, (str, int)) or not str(node_id).strip():
            raise ValueError('node identity is required')
        if not isinstance(field_name, str) or not field_name.strip():
            raise ValueError('node identity is required')
        return (str(node_id), field_name)
    index = {}
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError('invalid node definition')
        identity = node_identity(node)
        if identity in index:
            raise ValueError('missing or duplicate node identity')
        index[identity] = node.get('fieldType')
    seen, failures = set(), []
    for selected in chosen:
        if not isinstance(selected, dict) or any(k not in ('nodeId', 'fieldName', 'fieldType') for k in selected):
            raise ValueError('selected nodes contain unsupported fields')
        identity = node_identity(selected)
        expected_type = selected.get('fieldType')
        if not isinstance(expected_type, str) or not expected_type.strip():
            raise ValueError('selected node identity and type are required')
        if identity in seen:
            raise ValueError('duplicate selected node')
        seen.add(identity)
        if identity not in index:
            failures.append({'nodeId': identity[0], 'fieldName': identity[1], 'issue': 'not_in_current_detail'})
        elif index[identity] != expected_type:
            failures.append({'nodeId': identity[0], 'fieldName': identity[1], 'issue': 'type_mismatch'})
    return {'appKey': selection['appKey'], 'configured_indicator': app.get('configured') is True,
            'mapping_state': 'matched' if not failures else 'mismatch', 'issues': failures,
            'required_inputs_verified': False, 'provider_access_verified': False,
            'cost_authorized': False, 'generation_verified': False}


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError('request must be an object')
        result = check(request.get('receipt'), request.get('selection'))
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['mapping_state'] == 'matched' else 1


if __name__ == '__main__':
    raise SystemExit(main())
