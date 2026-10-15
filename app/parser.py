"""AquaDX best-record parsing. Achievement uses 1/10000 percent units."""
from decimal import Decimal, InvalidOperation

DIFFICULTIES = ('BASIC', 'ADVANCED', 'EXPERT', 'MASTER', 'Re:MASTER')
FC = {0: '', 1: 'fc', 2: 'fcp', 3: 'ap', 4: 'app'}
FS = {0: '', 1: 'fs', 2: 'fsp', 3: 'fsd', 4: 'fsdp', 5: 'sync'}
FS_ORDER = {'': 0, 'sync': 1, 'fs': 2, 'fsp': 3, 'fsd': 4, 'fsdp': 5}


def integer(value, field, minimum=0):
    try:
        d = Decimal(str(value))
        if not d.is_finite() or d != d.to_integral_value() or d < minimum:
            raise ValueError()
        return int(d)
    except (ValueError, InvalidOperation):
        raise ValueError(f'{field}: expected integer >= {minimum}') from None


def first(item, keys, default=None):
    return next((item[k] for k in keys if item.get(k) is not None), default)


def parse_record(item):
    if not isinstance(item, dict):
        raise ValueError('score must be an object')
    music_id = integer(item.get('musicId'), 'musicId', 1)
    level = integer(item.get('level'), 'level')
    raw = integer(item.get('achievement'), 'achievement')
    if raw > 1010000:
        raise ValueError('achievement: expected AquaDX units 0..1010000')
    combo = integer(item.get('comboStatus', 0), 'comboStatus')
    sync = integer(item.get('syncStatus', 0), 'syncStatus')
    if combo not in FC or sync not in FS:
        raise ValueError('unknown comboStatus or syncStatus')
    dx = integer(first(item, ('deluxscoreMax', 'deluxscore', 'dxScore', 'dxscore'), 0), 'DXScore')
    return {'musicId': music_id, 'level': level, 'difficulty': DIFFICULTIES[level] if level < 5 else 'UTAGE/UNKNOWN',
            'achievement': raw, 'achievements': float(Decimal(raw) / 10000),
            'dxScore': dx, 'scoreRank': item.get('scoreRank'), 'comboStatus': combo,
            'syncStatus': sync, 'fc': FC[combo], 'fs': FS[sync],
            'ap': FC[combo] if combo >= 3 else '',
            'playCount': integer(item.get('playCount', 0), 'playCount')}


def best_records(records):
    """Best marks and DX score may come from different plays; count is a snapshot."""
    best = {}
    for record in records:
        key = (record['musicId'], record['level'])
        if key not in best:
            best[key] = dict(record)
            continue
        old = best[key]
        if record['achievement'] > old['achievement']:
            for field in ('achievement', 'achievements', 'scoreRank'):
                old[field] = record[field]
        old['dxScore'] = max(old['dxScore'], record['dxScore'])
        old['playCount'] = max(old['playCount'], record['playCount'])
        if record['comboStatus'] > old['comboStatus']:
            for field in ('comboStatus', 'fc', 'ap'):
                old[field] = record[field]
        if FS_ORDER[record['fs']] > FS_ORDER[old['fs']]:
            old['syncStatus'], old['fs'] = record['syncStatus'], record['fs']
    return [best[key] for key in sorted(best)]


def parse_rating_composition(data):
    """Keep the game's own B35/B15 ordering; it cannot be inferred from CN catalogs."""
    general = data.get('userGeneralDataList', [])
    result = {'old': [], 'new': [], 'available': False, 'warnings': []}
    if not isinstance(general, list):
        result['warnings'].append('userGeneralDataList 不是列表，无法读取私服 B50')
        return result
    for group, name, limit in [('old', 'recent_rating', 35), ('new', 'recent_rating_new', 15)]:
        values = [x.get('propertyValue') for x in general if isinstance(x, dict) and x.get('propertyKey') == name]
        if not values:
            result['warnings'].append(f'导出未包含 {name}，请重新导入完整 AquaDX 导出文件')
            continue
        try:
            value = values[-1]
            if not isinstance(value, str):
                raise ValueError('expected string')
            entries = [entry for entry in value.split(',') if entry]
            if len(entries) > limit:
                raise ValueError('too many entries')
            seen = set()
            parsed = []
            for entry in entries:
                fields = entry.split(':')
                if len(fields) != 4:
                    raise ValueError('expected musicId:level:romVersion:achievement')
                mid, level, version, achievement = [integer(v, name) for v in fields]
                if mid <= 0 or level > 4 or achievement > 1010000 or (mid, level, version) in seen:
                    raise ValueError('invalid or duplicate entry')
                seen.add((mid, level, version))
                parsed.append({'musicId': mid, 'level': level, 'romVersion': version,
                               'achievement': achievement, 'achievements': achievement / 10000,
                               'difficulty': DIFFICULTIES[level]})
            result[group] = parsed
        except ValueError:
            result['warnings'].append(f'{name} 格式异常，未猜测或重排该分组')
    result['available'] = all(any(isinstance(x, dict) and x.get('propertyKey') == name for x in general)
                              for name in ('recent_rating', 'recent_rating_new')) and not result['warnings']
    return result


def parse_aquadx(data):
    if not isinstance(data, dict):
        raise ValueError('AquaDX export must be an object')
    lists = [data[k] for k in ('userMusicDetailList', 'musicDetailList', 'userMusicList') if k in data]
    if not lists:
        raise ValueError('missing AquaDX best-score list')
    records = []
    for entries in lists:
        if not isinstance(entries, list):
            raise ValueError('score list must be an array')
        for item in entries:
            if isinstance(item, dict) and 'userMusicDetailList' in item:
                nested = item['userMusicDetailList']
                if not isinstance(nested, list):
                    raise ValueError('nested score list must be an array')
                records.extend(parse_record(dict(child, musicId=child.get('musicId', item.get('musicId')))) for child in nested)
            else:
                records.append(parse_record(item))
    user = data.get('userData', {})
    if not isinstance(user, dict):
        raise ValueError('userData must be an object')
    return {'source': 'AquaDX', 'player': {'name': user.get('userName'), 'rating': user.get('playerRating'),
            'playCount': user.get('playCount'), 'romVersion': user.get('lastRomVersion'),
            'dataVersion': user.get('lastDataVersion')}, 'records': records,
            'best': best_records(records), 'ratingComposition': parse_rating_composition(data),
            'sourceRatings': {k: user.get(k) for k in ('playerOldRating', 'playerNewRating', 'musicRating', 'playerRating')}}
