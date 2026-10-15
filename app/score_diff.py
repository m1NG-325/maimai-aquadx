"""Canonical comparisons and local pre-upload snapshots; no credentials stored."""
import hashlib
import json
import secrets
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from app.parser import FC, FS_ORDER, integer

FC_ORDER = {value: key for key, value in FC.items()}
FIELDS = ('achievements', 'dx_score', 'fc', 'fs')


def score_key(score):
    return f"{score['id']}:{score['type']}:{score['level_index']}"


def normalize_scores(response):
    data = response.get('data')
    if isinstance(data, dict):
        data = data.get('scores')
    if response.get('success') is not True or not isinstance(data, list):
        raise ValueError('落雪没有返回完整成绩列表，未创建上传预览')
    scores, seen = [], set()
    for item in data:
        if not isinstance(item, dict):
            raise ValueError('落雪成绩条目结构异常')
        a = Decimal(str(item.get('achievements')))
        if not a.is_finite() or not 0 <= a <= 101:
            raise ValueError('落雪达成率字段异常')
        fc, fs = item.get('fc') or '', item.get('fs') or ''
        kind = item.get('type')
        if fc not in FC_ORDER or fs not in FS_ORDER or kind not in ('standard', 'dx', 'utage'):
            raise ValueError('落雪谱面类型或标记异常，未猜测原成绩')
        score = {'id': integer(item.get('id'), 'id', 1), 'type': kind,
                 'level_index': integer(item.get('level_index'), 'level_index'),
                 'achievements': float(a.quantize(Decimal('0.0001'))),
                 'dx_score': integer(item.get('dx_score'), 'dx_score'), 'fc': fc or None, 'fs': fs or None}
        key = score_key(score)
        if key in seen:
            raise ValueError('落雪返回了重复谱面，无法确定原最佳成绩')
        seen.add(key)
        scores.append(score)
    return sorted(scores, key=score_key)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def field_number(field, value):
    if field == 'fc':
        return FC_ORDER[value or '']
    if field == 'fs':
        return FS_ORDER[value or '']
    return Decimal(str(value))


def differences(local, remote):
    previous = {score_key(s): s for s in remote}
    rows = []
    for score in local:
        key = score_key(score)
        old = previous.get(key)
        changes = []
        if old is not None:
            for field in FIELDS:
                direction = field_number(field, score[field]) - field_number(field, old[field])
                if direction:
                    changes.append({'field': field, 'before': old[field], 'after': score[field],
                                    'direction': 'higher' if direction > 0 else 'lower'})
        lower = any(c['direction'] == 'lower' for c in changes)
        higher = any(c['direction'] == 'higher' for c in changes)
        category = 'new' if old is None else 'mixed' if lower and higher else 'lower' if lower else 'higher' if higher else 'same'
        rows.append({'key': key, 'before': old, 'after': score, 'changes': changes, 'category': category,
                     'hasLower': lower, 'recommended': category in ('new', 'higher'),
                     'fcChanged': any(c['field'] == 'fc' for c in changes),
                     'fsChanged': any(c['field'] == 'fs' for c in changes)})
    return rows


def verify_scores(selected, remote):
    observed = {score_key(s): s for s in remote}
    rows = []
    for want in selected:
        found = observed.get(score_key(want))
        if found is None:
            status = 'missing'
        else:
            values = [field_number(f, found[f]) - field_number(f, want[f]) for f in FIELDS]
            status = 'exact' if all(v == 0 for v in values) else 'stronger' if all(v >= 0 for v in values) else 'different'
        rows.append({'key': score_key(want), 'status': status, 'expected': want, 'observed': found})
    return {'available': True, 'rows': rows, 'counts': {kind: sum(r['status'] == kind for r in rows)
                                                     for kind in ('exact', 'stronger', 'different', 'missing')}}


class BackupStore:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('''CREATE TABLE IF NOT EXISTS lxns_backups (
                id TEXT PRIMARY KEY, user_id TEXT NOT NULL, friend_code TEXT NOT NULL,
                created_at TEXT NOT NULL, phase TEXT NOT NULL, payload TEXT NOT NULL)''')

    def save(self, user_id, account, response, phase):
        backup_id = secrets.token_hex(16)
        created = datetime.now(timezone.utc).isoformat()
        payload = {'source': 'Lxns', 'account': account, 'created_at': created, 'phase': phase,
                   'response': response}
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('INSERT INTO lxns_backups VALUES (?,?,?,?,?,?)',
                       (backup_id, user_id, account['friend_code'], created, phase, json.dumps(payload, ensure_ascii=False)))
        return {'id': backup_id, 'created_at': created, 'phase': phase, 'friend_code': account['friend_code']}

    def get(self, user_id, backup_id):
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute('SELECT payload FROM lxns_backups WHERE id=? AND user_id=?', (backup_id, user_id)).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, user_id):
        with closing(sqlite3.connect(self.path)) as db:
            rows = db.execute('SELECT id, created_at, phase, friend_code FROM lxns_backups WHERE user_id=? ORDER BY created_at DESC LIMIT 50', (user_id,)).fetchall()
        return [dict(zip(('id', 'created_at', 'phase', 'friend_code'), r)) for r in rows]
