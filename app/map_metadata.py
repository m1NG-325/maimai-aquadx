"""Public local-game map routes. No player data or executable reads."""
import json,re
from pathlib import Path
import xml.etree.ElementTree as ET

TYPE_FIELDS={'Character':('CharacterId','角色'),'NamePlate':('NamePlate','名牌板底板'),'Frame':('Frame','背景框'),'Title':('Title','称号'),'Icon':('Icon','头像'),'MusicNew':('MusicId','曲目解禁'),'MapTaskMusic':('MusicId','任务曲目'),'Challenge':('Challenge','挑战解禁'),'Gate':('Gate','万华镜门'),'Key':('Key','万华镜钥匙')}

def read_map_details(directory):
 root=Path(directory);maps={};treasures={};challenges={};count=0
 paths=[p for p in root.rglob('*.xml') if p.name in ('Map.xml','MapTreasure.xml','Challenge.xml')]
 # Exclude duplicate no-BGA installation; patches override base snapshots.
 paths=[p for p in paths if 'no BGA' not in p.relative_to(root).parts]
 paths.sort(key=lambda p:(max([int(n) for n in re.findall(r'(?:^|/)A(\d+)(?:/|$)',p.relative_to(root).as_posix())] or [0]),p.as_posix()))
 for p in paths:
  if p.stat().st_size>5_000_000:continue
  blob=p.read_bytes()
  if b'<!DOCTYPE' in blob.upper():continue
  try:t=ET.fromstring(blob)
  except ET.ParseError:continue
  mid=t.findtext('name/id')
  if not mid or not mid.isdigit():continue
  count+=1
  if p.name=='Challenge.xml':
   challenges[mid]={'musicId':t.findtext('Music/id'),'musicName':t.findtext('Music/str')};continue
  if p.name=='MapTreasure.xml':
   kind=t.findtext('TreasureType','未知');field,label=TYPE_FIELDS.get(kind,('',kind));name=t.findtext(field+'/str') if field else None
   treasures[mid]={'treasureId':int(mid),'kind':kind,'kindLabel':label,'name':name or t.findtext('name/str','未知奖励'),'elementId':t.findtext(field+'/id') if field else None,'quantity':t.findtext('Numeric'),'rawItemId':t.findtext('itemID')}
  else:maps[mid]=t
 result={}
 for mid,t in maps.items():
  rewards=[]
  for n in t.findall('TreasureExDatas/MapTreasureExData'):
   tid=n.findtext('TreasureId/id');raw=n.findtext('Distance')
   try:distance=int(raw)
   except (TypeError,ValueError):distance=None
   reward=dict(treasures.get(tid,{'treasureId':tid,'kind':'Unknown','kindLabel':'未收录类型','name':n.findtext('TreasureId/str','未知奖励'),'elementId':None}))
   if reward['kind']=='Challenge':reward.update(challenges.get(str(reward.get('elementId')),{}))
   reward.update(distance=distance,flag=n.findtext('Flag'),subParam1=n.findtext('SubParam1'),subParam2=n.findtext('SubParam2'));rewards.append(reward)
  plates=[r for r in rewards if r['kind']=='NamePlate' and r.get('elementId') and r['distance'] is not None]
  last=max(enumerate(plates),key=lambda pair:(pair[1]['distance'],pair[0]))[1] if plates else None
  conditions=[]
  for n in t.findall('ReleaseConditionIds/list/*'):
   conditions.append({'id':n.findtext('id') or n.text,'name':n.findtext('str')})
  result[mid]={'name':t.findtext('name/str'),'infinite':t.findtext('IsInfinity','false').lower()=='true','lastRewardDistance':max([r['distance'] for r in rewards if r['distance'] is not None],default=None),'lastPlateId':last['elementId'] if last else None,'lastPlateName':last['name'] if last else None,'lastPlateDistance':last['distance'] if last else None,'rewards':rewards,'unlockConditions':conditions,'openEvent':t.findtext('OpenEventId/str'),'openEventId':t.findtext('OpenEventId/id'),'bonusMusic':t.findtext('BonusMusicId/str'),'bonusMusicId':t.findtext('BonusMusicId/id'),'bonusMagnification':t.findtext('BonusMusicMagnification'),'color':t.findtext('ColorId/str')}
 return {'schema':1,'source':'用户本地游戏 Map.xml、MapTreasure.xml 与 Challenge.xml；参考路线可能与私服修改不同。距离为游戏原始单位；达到节点不代表已领奖。','sourceFiles':count,'maps':result}

def load_map_details(bundled,local):
 result={}
 for p in (bundled,local):
  try:result.update(json.loads(Path(p).read_text(encoding='utf-8')).get('maps',{}))
  except (OSError,ValueError,AttributeError):pass
 return result
