#!/usr/bin/env python3
"""Persist a task's archive operation identity; never invoke MCP or store payloads."""
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
import sqlite3
import sys
import uuid
from pathlib import Path


def required_text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError(f'{name} must be a nonempty string of at most 256 characters')
    return value


@contextmanager
def connect(path):
    path = Path(path)
    if not path.parent.is_dir() or path.is_symlink():
        raise ValueError('journal parent must exist and journal must not be a symlink')
    db = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    try:
        db.execute('PRAGMA busy_timeout=30000')
        db.execute('''CREATE TABLE IF NOT EXISTS operations (
            task_id TEXT NOT NULL, brand_id TEXT NOT NULL, slot TEXT NOT NULL,
            operation_key TEXT NOT NULL UNIQUE, digest TEXT NOT NULL,
            state TEXT NOT NULL, record_id TEXT,
            PRIMARY KEY (task_id, brand_id, slot))''')
        yield db
    finally:
        db.close()


def identity(request):
    return tuple(required_text(request.get(k), k) for k in ('taskId', 'brandId', 'slot'))


def payload_digest(request):
    payload = request.get('payload')
    if not isinstance(payload, dict) or 'idempotencyKey' in payload:
        raise ValueError('payload must be an object without idempotencyKey')
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def prepare(db, request):
    task, brand, slot = identity(request)
    digest = payload_digest(request)
    db.execute('BEGIN IMMEDIATE')
    try:
        row = db.execute('SELECT operation_key,digest,state,record_id FROM operations WHERE task_id=? AND brand_id=? AND slot=?', (task, brand, slot)).fetchone()
        if row is None:
            row = (str(uuid.uuid4()), digest, 'prepared', None)
            db.execute('INSERT INTO operations VALUES (?,?,?,?,?,?,?)', (task, brand, slot, *row))
        elif row[1] != digest:
            raise ValueError('operation content changed; inspect the original or create a new operation slot')
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {'operationKey': row[0], 'state': row[2], 'recordId': row[3]}


def transition(db, request, action, required_digest=None):
    task, brand, slot = identity(request)
    key = required_text(request.get('operationKey'), 'operationKey')
    db.execute('BEGIN IMMEDIATE')
    try:
        row = db.execute('SELECT operation_key,state,record_id,digest FROM operations WHERE task_id=? AND brand_id=? AND slot=?', (task, brand, slot)).fetchone()
        if not row or row[0] != key:
            raise ValueError('operation identity does not match')
        if required_digest is not None and row[3] != required_digest:
            raise ValueError('operation content does not match prepared payload')
        if action == 'attempted':
            if row[1] not in ('prepared', 'attempted'):
                raise ValueError('acknowledged operation cannot be attempted again')
            state, record = 'attempted', None
        else:
            record = required_text(request.get('recordId'), 'recordId')
            if row[1] not in ('attempted', 'acknowledged') or (row[2] is not None and row[2] != record):
                raise ValueError('operation state or record identity conflicts')
            state = 'acknowledged'
        db.execute('UPDATE operations SET state=?,record_id=? WHERE task_id=? AND brand_id=? AND slot=?', (state, record, task, brand, slot))
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {'operationKey': key, 'state': state, 'recordId': record}


def acknowledge_verified(db, request):
    """Confirm a plan only after matching supplied create and read-back receipts."""
    _, brand, _ = identity(request)
    expected = request.get('expected')
    body = request.get('payload')
    digest = payload_digest(request)
    if not isinstance(expected, dict) or expected.get('kind') != 'plan' or expected.get('brandId') != brand:
        raise ValueError('plan receipt and operation must use the same brand')
    for field in ('workspaceScope', 'title', 'htmlContent'):
        if not isinstance(expected.get(field), str) or not expected[field] or body.get(field) != expected[field]:
            raise ValueError(f'plan {field} does not match prepared payload')
    checker_path = Path(__file__).with_name('check_archive_receipt.py')
    spec = importlib.util.spec_from_file_location('omni_archive_receipt_checker', checker_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    result = checker.check(request.get('createReceipt'), request.get('readReceipt'), expected)
    if result['state'] != 'record_fields_match':
        raise ValueError('archive receipt not fully verified: ' + result['state'])
    created = checker.payload(request['createReceipt'])
    return transition(db, {**request, 'recordId': created['id']}, 'acknowledge', required_digest=digest)


def acknowledge_recovered_lab(db, request):
    """Verify a keyed Lab lookup when the original create receipt was lost."""
    _, brand, _ = identity(request)
    key = required_text(request.get('operationKey'), 'operationKey')
    if brand != brand.strip() or key != key.strip():
        raise ValueError('brand and operation key must match the values sent to Lab')
    digest = payload_digest(request)
    body = request['payload']
    for field in ('workspaceScope', 'title', 'htmlContent'):
        if not isinstance(body.get(field), str) or not body[field]:
            raise ValueError(f'plan {field} must be nonempty')
    spec = importlib.util.spec_from_file_location('omni_archive_receipt_checker', Path(__file__).with_name('check_archive_receipt.py'))
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    result = checker.payload(request.get('readReceipt'))
    if not isinstance(result, dict) or result.get('status') != 'found' or not isinstance(result.get('item'), dict):
        raise ValueError('keyed lookup did not return a found record')
    item = result['item']
    identity_bytes = json.dumps([brand, key], ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    record_id = 'ai_control_center_marketing_plan_' + hashlib.sha256(identity_bytes).hexdigest()
    if item.get('id') != record_id or item.get('brandId') != brand:
        raise ValueError('recovered record does not match the Lab brand and operation key')
    if any(item.get(field) != body[field] for field in ('workspaceScope', 'title', 'htmlContent')):
        raise ValueError('recovered record does not match the prepared plan')
    return transition(db, {**request, 'recordId': record_id}, 'acknowledge', required_digest=digest)


def main():
    # The caller sends UTF-8 JSON even on Windows systems with a different ANSI code page.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Persist archive operation identity in a local task directory.')
    parser.add_argument('action', choices=('prepare', 'attempted', 'acknowledge', 'acknowledge-verified', 'acknowledge-recovered-lab'))
    parser.add_argument('--journal', required=True)
    args = parser.parse_args()
    try:
        request = json.load(sys.stdin)
        with connect(args.journal) as db:
            if args.action == 'prepare':
                result = prepare(db, request)
            elif args.action == 'acknowledge-verified':
                result = acknowledge_verified(db, request)
            elif args.action == 'acknowledge-recovered-lab':
                result = acknowledge_recovered_lab(db, request)
            else:
                result = transition(db, request, args.action)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
