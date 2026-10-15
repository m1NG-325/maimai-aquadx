"""Presentation models preserve the calculator's B50 and plate decisions."""
from collections import defaultdict
from app.calculations import OLD_VERSIONS
from app.versions import OLD,DX,canonical_version
from app.calculations import rating

PLATE_WORDS={canonical_version(v):word for v,word in zip(OLD+DX,
    ['真','真','超','檄','橙','暁','桃','櫻','紫','菫','白','雪','輝','熊','華','爽','煌','宙','星','祭','祝','双','宴','鏡','彩','丸','廻'])}


def b50_report(data, view, catalog, label):
    lookup={(c['music_id'],c['level_index']):c for c in catalog}
    scores={(r['musicId'],r['level']):r for r in data['privateCatalog']['rows']}
    result=dict(view, label=label, player=data['player'].get('name') or '本地玩家')
    for group in ('old','new'):
        result[group]=[]
        for position,r in enumerate(view[group],1):
            key=(r['musicId'],r['level']);c=lookup.get(key,{});score=scores.get(key,{})
            ds=r.get('ds') if r.get('ds') is not None else c.get('ds')
            ra=r.get('ra')
            if ra is None and ds is not None:ra=rating(ds,r['achievements'])[0]
            result[group].append(dict(r, title=r.get('title') or c.get('title'), position=position,
                ds=ds, ra=ra, type=c.get('type','DX' if r['musicId']>=10000 else 'SD'),
                fc=score.get('fc',''), fs=score.get('fs','')))
    return result


def plate_report(data, charts, version, mark, difficulty=3, only_missing=False):
    progress=data['plates'][version][mark]
    standard=[c for c in charts if c['music_id']<100000 and c['level_index']<5]
    if version=='真':
        required=[c for c in standard if c['version'] in ('maimai','maimai PLUS') and c['music_id']!=70 and c['level_index']<4]
    elif version=='舞':
        required=[c for c in standard if c['version'] in OLD_VERSIONS]
    else:
        required=[c for c in standard if c['version']==version and c['level_index']<4]
    missing={(r['musicId'],r['level']) for r in progress['missing']}
    counts=[]
    for level in (4,3,2,1,0):
        group=[c for c in required if c['level_index']==level]
        if group:counts.append(dict(level=level,total=len(group),completed=sum((c['music_id'],level) not in missing for c in group)))
    groups=defaultdict(list)
    for c in required:
        if c['level_index']!=difficulty:continue
        complete=(c['music_id'],difficulty) not in missing
        if only_missing and complete:continue
        groups[c['level']].append(dict(c,complete=complete))
    def order(level):
        try:return float(level.rstrip('+'))+(.5 if level.endswith('+') else 0)
        except ValueError:return -1
    return dict(title=PLATE_WORDS.get(version,version)+mark+'完成表',version=version,mark=mark,difficulty=difficulty,
                supported=progress['supported'],counts=counts,completed=progress['completed'],total=progress['total'],
                groups=[{'level':level,'charts':sorted(rows,key=lambda c:c['music_id'])} for level,rows in sorted(groups.items(),key=lambda x:-order(x[0]))],
                onlyMissing=only_missing)
