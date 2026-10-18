"""Analytics of retained logs, never inferred full-history or exact session duration."""
from collections import Counter
from statistics import mean
from app.archive_data import NOTE_TYPES,JUDGEMENTS,ITEM_KINDS
from app.score_times import display_play_time
from app.calculations import rating


def number(value,minimum=None):
    import math
    if isinstance(value,bool) or not isinstance(value,(int,float)):return None
    try:
        if not math.isfinite(value):return None
    except OverflowError:return None
    return value if minimum is None or value>=minimum else None


def enrich_logs(archive,charts):
    index={(c['music_id'],c['level_index']):c for c in charts};rows=[]
    for source in archive.get('sections',{}).get('userPlaylogList',[]):
        r=dict(source);chart=index.get((r['musicId'],r['level']),{})
        value=number(r.get('achievement'),0)
        r['achievements']=value/10000 if value is not None and value<=1010000 else None
        r.update(title=chart.get('title') or f"待补充曲目 · ID {r['musicId']}",ds=chart.get('ds'),versionName=chart.get('version') or '版本待核实')
        r['timeLabel']=display_play_time(r);r['day']=r['timeLabel'][:10] if r.get('lastPlayedTimestamp') is not None else ''
        r['referenceRating']=rating(r['ds'],r['achievements'])[0] if r['ds'] is not None and r['achievements'] is not None else None
        before,after=number(r.get('beforeDeluxRating')),number(r.get('afterDeluxRating'))
        r['ratingDelta']=after-before if before is not None and after is not None else None
        rows.append(r)
    return sorted(rows,key=lambda r:(r.get('lastPlayedTimestamp') is None,r.get('lastPlayedTimestamp',0),number(r.get('orderId')) or 0,number(r.get('trackNo')) or 0,r['sourceIndex']))


def filter_logs(rows,query='',difficulty=None,start='',end='',new_only=False):
    query=query.casefold().strip()
    return [r for r in rows if (not query or query in r['title'].casefold() or query==str(r['musicId']))
            and (difficulty is None or r['level']==difficulty)
            and (not start or r['day'] and r['day']>=start) and (not end or r['day'] and r['day']<=end)
            and (not new_only or r.get('isAchieveNewRecord') is True or r.get('isDeluxscoreNewRecord') is True)]


def filter_accuracy(rows,lower,upper):
    """Inclusive displayed ACC range; unknown achievements never become zero."""
    return [r for r in rows if (value:=number(r.get('achievements'))) is not None and lower<=value<=upper]


def log_statistics(rows):
    totals={};coverage={}
    for note in NOTE_TYPES:
        for judge in JUDGEMENTS:
            field=note+judge;values=[v for r in rows if (v:=number(r.get(field),0)) is not None]
            totals[field]=sum(values) if values else None;coverage[field]=len(values)
    counts=Counter(r['day'] for r in rows if r.get('day'))
    fast=[v for r in rows if (v:=number(r.get('fastCount'),0)) is not None]
    late=[v for r in rows if (v:=number(r.get('lateCount'),0)) is not None]
    # Ratio only uses logs providing BOTH counters. Partial field coverage must not skew it.
    pairs=[(f,l) for r in rows if (f:=number(r.get('fastCount'),0)) is not None and (l:=number(r.get('lateCount'),0)) is not None]
    f,l=sum(p[0] for p in pairs),sum(p[1] for p in pairs)
    valid_acc=[r['achievements'] for r in rows if r.get('achievements') is not None]
    return {'logs':len(rows),'days':dict(sorted(counts.items())),'undated':sum(not r.get('day') for r in rows),
            'judgements':totals,'coverage':coverage,'fast':sum(fast) if fast else None,'late':sum(late) if late else None,
            'fastCoverage':len(fast),'lateCoverage':len(late),'pairedTimingLogs':len(pairs),
            'fastPercent':100*f/(f+l) if f+l else None,'averageAchievement':mean(valid_acc) if valid_acc else None,
            'fcLogs':sum(r.get('comboStatus') in (1,2,3,4) for r in rows),'apLogs':sum(r.get('comboStatus') in (3,4) for r in rows)}


def rating_candidates(archive,charts):
    index={(c['music_id'],c['level_index']):c for c in charts};result=[]
    for entry in archive.get('sections',{}).get('userGeneralDataList',[]):
        if entry['propertyKey'] not in ('recent_rating_next','recent_rating_next_new'):continue
        for position,text in enumerate(entry['propertyValue'].split(','),1):
            parts=text.split(':')
            if len(parts)!=4 or not all(p.isdigit() for p in parts):continue
            mid,level,version,acc=map(int,parts)
            if mid<1 or level>4 or acc>1010000:continue
            c=index.get((mid,level),{});ds=c.get('ds')
            result.append({'musicId':mid,'level':level,'version':version,'title':c.get('title') or f'ID {mid}',
                'achievements':acc/10000,'referenceRating':rating(ds,acc/10000)[0] if ds is not None else None,
                'group':'新曲候选' if entry['propertyKey'].endswith('_new') else '旧曲候选','position':position})
    return result


def favorite_music_ids(archive):
    sections=archive.get('sections',{});ids=set()
    for r in sections.get('userFavoriteMusicList',[]):
        if isinstance(r.get('id'),int) and r['id']>0:ids.add(r['id'])
    for r in sections.get('userGeneralDataList',[]):
        if r['propertyKey']=='favorite_music':
            for value in r['propertyValue'].split(','):
                if value.isdigit() and int(value)>0:ids.add(int(value))
    return ids
