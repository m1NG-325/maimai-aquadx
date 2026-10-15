"""Offline querying tools; reference calculations never write remote scores."""
from app.calculations import rating
from app.private_catalog import display_catalog
from app.parser import DIFFICULTIES


def library_rows(base, private, best=()):
    scores = {(r['musicId'], r['level']): r for r in best}
    rows = []
    for c in display_catalog(base, private):
        if c['music_id'] >= 100000 or c['level_index'] >= 5:
            continue
        score = scores.get((c['music_id'], c['level_index']))
        rows.append(dict(c, difficulty=DIFFICULTIES[c['level_index']], score=score))
    return sorted(rows, key=lambda c: (c['music_id'], c['level_index']))


def filter_library(rows, query='', kind='', difficulty=None, minimum=0, maximum=20, status='all'):
    query = query.casefold().strip()
    return [c for c in rows if (not query or query in c['title'].casefold() or query == str(c['music_id']))
            and (not kind or c['type'] == kind) and (difficulty is None or c['level_index'] == difficulty)
            and (minimum <= c['ds'] <= maximum if c['ds'] is not None else minimum==0 and maximum==20)
            and (status == 'all' or status == 'played' and c['score'] is not None
                 or status == 'unplayed' and c['score'] is None
                 or status == 'fc' and c['score'] and c['score']['comboStatus'] >= 1
                 or status == 'ap' and c['score'] and c['score']['comboStatus'] >= 3)]


def recommendations(records, limit=30):
    """Only recommend known, played charts relative to this catalog's B50 cutoff."""
    cutoffs = {}
    for new, count in ((False, 35), (True, 15)):
        pool = sorted((r['ra'] for r in records if r.get('ra') is not None and bool(r.get('is_new')) == new), reverse=True)
        cutoffs[new] = pool[count-1] if len(pool) >= count else 0
    rows = []
    for r in records:
        if r.get('ra') is None or r['achievements'] >= 100.5:
            continue
        cutoff = cutoffs[bool(r['is_new'])]
        for goal in (97, 98, 99, 99.5, 100, 100.5):
            if goal <= r['achievements']:
                continue
            target, _ = rating(r['ds'], goal)
            gain = target - max(cutoff, r['ra'])
            if gain > 0:
                rows.append(dict(r, goal=goal, targetRating=target, estimatedGain=gain,
                                 requiredImprovement=round(goal-r['achievements'], 4), cutoff=cutoff))
                break
    return sorted(rows, key=lambda r: (r['requiredImprovement'], -r['estimatedGain'], r['musicId'], r['level']))[:limit]
