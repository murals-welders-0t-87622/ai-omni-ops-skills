"""Compare an MCP route recommendation with a tools/list response, offline."""
import argparse
import json
from pathlib import Path


def unwrap(value):
    if not isinstance(value, dict):
        raise ValueError('expected a JSON object')
    if 'error' in value:
        raise ValueError('MCP response contains an error')
    value = value.get('result', value)
    if not isinstance(value, dict) or value.get('isError'):
        raise ValueError('MCP result is not successful')
    if 'content' in value:
        texts = [b.get('text') for b in value['content'] if b.get('type') == 'text']
        if len(texts) != 1:
            raise ValueError('expected one JSON text block')
        value = json.loads(texts[0])
    if not isinstance(value, dict):
        raise ValueError('expected a JSON object in result')
    return value


def check_route(route, catalog, expected_functions=None):
    route, catalog = unwrap(route), unwrap(catalog)
    if catalog.get('nextCursor'):
        raise ValueError('tools/list has more pages; collect the full catalog first')
    tools = catalog.get('tools')
    if not isinstance(tools, list):
        raise ValueError('tools/list must contain a tools array')
    names = {t.get('name') for t in tools if isinstance(t, dict) and isinstance(t.get('name'), str)}
    primary = route.get('data', {}).get('primary', {})
    recommended = primary.get('mcpTools')
    unavailable = primary.get('unavailableMcpTools', [])
    if (not isinstance(recommended, list) or not isinstance(unavailable, list)
            or not all(isinstance(n, str) and n for n in recommended + unavailable)
            or not recommended + unavailable):
        raise ValueError('primary route has no usable mcpTools list')
    # Recompare both groups: the catalog may have changed since routing.
    recommended = list(dict.fromkeys(recommended + unavailable))
    if expected_functions is not None and (not isinstance(expected_functions, (list, tuple))
            or not expected_functions or not all(isinstance(x, str) and x.strip() for x in expected_functions)):
        raise ValueError('expected functions must be a nonempty list of names')
    function_key = primary.get('functionKey')
    if expected_functions is not None and (not isinstance(function_key, str) or not function_key):
        raise ValueError('primary route has no functionKey to compare')
    return {'functionKey': primary.get('functionKey'),
            'available': [n for n in recommended if n in names],
            'missing': [n for n in recommended if n not in names],
            'expected_route_match': None if expected_functions is None else function_key in expected_functions,
            'business_execution_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', type=Path)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('--expected-function', action='append', dest='expected_functions',
                        help='An independently verified acceptable primary function; may be repeated')
    args = parser.parse_args()
    try:
        result = check_route(json.loads(args.route.read_text(encoding='utf-8')),
                             json.loads(args.catalog.read_text(encoding='utf-8')),
                             args.expected_functions)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f'Cannot check route: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['missing'] or result['expected_route_match'] is False else 0


if __name__ == '__main__':
    raise SystemExit(main())
