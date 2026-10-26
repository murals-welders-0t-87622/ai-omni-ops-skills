#!/usr/bin/env python3
"""Search the offline link index; never download or execute upstream files."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', choices=['shotcraft', 'talkcraft'])
    parser.add_argument('--query', default='')
    parser.add_argument('--id')
    parser.add_argument('--limit', type=int, default=12)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    path = Path(__file__).resolve().parents[1] / 'references' / 'recipe-index.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    matches = []
    for card in data['cards']:
        if args.library and card['library'] != args.library:
            continue
        if args.id and card['id'] != args.id:
            continue
        fields = [card['id'], card.get('category', ''), *card.get('tags', [])]
        for style in card.get('styles', []):
            fields.extend([style['key'], style.get('label', '')])
        if args.query.casefold() not in ' '.join(fields).casefold():
            continue
        matches.append(card)
    shown = matches[:args.limit]
    if args.json:
        print(json.dumps({'snapshot': data['snapshot'], 'total': len(matches), 'cards': shown}, ensure_ascii=False, indent=2))
    else:
        print(f'{len(matches)} matches; showing {len(shown)}. Snapshot: {data["snapshot"]}')
        for card in shown:
            print(f'\n[{card["library"]}] {card["id"]} ({card.get("category", "")})')
            print(f'  Card: {card["sourceUrl"]}')
            if card.get('implementationUrl'):
                print(f'  Implementation: {card["implementationUrl"]}')
            for style in card.get('styles', []):
                print(f'  Style: {style["key"]} | Preview: {style.get("previewUrl", "unavailable")}')
            if card.get('previewUrl'):
                print(f'  Preview: {card["previewUrl"]}')
        if not matches:
            print('Try an English slug/category; this index is not a semantic search engine.')


if __name__ == '__main__':
    main()
