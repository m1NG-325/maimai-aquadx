"""Offline regional plate membership snapshots; metadata is resolved by UnifiedCatalog."""
import json
from pathlib import Path
from app.versions import canonical_version

SCOPE_LABELS = ('私服曲库', '国服曲库', '私服曲库（含删除曲目）')
SCOPE_KEYS = ('jp', 'cn', 'jp_history')


def load_plate_catalogs(path):
    value = json.loads(Path(path).read_text(encoding='utf-8'))
    if value.get('schema') != 1:
        raise ValueError('unsupported plate catalog schema')
    for key in SCOPE_KEYS:
        scope = value['scopes'][key]
        scope['charts'] = [dict(c,version=canonical_version(c['version'])) for c in scope['charts']]
        if 'requirements' in scope:
            scope['requirements'] = {canonical_version(v):marks for v,marks in scope['requirements'].items()}
        seen = set()
        for c in scope['charts']:
            identity = (c['music_id'], c['level_index'], c['version'])
            if identity in seen or not 0 < c['music_id'] < 100000 or c['level_index'] not in range(5):
                raise ValueError('invalid or duplicate plate chart')
            seen.add(identity)
        available = {(c['music_id'], c['level_index']) for c in scope['charts']}
        for marks in scope.get('requirements', {}).values():
            for required in marks.values():
                if not all(tuple(pair) in available for pair in required):
                    raise ValueError('plate requirement missing from catalog')
    return value
