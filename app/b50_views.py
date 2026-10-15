"""Source B50 is an exported snapshot; Lxns B50 is a labeled catalog estimate."""
import math
from app.calculations import b50, rating
from app.parser import DIFFICULTIES


def source_b50(payload, charts):
    composition = payload.get('ratingComposition', {})
    lookup = {(c['music_id'], c['level_index']): c for c in charts}
    groups = {}
    for group in ('old', 'new'):
        groups[group] = []
        for position, item in enumerate(composition.get(group, []), 1):
            c = lookup.get((item['musicId'], item['level']))
            ds = c.get('ds') if c else None
            ra, rank = rating(ds, item['achievements']) if ds is not None else (None, None)
            groups[group].append(dict(item, position=position, title=c['title'] if c else None,
                                      ds=ds, ra=ra, rate=rank, ratingSource='reference calculation' if ra is not None else 'metadata unavailable',
                                      catalogMatched=c is not None))
    totals = payload.get('sourceRatings', {})
    old, new = totals.get('playerOldRating'), totals.get('playerNewRating')
    valid = lambda v: isinstance(v, int) and not isinstance(v, bool) and v >= 0
    calculated = {g: sum(r['ra'] or 0 for r in groups[g]) for g in ('old', 'new')}
    return dict(groups, calculatedOldRating=calculated['old'], calculatedNewRating=calculated['new'],
                calculatedRating=sum(calculated.values()), uncalculated=sum(r['ra'] is None for g in groups.values() for r in g),
                available=bool(composition.get('available')), oldRating=old if valid(old) else None,
                newRating=new if valid(new) else None, rating=old + new if valid(old) and valid(new) else None,
                reportedPlayerRating=payload['player'].get('rating'),
                warnings=composition.get('warnings', ['旧的本地快照没有私服分组，请重新导入原始 JSON']),
                basis='AquaDX exported order and reported totals; individual ratings calculated with reference constants')


def target_b50(scores, catalog, current_version, use_remote_rating=False):
    records, excluded = [], []
    for score in scores:
        key = (score['id'], score['type'], score['level_index'])
        c = catalog.get(key)
        if not c or c.get('disabled') or c.get('ds') is None or c.get('version') is None:
            excluded.append(':'.join(map(str, key)))
            continue
        ra, rank = rating(c['ds'], score['achievements'])
        supplied = score.get('dx_rating')
        if use_remote_rating and isinstance(supplied, (int, float)) and math.isfinite(supplied) and supplied >= 0:
            ra = math.floor(supplied)
        mid = score['id'] + (10000 if score['type'] == 'dx' else 0)
        records.append(dict(score, musicId=mid, level=score['level_index'], difficulty=DIFFICULTIES[score['level_index']],
                            title=c['title'], ds=c['ds'], version=c['version'], ra=ra, rate=rank,
                            achievement=round(score['achievements'] * 10000),
                            is_new=c['version'] >= current_version))
    view = b50(records)
    view.update(excluded=excluded, available=True, currentVersion=current_version,
                basis='remote scores with catalog grouping' if use_remote_rating else 'imported scores only; catalog estimate',
                estimated=True)
    return view


def compare_groups(source, target):
    membership = {(r['musicId'], r['level']): group for group in ('old', 'new') for r in target[group]}
    differences = []
    for group in ('old', 'new'):
        for r in source[group]:
            target_group = membership.get((r['musicId'], r['level']))
            if target_group != group:
                differences.append({'musicId': r['musicId'], 'level': r['level'], 'title': r.get('title'),
                                    'sourceGroup': group, 'targetGroup': target_group,
                                    'reason': '分组不同' if target_group else '未进入落雪估算 B50（可能未收录或被其他成绩挤出）'})
    return differences


def compare_b50(source, target):
    """Align by musicId/difficulty, rather than pairing unrelated songs at rank N."""
    target_rows = {(r['musicId'], r['level']): dict(r, group=group, position=rank)
                   for group in ('old', 'new') for rank, r in enumerate(target.get(group, []), 1)}
    source_keys = set()
    rows = []
    for group in ('old', 'new'):
        for rank, original in enumerate(source.get(group, []), 1):
            key = (original['musicId'], original['level'])
            source_keys.add(key)
            left = dict(original, group=group, position=rank)
            right = target_rows.get(key)
            changes = []
            if right is None:
                changes.append('source_only')
            else:
                if group != right['group']:
                    changes.append('group_changed')
                if round(left['achievements'] * 10000) != round(right['achievements'] * 10000):
                    changes.append('score_changed')
                if group == right['group'] and rank != right['position']:
                    changes.append('rank_changed')
            rows.append({'musicId': key[0], 'level': key[1], 'title': left.get('title') or (right or {}).get('title'),
                         'source': left, 'target': right, 'changes': changes or ['same']})
    for key, right in target_rows.items():
        if key not in source_keys:
            rows.append({'musicId': key[0], 'level': key[1], 'title': right.get('title'), 'source': None,
                         'target': right, 'changes': ['target_only']})
    kinds = ('same', 'source_only', 'target_only', 'group_changed', 'score_changed', 'rank_changed')
    source_rating, target_rating = source.get('rating'), target.get('rating')
    return {'available': bool(source.get('available')) and target.get('available', True), 'rows': rows,
            'counts': {kind: sum(kind in r['changes'] for r in rows) for kind in kinds},
            'ratingDelta': target_rating - source_rating if isinstance(source_rating, int) and isinstance(target_rating, int) else None}
