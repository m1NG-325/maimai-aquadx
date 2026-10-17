"""Separate offline recommendation pools; imported scores are never remote account scores."""
from collections import Counter
from app.calculations import enrich, b50
from app.local_tools import recommendations
from app.private_catalog import display_catalog
from app.versions import canonical_version, version_order


def scope_result(payload, charts, current, label, basis, versions=()):
    records=enrich(payload['best'],charts)
    best=b50(records)
    cutoffs={group: min((r['ra'] for r in best[group]),default=0) if len(best[group])==count else 0
             for group,count in [('old',35),('new',15)]}
    return dict(label=label,currentVersion=current,basis=basis,versions=list(versions),
                rows=recommendations(records),rating=best['rating'],b50=best,cutoffs=cutoffs,
                matched=sum(r['ra'] is not None for r in records),
                missingConstants=sum(r['catalogMatched'] and r['ds'] is None for r in records),
                unsupported=sum(not r['catalogMatched'] for r in records),
                scoreSource='本地导入成绩，非官服账号成绩')


def private_recommendations(payload, base, private, history, current=None):
    charts=display_catalog(display_catalog(base,history),private)
    charts=[dict(c,version=canonical_version(c['version'])) for c in charts
            if c['music_id']<100000 and c['level_index']<5 and c.get('version')]
    versions=sorted({c['version'] for c in charts if version_order(c['version'])[0]!=999},key=version_order)
    lookup={(c['music_id'],c['level_index']):c for c in charts}
    exported=Counter(lookup[(r['musicId'],r['level'])]['version']
                     for r in payload.get('ratingComposition',{}).get('new',[])
                     if (r['musicId'],r['level']) in lookup)
    inferred=next(iter(exported)) if len(exported)==1 else None
    if current is not None:
        current=canonical_version(current)
        if current not in versions:raise ValueError('私服推荐版本不在参考曲库内')
        basis='手动选择新曲版本；私服参考定数估算'
    else:
        current=inferred or (versions[-1] if versions else None)
        basis='从导出新曲分组识别版本；私服参考定数估算' if inferred else '未能唯一识别游戏版本，暂用最新参考版本；请核对新曲版本'
    eligible=[dict(c,is_new=c['version']==current) for c in charts
              if current is not None and version_order(c['version'])<=version_order(current)]
    return scope_result(payload,eligible,current,'私服',basis,versions)


def cn_recommendations(payload, catalog, versions, unified_charts=None):
    codes=[v['version'] for v in versions if isinstance(v.get('version'),int)]
    current=max(codes) if codes else max((c['version']//1000*1000 for c in catalog.values() if isinstance(c.get('version'),int)),default=0)
    title=next((v.get('title') for v in versions if v.get('version')==current),str(current))
    charts=[]
    for (mid,kind,level),c in catalog.items():
        version=c.get('version')
        if c.get('disabled') or not isinstance(version,int) or level>=5:continue
        charts.append(dict(music_id=mid+(10000 if kind=='dx' else 0),level_index=level,
                           title=c['title'],ds=c.get('ds'),version=str(version),type='DX' if kind=='dx' else 'SD',
                           level=c['level'],is_new=version>=current))
    if unified_charts is not None:
        charts=[dict(c) for c in unified_charts if not c.get('disabled')]
    result=scope_result(payload,charts,title,'国服','按统一国服曲库的定数及当前年度分组估算')
    result['versionCode']=current
    return result
