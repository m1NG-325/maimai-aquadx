"""Generate public course/bonus metadata and resolve original bonus artwork."""
import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import UnityPy
from app.activity_metadata import read_activity_details
root=Path(sys.argv[1]);out=Path('data/report_assets/archive');data=read_activity_details(root)
Path('data/activity_details.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
roots=[root/'StreamingAssets/A000',*sorted((p for p in root.iterdir() if re.fullmatch(r'A\d+',p.name)),key=lambda p:int(p.name[1:]))]
bundles={}
for base in roots:
 for kind in ('nameplate','frame','icon','partner','chara'):
  for p in (base/'AssetBundleImages'/kind).glob('*.ab'):bundles[p.name]=p
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'));entries=manifest['entries'];unavailable=[]
for mid,b in data['bonuses'].items():
 r=b['reward'];kind=r['kind'];identifier=r['elementId']
 if not identifier or not identifier.isdigit():continue
 if kind=='MusicNew':continue
 spec={'Partner':('ui_partner','partner'),'Character':('ui_chara','chara'),'NamePlate':('ui_plate','reward-NamePlate'),'Frame':('ui_frame','reward-Frame'),'Icon':('ui_icon','reward-Icon')}.get(kind)
 if spec is None:unavailable.append({'bonusId':mid,'kind':kind,'id':identifier});continue
 prefix,category=spec;key=f'{category}:{identifier}'
 if key not in entries:
  path=bundles.get(f'{prefix}_{int(identifier):06d}.ab')
  if path:
   env=UnityPy.load(str(path));sprites=[o for o in env.objects if o.type.name=='Sprite']
   if sprites:
    name=f'bonus-{kind}-{identifier}.png';sprites[0].read().image.save(out/name);entries[key]={'file':name,'source':f'LoginBonus.xml {kind} -> {path.name}'}
 if key in entries:entries[f'bonus:{mid}']=dict(entries[key],source=f'LoginBonus.xml {kind} ID {identifier}')
 else:unavailable.append({'bonusId':mid,'kind':kind,'id':identifier})
if len(sys.argv)>2:
 import zipfile
 with zipfile.ZipFile(sys.argv[2]) as package:
  member=next(n for n in package.namelist() if n.endswith('/data.unity3d'))
  env=UnityPy.load(package.read(member))
 target={b['reward'].get('spriteName'):(mid,b) for mid,b in data['bonuses'].items() if b['reward']['kind']=='Ticket' and b['reward'].get('spriteName')}
 for obj in env.objects:
  if obj.type.name!='Sprite':continue
  sprite=obj.read()
  if sprite.m_Name not in target:continue
  mid,b=target[sprite.m_Name];identifier=b['reward']['elementId'];name=f'bonus-Ticket-{identifier}.png';sprite.image.save(out/name)
  entries[f'ticket:{identifier}']={'file':name,'source':f'LoginBonus.xml TicketId -> Ticket.xml filename {sprite.m_Name} -> game Sprite'}
  entries[f'bonus:{mid}']=dict(entries[f'ticket:{identifier}'])
  unavailable=[v for v in unavailable if v.get('bonusId')!=mid]
manifest['missingBonusImages']=unavailable
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Courses',len(data['courses']),'random',sum(c['random'] for c in data['courses'].values()),'bonuses',len(data['bonuses']),'unresolved',unavailable,flush=True)
