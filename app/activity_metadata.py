"""Course and login-bonus reference metadata from user-owned game XML."""
from pathlib import Path
import re,json
import xml.etree.ElementTree as ET
BONUS_FIELDS={'Partner':('PartnerId','Partner','搭档'),'Character':('CharacterId','Character','角色'),'MusicNew':('MusicId','MusicNew','曲目解禁'),'Frame':('FrameId','Frame','背景框'),'Plate':('PlateId','NamePlate','名牌板'),'Icon':('IconId','Icon','头像'),'Title':('TitleId','Title','称号'),'Ticket':('TicketId','Ticket','票券')}
def read_activity_details(directory):
 root=Path(directory);courses={};bonuses={};tickets={};count=0
 paths=[p for p in root.rglob('*.xml') if p.name in ('Course.xml','LoginBonus.xml','Ticket.xml') and 'no BGA' not in p.relative_to(root).parts]
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
  if p.name=='Ticket.xml':tickets[mid]={'spriteName':t.findtext('filename')};continue
  if p.name=='Course.xml':
   musics=[]
   for n in t.findall('courseMusicData/CourseMusicData'):
    identifier=n.findtext('musicId/id');level=n.findtext('difficulty/id')
    if identifier and identifier.isdigit() and level and level.isdigit():musics.append({'musicId':int(identifier),'name':n.findtext('musicId/str'),'level':int(level)})
   courses[mid]={'name':t.findtext('name/str'),'mode':t.findtext('courseMode/str'),'random':t.findtext('isRandom','false').lower()=='true','lower':t.findtext('lowerLevel'),'upper':t.findtext('upperLevel'),'life':t.findtext('life'),'recover':t.findtext('recover'),'damage':{k:t.findtext(k+'Damage') for k in ('perfect','great','good','miss')},'musics':musics}
  else:
   kind=t.findtext('BonusType','Unknown');field,target,label=BONUS_FIELDS.get(kind,('','Unknown',kind));identifier=t.findtext(field+'/id') if field else None
   bonuses[mid]={'name':t.findtext('name/str'),'bonusType':kind,'reward':{'kind':target,'kindLabel':label,'elementId':identifier,'name':t.findtext(field+'/str') if field else t.findtext('name/str')},'maxPoint':t.findtext('maxPoint'),'repeat':t.findtext('IsRepeatGet','false').lower()=='true','collabo':t.findtext('IsCollabo','false').lower()=='true','openEvent':t.findtext('OpenEventId/str'),'openEventId':t.findtext('OpenEventId/id')}
 for b in bonuses.values():
  if b['reward']['kind']=='Ticket':b['reward'].update(tickets.get(str(b['reward'].get('elementId')),{}))
 return {'schema':1,'source':'本地 Course.xml 与 LoginBonus.xml；配置与导出状态分别展示，可能与私服修改不同。','sourceFiles':count,'courses':courses,'bonuses':bonuses}
def load_activity_details(bundled,local):
 result={'courses':{},'bonuses':{}}
 for p in (bundled,local):
  try:data=json.loads(Path(p).read_text(encoding='utf-8'))
  except (OSError,ValueError):continue
  for key in result:result[key].update(data.get(key,{}))
 return result
