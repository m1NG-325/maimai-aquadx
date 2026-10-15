"""SQLite catalog and player snapshots; writes are atomic."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from decimal import Decimal
from app.parser import integer


class Database:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS charts (
                  music_id INTEGER NOT NULL, level_index INTEGER NOT NULL,
                  title TEXT NOT NULL, type TEXT NOT NULL, level TEXT NOT NULL,
                  ds REAL, version TEXT NOT NULL, is_new INTEGER NOT NULL,
                  PRIMARY KEY(music_id, level_index));
                CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def import_catalog(self, songs, source='local'):
        if not isinstance(songs, list) or not songs:
            raise ValueError('catalog must be a nonempty water-fish music_data array')
        rows = []
        seen = set()
        for song in songs:
            mid = integer(song.get('id'), 'catalog id', 1)
            info = song['basic_info']
            title, version, kind = song['title'], info['from'], song['type']
            if not all(isinstance(s, str) and s for s in (title, version)) or kind not in ('SD', 'DX'):
                raise ValueError('catalog requires title, version and SD/DX type')
            if '\ufffd' in title or '\ufffd' in version:
                raise ValueError('catalog contains replacement characters; check UTF-8 encoding')
            if not isinstance(info['is_new'], bool):
                raise ValueError('is_new must be boolean')
            if len(song['ds']) != len(song['level']) or not song['ds']:
                raise ValueError('catalog ds and level arrays must have equal nonzero lengths')
            if mid < 100000 and (len(song['ds']) not in (4, 5) or (kind == 'DX') != (mid >= 10000)):
                raise ValueError('standard catalog requires 4/5 charts and AquaDX SD/DX ID convention')
            for index, (ds, level) in enumerate(zip(song['ds'], song['level'])):
                constant = None if ds is None else Decimal(str(ds))
                if constant is not None and (not constant.is_finite() or not 0 < constant <= 20):
                    raise ValueError('invalid chart constant')
                if (mid, index) in seen:
                    raise ValueError('duplicate catalog chart')
                seen.add((mid, index))
                rows.append((mid, index, title, kind, str(level), None if constant is None else float(constant), version, info['is_new']))
        with self.connect() as db:
            db.execute('DELETE FROM charts')
            db.executemany('INSERT INTO charts VALUES (?,?,?,?,?,?,?,?)', rows)
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', ('catalog_source', source))
        return len(rows)

    def charts(self):
        with self.connect() as db:
            return [dict(r) for r in db.execute('SELECT * FROM charts ORDER BY music_id, level_index')]

    def save_private_catalog(self, value):
        # Separate reference snapshot, never replace the export eligibility catalog.
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',
                       ('private_catalog', json.dumps(value, ensure_ascii=False)))

    def private_charts(self):
        with self.connect() as db:
            row = db.execute("SELECT value FROM metadata WHERE key='private_catalog'").fetchone()
            return json.loads(row['value'])['charts'] if row else []

    def catalog_source(self):
        with self.connect() as db:
            r = db.execute("SELECT value FROM metadata WHERE key='catalog_source'").fetchone()
            return r['value'] if r else None

    def save_player(self, user_id, payload):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO players VALUES (?,?)', (str(user_id), json.dumps(payload, ensure_ascii=False)))

    def player(self, user_id):
        with self.connect() as db:
            r = db.execute('SELECT payload FROM players WHERE id=?', (str(user_id),)).fetchone()
            return json.loads(r['payload']) if r else None

    def users(self):
        with self.connect() as db:
            return [{'id': r['id'], 'name': json.loads(r['payload']).get('player', {}).get('name', r['id'])}
                    for r in db.execute('SELECT id, payload FROM players ORDER BY id')]
