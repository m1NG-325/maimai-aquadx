"""Apply reviewed ID-to-public-jacket matches, never infer a constant from level."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.versions import canonical_version


def supplement(public, matches):
    rows=[]
    for item in matches:
        first,second=item['matches'][:2]
        if first['distance']>3 or second['distance']-first['distance']<20:continue
        songs=[s for s in public if s['image_url']==first['image']+'.png'
               and s['title']==first['title'] and s.get('dx_lev_exp')]
        if len(songs)!=1:raise ValueError('Ambiguous image or chart type')
        s=songs[0]
        for level,diff in enumerate(('bas','adv','exp','mas','remas')):
            field='dx_lev_'+diff
            if not s.get(field):continue
            ds=s.get(field+'_i')
            rows.append(dict(music_id=item['id']+10000,level_index=level,title=s['title'],
                type='DX',level=s[field],ds=float(ds) if ds else None,
                version=canonical_version('MAGiCAL' if int(s['version'])>=27000 else 'CiRCLE PLUS' if int(s['version'])>=26500 else 'CiRCLE'),
                release_date=s.get('date_added'),artist=s['artist'],bpm=s.get('bpm'),
                designer=s.get(field+'_designer'),notes=None,reference_only=True,
                source='https://otoge-db.net/maimai/data/music-ex.json',
                idMapping=dict(method='public jacket image match',publicImage=first['image'],
                    meanPixelError=first['distance'],nextMatchError=second['distance'],
                    coverSource=f'https://assets2.lxns.net/maimai/jacket/{item["id"]}.png')))
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('public',type=Path);p.add_argument('matches',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    rows=supplement(json.loads(args.public.read_text(encoding='utf-8-sig')),json.loads(args.matches.read_text(encoding='utf8')))
    args.output.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'{len(rows)} charts from reviewed public images')
