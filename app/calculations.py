"""DX Rating, Best 35 + 15, and catalog-relative completion progress."""
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_FLOOR
from app.versions import version_order, canonical_version

COEFFICIENTS = [(0, 0, 'd'), (10, 1.6, 'd'), (20, 3.2, 'd'), (30, 4.8, 'd'),
 (40, 6.4, 'd'), (50, 8, 'c'), (60, 9.6, 'b'), (70, 11.2, 'bb'), (75, 12, 'bbb'),
 (79.9999, 12.8, 'bbb'), (80, 13.6, 'a'), (90, 15.2, 'aa'), (94, 16.8, 'aaa'),
 (96.9999, 17.6, 'aaa'), (97, 20, 's'), (98, 20.3, 'sp'), (98.9999, 20.6, 'sp'),
 (99, 20.8, 'ss'), (99.5, 21.1, 'ssp'), (99.9999, 21.4, 'ssp'), (100, 21.6, 'sss'),
 (100.4999, 22.2, 'sss'), (100.5, 22.4, 'sssp')]
OLD_VERSIONS = ('maimai', 'maimai PLUS', 'maimai GreeN', 'maimai GreeN PLUS',
 'maimai ORANGE', 'maimai ORANGE PLUS', 'maimai PiNK', 'maimai PiNK PLUS',
 'maimai MURASAKi', 'maimai MURASAKi PLUS', 'maimai MiLK', 'MiLK PLUS', 'maimai MiLK PLUS', 'maimai FiNALE')


def rating(ds, achievements):
    ds, a = Decimal(str(ds)), Decimal(str(achievements))
    if not ds.is_finite() or ds <= 0 or not a.is_finite() or not 0 <= a <= 101:
        raise ValueError('invalid constant or achievements')
    threshold, coefficient, rank = next(r for r in reversed(COEFFICIENTS) if a >= Decimal(str(r[0])))
    return int((ds * min(a, Decimal('100.5')) * Decimal(str(coefficient)) / 100).to_integral_value(rounding=ROUND_FLOOR)), rank


def enrich(records, charts, current_version=None):
    charts = [dict(c,version=canonical_version(c['version'])) for c in charts]
    current_version = canonical_version(current_version) if current_version is not None else None
    catalog = {(c['music_id'], c['level_index']): c for c in charts}
    if current_version is not None and current_version not in {c['version'] for c in charts}:
        raise ValueError('current_version is absent from catalog; import a matching catalog first')
    result = []
    for record in records:
        r = dict(record)
        c = catalog.get((r['musicId'], r['level']))
        r.update(title=None, ds=None, version=None, type=None, chart_level=None, ra=None, rate=None, is_new=None)
        r['catalogMatched'] = c is not None
        if c:
            r.update(title=c['title'], ds=c['ds'], version=c['version'], type=c['type'], chart_level=c['level'])
            r['is_new'] = c['version'] == current_version if current_version else bool(c['is_new'])
            if c['ds'] is not None and r['musicId'] < 100000 and r['level'] < 5:
                r['ra'], r['rate'] = rating(c['ds'], r['achievements'])
        result.append(r)
    return result


def b50(records):
    eligible = [r for r in records if r['ra'] is not None]
    ordered = sorted(eligible, key=lambda r: (-r['ra'], -r['ds'], -r['achievement'], r['musicId'], r['level']))
    old, new = [r for r in ordered if not r['is_new']][:35], [r for r in ordered if r['is_new']][:15]
    return {'old': old, 'new': new, 'oldRating': sum(r['ra'] for r in old),
            'newRating': sum(r['ra'] for r in new), 'rating': sum(r['ra'] for r in old + new),
            'excluded': [{'musicId': r['musicId'], 'level': r['level']} for r in records if r['ra'] is None]}


