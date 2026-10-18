"""Generate public map metadata and last-nameplate artwork from game snapshots."""
import sys,json,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import UnityPy
from app.map_metadata import read_map_details
root=Path(sys.argv[1]);out=Path('data/report_assets/archive');data=read_map_details(root)
Path('data/map_details.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
roots=[root/'StreamingAssets/A000',*sorted((p for p in root.iterdir() if re.fullmatch(r'A\d+',p.name)),key=lambda p:int(p.name[1:]))]
bundles={}
for base in roots:
 for kind in ('nameplate','frame','icon'):
  for p in (base/'AssetBundleImages'/kind).glob('*.ab'):bundles[p.name]=p
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'));entries=manifest['entries'];entries={k:v for k,v in entries.items() if not k.startswith('map:')}
cache={};missing=[]
for mid,m in data['maps'].items():
 pid=m['lastPlateId']
 if not pid:continue
 if pid not in cache:
  path=bundles.get(f'ui_plate_{int(pid):06d}.ab');cache[pid]=None
  if path:
   env=UnityPy.load(str(path));sprites=[o for o in env.objects if o.type.name=='Sprite']
   if sprites:
    name=f'map-plate-{pid}.png';sprites[0].read().image.save(out/name);cache[pid]=name
 if cache[pid]:entries[f'map:{mid}']={'file':cache[pid],'source':f'Map.xml -> MapTreasure.xml NamePlate {pid}; last by distance','plateId':pid}
 else:missing.append({'mapId':mid,'plateId':pid})
reward_assets=set()
for m in data['maps'].values():
 for r in m['rewards']:
  if r['kind'] in ('NamePlate','Frame','Icon') and str(r.get('elementId') or '').isdigit():reward_assets.add((r['kind'],r['elementId']))
reward_missing=[]
for kind,identifier in sorted(reward_assets):
 category,prefix=('plate','ui_plate') if kind=='NamePlate' else ('frame','ui_frame') if kind=='Frame' else ('icon','ui_icon')
 name=f'map-plate-{identifier}.png' if kind=='NamePlate' else f'reward-{category}-{identifier}.png'
 path=bundles.get(f'{prefix}_{int(identifier):06d}.ab')
 if not (out/name).exists() and path:
  env=UnityPy.load(str(path));sprites=[o for o in env.objects if o.type.name=='Sprite']
  if sprites:sprites[0].read().image.save(out/name)
 if (out/name).exists():entries[f'reward-{kind}:{identifier}']={'file':name,'source':f'MapTreasure.xml {kind} -> {prefix}_{int(identifier):06d}.ab'}
 else:reward_missing.append({'kind':kind,'id':identifier})
manifest['missingRewardImages']=reward_missing
print('Reward image references',len(reward_assets),'missing',len(reward_missing),flush=True)
manifest.update(entries=entries,mapSource='Last NamePlate reward by route distance; no island fallback',missingMapPlates=missing)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Maps',len(data['maps']),'with plate',sum(bool(m['lastPlateId']) for m in data['maps'].values()),'images',sum(k.startswith('map:') for k in entries),'missing',len(missing),flush=True)
