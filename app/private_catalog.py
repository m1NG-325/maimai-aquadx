"""JP reference metadata never grants eligibility to a third-party upload."""
import math
from app.versions import canonical_version


def salt_charts(data, source='https://github.com/realtvop/SaltMeta'):
    dates = {canonical_version(v['version']): v['releaseDate'] for v in data['versions']}
    rows, seen = [], set()
    for song in data['musics']:
        if all(c['type'] == 'utage' for c in song['charts']):
            continue
        mid = song['id']
        if not isinstance(mid, int) or isinstance(mid, bool) or not 0 < mid < 10000:
            raise ValueError('invalid private music ID')
        for chart in song['charts']:
            if chart['type'] not in ('sd', 'dx') or chart['difficulty'] not in range(5):
                continue
            jp = chart.get('regions', {}).get('jp')
            if not jp:
                continue
            key = (mid + (10000 if chart['type'] == 'dx' else 0), chart['difficulty'])
            if key in seen:
                raise ValueError('duplicate private chart')
            seen.add(key)
            ds = jp.get('internalLevel')
            if ds is not None and (isinstance(ds, bool) or not isinstance(ds, (int, float)) or not math.isfinite(ds) or not 0 < ds <= 20):
                raise ValueError('invalid private constant')
            version = canonical_version(jp['version'])
            rows.append(dict(music_id=key[0], level_index=key[1], title=song['title'],
                             type=chart['type'].upper(), level=jp['level'], ds=ds, version=version,
                             release_date=dates.get(version), source=source, reference_only=True))
            rows[-1].update(artist=song.get('artist'), bpm=song.get('bpm'), genre=song.get('category'),
                            designer=chart.get('noteDesigner'), notes=chart.get('noteCounts'))
    if not rows:
        raise ValueError('private catalog has no JP charts')
    return rows


def display_catalog(base, private):
    # Public metadata remains available when a deleted song is absent from JP data.
    lookup = {(c['music_id'], c['level_index']): c for c in base}
    lookup.update({(c['music_id'], c['level_index']): c for c in private})
    return list(lookup.values())


def private_view(best, base, private, lxns):
    lookup = {(c['music_id'], c['level_index']): c for c in display_catalog(base, private)}
    rows = []
    for r in best:
        c = lookup.get((r['musicId'], r['level']))
        target = lxns.get((r['musicId'] % 10000, 'dx' if r['musicId'] >= 10000 else 'standard', r['level'])) if r['musicId'] < 100000 else None
        rows.append(dict(r, title=c['title'] if c else None, ds=c['ds'] if c else None,
                         version=c['version'] if c else None, chart_level=c['level'] if c else None,
                         metadataSource=c.get('source', '本地分析曲库') if c else None,
                         referenceOnly=bool(c and c.get('reference_only')), lxnsSupported=target is not None))
    return {'rows': rows, 'known': sum(r['title'] is not None for r in rows),
            'unknown': sum(r['title'] is None for r in rows), 'referenceCharts': len(private)}
