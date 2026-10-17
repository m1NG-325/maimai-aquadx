"""Only attach real per-chart timestamps; never infer time from record order or rating."""
from datetime import datetime,timezone,timedelta
import math

LOCAL_TIMEZONE=timezone(timedelta(hours=8))
SCORE_FIELDS=('lastPlayedAt','last_played_at','lastPlayDate','lastPlayTime','userPlayDate','playDate')
LOG_FIELDS=('userPlayDate','playDate','playTime')


def parse_play_time(value):
    if value is None or isinstance(value,bool):return None
    try:
        text=str(value).strip()
        if not text:return None
        if text.isdigit() and len(text) in (8,14):
            dt=datetime.strptime(text,'%Y%m%d' if len(text)==8 else '%Y%m%d%H%M%S')
        elif isinstance(value,(int,float)) or text.isdigit():
            number=float(value)
            if not math.isfinite(number) or number<=0:return None
            dt=datetime.fromtimestamp(number/(1000 if number>=100000000000 else 1),tz=LOCAL_TIMEZONE)
        else:
            dt=datetime.fromisoformat(text.replace('/','-').replace('Z','+00:00'))
        if not 2000<=dt.year<=2100:return None
        if dt.tzinfo is None:dt=dt.replace(tzinfo=LOCAL_TIMEZONE)
        return dict(lastPlayedAt=dt.isoformat(timespec='milliseconds'),lastPlayedTimestamp=round(dt.timestamp()*1000))
    except (ValueError,OverflowError,OSError):return None


def latest_time(item,fields=SCORE_FIELDS,prefix='score'):
    candidates=[]
    for field in fields:
        result=parse_play_time(item.get(field))
        if result:candidates.append(dict(result,lastPlayedSource=prefix+'.'+field))
    return max(candidates,key=lambda v:v['lastPlayedTimestamp']) if candidates else {}


def playlog_times(logs):
    result={}
    if not isinstance(logs,list):return result
    for row in logs:
        if not isinstance(row,dict):continue
        mid,level=str(row.get('musicId','')),str(row.get('level',''))
        if not mid.isdigit() or not level.isdigit() or int(mid)<=0:continue
        key=(int(mid),int(level));value=latest_time(row,LOG_FIELDS,'userPlaylogList')
        if value and value['lastPlayedTimestamp']>result.get(key,{}).get('lastPlayedTimestamp',-1):result[key]=value
    return result


def attach_latest(record,times):
    value=times.get((record['musicId'],record['level']))
    if value and value['lastPlayedTimestamp']>(record.get('lastPlayedTimestamp') or -1):record.update(value)


def display_play_time(record):
    value=record.get('lastPlayedAt')
    if not value:return '未提供'
    parsed=parse_play_time(value)
    if not parsed:return '未提供'
    return datetime.fromtimestamp(parsed['lastPlayedTimestamp']/1000,tz=LOCAL_TIMEZONE).strftime('%Y-%m-%d %H:%M')