def statistics(records):
    marks = Counter(r['fc'] for r in records)
    return {'charts': len(records), 'fcOrBetter': sum(marks[m] for m in ('fc', 'fcp', 'ap', 'app')),
            'apOrBetter': marks['ap'] + marks['app'], 'marks': {m: marks[m] for m in ('', 'fc', 'fcp', 'ap', 'app')},
            'fsMarks': dict(Counter(r['fs'] for r in records)), 'chartPlayCount': sum(r['playCount'] for r in records)}


def plate_required(charts, version, mark, requirements=None):
    standard = [c for c in charts if c['music_id'] < 100000 and c['level_index'] < 5]
    if requirements is not None:
        keys = {tuple(pair) for pair in requirements.get(version, {}).get(mark, [])}
        return [c for c in standard if (c['music_id'], c['level_index']) in keys]
    if version == '真':
        return [c for c in standard if c['version'] in ('maimai', 'maimai PLUS') and c['music_id'] != 70 and c['level_index'] < 4]
    if version == '舞':
        return [c for c in standard if c['version'] in OLD_VERSIONS]
    return [c for c in standard if c['version'] == version and c['level_index'] < 4]


def plate_progress(records, charts, requirements=None):
    """Version plates exclude Re:MASTER; whole old-era 舞 includes it.

    真 groups maimai/PLUS and excludes ジングルベル (70); 真将 does not exist.
    Results describe the supplied catalog, not server-awarded plates.
    """
    by_version = defaultdict(list)
    standard = [c for c in charts if c['music_id'] < 100000 and c['level_index'] < 5]
    for c in standard:
        by_version[c['version']].append(c)
    groups = {v: [c for c in cs if c['level_index'] < 4] for v, cs in by_version.items() if v not in ('maimai', 'maimai PLUS')}
    true = [c for c in standard if c['version'] in ('maimai', 'maimai PLUS') and c['music_id'] != 70 and c['level_index'] < 4]
    if 'maimai' in by_version or 'maimai PLUS' in by_version:
        groups['真'] = true
    old = [c for c in standard if c['version'] in OLD_VERSIONS]
    if old:
        groups['舞'] = old
    scores = {(r['musicId'], r['level']): r for r in records}
    predicates = {'将': lambda r: r['achievements'] >= 100,
                  '极': lambda r: r['comboStatus'] >= 1,
                  '神': lambda r: r['comboStatus'] >= 3,
                  '舞舞': lambda r: r['fs'] in ('fsd', 'fsdp')}
    result = {}
    for version in sorted(requirements if requirements is not None else groups, key=version_order):
        progress = {}
        for mark, predicate in predicates.items():
            required = plate_required(charts, version, mark, requirements)
            supported = (mark in requirements[version]) if requirements is not None else not (version == '真' and mark == '将')
            missing = []
            for c in required:
                r = scores.get((c['music_id'], c['level_index']))
                if r is None or not predicate(r):
                    missing.append({'musicId': c['music_id'], 'level': c['level_index'], 'title': c['title']})
            total, completed = len(required), len(required) - len(missing)
            progress[mark] = {'supported': supported, 'total': total, 'completed': completed,
                             'remaining': total - completed, 'achieved': supported and total > 0 and not missing,
                             'percent': round(completed / total * 100, 2) if total else 0, 'missing': missing}
        result[version] = progress
    return result


def summarize(payload, charts, current_version=None):
    records = enrich(payload['records'], charts, current_version)
    best = enrich(payload['best'], charts, current_version)
    b = b50(best)
    unknown = [{'musicId': r['musicId'], 'level': r['level']} for r in best if not r['catalogMatched']]
    return {'source': payload['source'], 'player': payload['player'], 'rating': b['rating'], 'b50': b,
            'records': records, 'best': best, 'statistics': statistics(best), 'plates': plate_progress(best, charts),
            'calculation': {'currentVersion': current_version, 'partition': 'version' if current_version else 'catalog.is_new',
                            'catalogCharts': len(charts), 'unmatchedCharts': unknown,
                            'ratingComplete': not any(r['ra'] is None for r in best if r['musicId'] < 100000 and r['level'] < 5),
                            'plateScope': 'imported catalog; verify region, deleted songs and private-server differences'}}
