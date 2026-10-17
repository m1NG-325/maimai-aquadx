"""Sort played-chart best snapshots, keeping unknown metrics last in both directions."""
from app.calculations import rating

SORT_FIELDS=(('achievements','达成率'),('recent','最近游玩'),('ds','定数'),('dxScore','DX 分'),
             ('playCount','游玩次数'),('ra','Rating'),('fc','FC 状态'),('ap','AP 状态'))


def score_value(row,field):
    if field=='recent':return row.get('lastPlayedTimestamp')
    if field=='ra':return rating(row['ds'],row['achievements'])[0] if row.get('ds') is not None else None
    if field=='fc':return row.get('comboStatus',0)
    if field=='ap':return row.get('comboStatus',0) if row.get('comboStatus',0)>=3 else 0
    return row.get(field)


def sort_scores(rows,field='achievements',descending=True):
    if field not in dict(SORT_FIELDS):raise ValueError('未知成绩排序字段')
    # Deterministic secondary order; never promote unknown dates or constants.
    ordered=sorted(rows,key=lambda r:(-r['achievements'],r['musicId'],r['level']))
    known=[r for r in ordered if score_value(r,field) is not None]
    missing=[r for r in ordered if score_value(r,field) is None]
    return sorted(known,key=lambda r:score_value(r,field),reverse=descending)+missing
