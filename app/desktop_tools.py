"""Additional native tools inspired by KarenBot's public maimai feature set."""
import hashlib
import random
from decimal import Decimal, ROUND_FLOOR
from app.calculations import rating


def score_line(notes, target):
    if not 0 <= target <= 101:
        raise ValueError('分数线范围为 0..101%')
    if not isinstance(notes, dict):
        raise ValueError('曲库没有谱面物量，无法计算容错')
    weights = {'tap':500,'hold':1000,'slide':1500,'touch':500,'break':2500}
    counts = {k: notes.get(k) or 0 for k in weights}
    if any(not isinstance(n,int) or n<0 for n in counts.values()):
        raise ValueError('物量字段异常')
    total = sum(counts[k]*v for k,v in weights.items())
    if total <= 0:
        raise ValueError('物量不足')
    bonus_loss = .25/counts['break'] if counts['break'] else None
    return {'tapGreatLossPercent':10000/total,'maxTapGreat':total*(101-target)/10000,
            'break50LossPercent':bonus_loss,'break50Equivalent':bonus_loss/(10000/total) if bonus_loss is not None else None,
            'totalScore':total}


def today_pick(user, date, rows):
    if not rows:
        raise ValueError('没有可选歌曲')
    seed = int(hashlib.sha256((user+'|'+date).encode()).hexdigest(),16)
    rng = random.Random(seed)
    return {'date':date,'luck':rng.randint(1,100),'song':rng.choice(rows)}


def completion(rows, goal):
    tests = {'FC':lambda s:s['comboStatus']>=1, 'AP':lambda s:s['comboStatus']>=3,
             'FSD':lambda s:s['fs'] in ('fsd','fsdp'), 'SSS':lambda s:s['achievements']>=100,
             'SSS+':lambda s:s['achievements']>=100.5}
    predicate = tests[goal]
    missing = [r for r in rows if not r['score'] or not predicate(r['score'])]
    return {'total':len(rows),'completed':len(rows)-len(missing),'missing':missing}


def custom_best(records, limit=50, mark='', minimum=0, maximum=20):
    rows = [r for r in records if r.get('ra') is not None and minimum<=r['ds']<=maximum
            and (not mark or mark=='FC' and r['comboStatus']>=1 or mark=='AP' and r['comboStatus']>=3)]
    return sorted(rows,key=lambda r:(-r['ra'],-r['achievement'],r['musicId'],r['level']))[:limit]


def best40(records):
    # Legacy formula from KarenBot Rating.calcOld, not a current DX B50.
    coefficients = {'d':0,'c':5,'b':6,'bb':7,'bbb':7.5,'a':8.5,'aa':9.5,
                    'aaa':10.5,'s':12.5,'sp':12.7,'ss':13,'ssp':13.2,'sss':13.5,'sssp':14}
    rows=[]
    for r in records:
        if r.get('ds') is None:continue
        _,rank=rating(r['ds'],r['achievements'])
        value=int((Decimal(str(r['ds']))*Decimal(str(coefficients[rank]))*min(Decimal('100.5'),Decimal(str(r['achievements'])))/100).to_integral_value(rounding=ROUND_FLOOR))
        rows.append(dict(r,ra=value))
    ordered=sorted(rows,key=lambda r:(-r['ra'],-r['achievement'],r['musicId'],r['level']))
    old=[r for r in ordered if not r['is_new']][:25];new=[r for r in ordered if r['is_new']][:15]
    return {'old':old,'new':new,'oldRating':sum(r['ra'] for r in old),'newRating':sum(r['ra'] for r in new),'rating':sum(r['ra'] for r in old+new)}
