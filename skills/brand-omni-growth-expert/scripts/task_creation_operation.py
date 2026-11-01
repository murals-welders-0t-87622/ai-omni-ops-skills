#!/usr/bin/env python3
"""Local creation-operation identity only; never sends a request or confirms a task."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import uuid


def text(value, name):
    if not isinstance(value, str) or not value or value != value.strip() or len(value) > 128:
        raise ValueError(f'{name} must be a nonempty, trimmed identifier of at most 128 characters')
    return value


@contextmanager
def connect(path):
    path = Path(path)
    if not path.parent.is_dir() or path.is_symlink():
        raise ValueError('journal parent must exist and journal must not be a symlink')
    db = sqlite3.connect(str(path), timeout=30, isolation_level=None)
    try:
        db.execute('PRAGMA busy_timeout=30000')
        db.execute('''CREATE TABLE IF NOT EXISTS task_creation_operations (
            brand_id TEXT NOT NULL, local_ref TEXT NOT NULL, command_id TEXT NOT NULL UNIQUE,
            operation_key TEXT NOT NULL UNIQUE, digest TEXT NOT NULL, state TEXT NOT NULL,
            PRIMARY KEY (brand_id, local_ref))''')
        yield db
    finally:
        db.close()


def identity(data):
    return text(data.get('brandId'), 'brandId'), text(data.get('localRef'), 'localRef')


def prepare(db, data):
    brand, ref = identity(data)
    body = data.get('request')
    if not isinstance(body, dict) or body.get('brand_id') != brand:
        raise ValueError('request must belong to the same brand')
    if 'command_id' in body or 'idempotency_key' in body:
        raise ValueError('request must not already contain operation identifiers')
    encoded = json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')
    digest = hashlib.sha256(encoded).hexdigest()
    db.execute('BEGIN IMMEDIATE')
    try:
        row = db.execute('SELECT command_id,operation_key,digest,state FROM task_creation_operations WHERE brand_id=? AND local_ref=?', (brand, ref)).fetchone()
        if row is None:
            # Lab accepts a task_ command ID as the preassigned task ID. This
            # also allows brand-scoped lookup if interruption precedes the event.
            row = ('task_' + uuid.uuid4().hex, str(uuid.uuid4()), digest, 'prepared')
            db.execute('INSERT INTO task_creation_operations VALUES (?,?,?,?,?,?)', (brand, ref, *row))
        elif row[2] != digest:
            raise ValueError('request changed; inspect the existing operation before proceeding')
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {'commandId': row[0], 'operationKey': row[1], 'state': row[3]}


def lookup(db, data):
    brand, ref = identity(data)
    row = db.execute('SELECT command_id,operation_key,state FROM task_creation_operations WHERE brand_id=? AND local_ref=?', (brand, ref)).fetchone()
    return {'status': 'found', 'commandId': row[0], 'operationKey': row[1], 'state': row[2]} if row else {'status': 'not_found'}


def mark_attempted(db, data):
    brand, ref = identity(data)
    key = text(data.get('operationKey'), 'operationKey')
    db.execute('BEGIN IMMEDIATE')
    try:
        changed = db.execute("UPDATE task_creation_operations SET state='attempted' WHERE brand_id=? AND local_ref=? AND operation_key=? AND state='prepared'", (brand, ref, key)).rowcount
        if changed != 1:
            raise ValueError('operation unavailable or already attempted; inspect the existing result')
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {'state': 'attempted'}


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='Record task creation identity without sending it.')
    parser.add_argument('action', choices=('prepare', 'lookup', 'mark-attempted'))
    parser.add_argument('--journal', required=True)
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        with connect(args.journal) as db:
            result = {'prepare': prepare, 'lookup': lookup, 'mark-attempted': mark_attempted}[args.action](db, data)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
