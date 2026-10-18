"""Extract collection artwork and render title text on original game title bases."""
import argparse,json,os,re,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
import UnityPy

def supplement_jackets(root,out):
    roots=[root/'StreamingAssets/A000',*sorted((p for p in root.iterdir() if re.fullmatch(r'A\d+',p.name)),key=lambda p:int(p.name[1:]))]
    jackets={}
    for base in roots:
        for path in (base/'AssetBundleImages').rglob('*.ab'):
            match=re.fullmatch(r'ui_jacket_(\d+)\.ab',path.name,re.I)
            if match:jackets[str(int(match[1]))]=path
    covers=out.parent/'covers';covers.mkdir(exist_ok=True);sources={};created=0
    for identifier,path in jackets.items():
        target=covers/(identifier+'.png')
        if not target.exists():
            env=UnityPy.load(str(path));sprites=[o for o in env.objects if o.type.name=='Sprite']
            if len(sprites)==1:image=sprites[0].read().image
            else:
                textures=[o.read() for o in env.objects if o.type.name=='Texture2D']
                texture=next((o for o in textures if o.m_Name.lower()==path.stem.lower()),None)
                if texture is None:continue
                image=texture.image
            image.save(target);created+=1
        sources[identifier]={'file':f'covers/{identifier}.png','source':f'AssetBundleImages/{path.parent.name}/{path.name}'}
    manifest=json.loads((out/'manifest.json').read_text(encoding='utf8'));manifest['collectionJacketSources']=sources
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print('Jacket references',len(sources),'new',created,flush=True)


def build(root,ipa,out):
    roots=[root/'StreamingAssets/A000',*sorted((p for p in root.iterdir() if re.fullmatch(r'A\d+',p.name)),key=lambda p:int(p.name[1:]))]
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((out/'manifest.json').read_text(encoding='utf8'));entries=manifest['entries'];missing=[];counts=Counter()
    bundles={}
    for base in roots:
        for path in (base/'AssetBundleImages').rglob('*.ab'):
            match=re.fullmatch(r'ui_(icon|plate|frame)_(\d+)\.ab',path.name,re.I)
            if match:bundles[(match[1].lower(),str(int(match[2])))]=path
    for (kind,identifier),path in sorted(bundles.items()):
        env=UnityPy.load(str(path));sprites=[o.read() for o in env.objects if o.type.name=='Sprite']
        sprite=next((s for s in sprites if s.m_Name.lower()==path.stem.lower()),sprites[0] if len(sprites)==1 else None)
        if sprite is None:missing.append({'kind':kind,'id':identifier,'reason':'no unambiguous Sprite'});continue
        image=sprite.image.convert('RGBA');image.thumbnail({'icon':(256,256),'plate':(768,192),'frame':(512,288)}[kind])
        filename=f'collection-{kind}-{identifier}.png';image.save(out/filename)
        row={'file':filename,'source':f'AssetBundleImages/{path.parent.name}/{path.name} -> Sprite {sprite.m_Name}'}
        entries[f'{kind}:{identifier}']=row
        alias={'plate':'NamePlate','icon':'Icon','frame':'Frame'}[kind]
        candidates=[f'map-plate-{identifier}.png'] if kind=='plate' else [f'reward-{kind}-{identifier}.png',f'bonus-{alias}-{identifier}.png']
        original=next((name for name in candidates if (out/name).is_file()),None)
        entries[f'reward-{alias}:{identifier}']=dict(row,file=original or filename)
        counts[kind]+=1
        if sum(counts.values())%250==0:print('Extracted',dict(counts),flush=True)
    records={'title':{},'ticket':{}}
    for base in roots:
        for kind,filename in [('title','Title.xml'),('ticket','Ticket.xml')]:
            for path in (base/kind).rglob(filename):
                blob=path.read_bytes()
                if len(blob)>5_000_000 or b'<!DOCTYPE' in blob.upper():continue
                tree=ET.fromstring(blob);identifier=tree.findtext('name/id')
                if identifier and identifier.isdigit():records[kind][identifier]={'name':tree.findtext('name/str') or '', 'rarity':tree.findtext('rareType'), 'sprite':tree.findtext('filename')}
    import zipfile
    with zipfile.ZipFile(ipa) as package:
        env=UnityPy.load(package.read(next(n for n in package.namelist() if n.endswith('/data.unity3d'))))
    wanted={r['sprite'] for r in records['ticket'].values() if r['sprite']}
    wanted.update('UI_CMN_Shougou_'+r['rarity'] for r in records['title'].values() if r['rarity'])
    shared={}
    for obj in env.objects:
        if obj.type.name!='Sprite':continue
        sprite=obj.read()
        if sprite.m_Name in wanted:
            filename=f'collection-common-{sprite.m_Name}.png';sprite.image.save(out/filename);shared[sprite.m_Name]=filename
    for identifier,row in records['ticket'].items():
        filename=shared.get(row['sprite'])
        if filename:entries[f'ticket:{identifier}']={'file':filename,'source':f'Ticket.xml filename {row["sprite"]} -> original shared Sprite'};counts['ticket']+=1
        else:missing.append({'kind':'ticket','id':identifier,'reason':'exact XML sprite not present'})
    # Titles are text with a shared rarity background, not unique per-title sprites.
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtGui import QGuiApplication,QPixmap,QPainter,QFont,QFontMetrics,QColor,QPainterPath,QPen,QFontDatabase
    from PySide6.QtCore import Qt,QRectF
    app=QGuiApplication.instance() or QGuiApplication([])
    for name in ('msyh.ttc','msyhbd.ttc','msgothic.ttc'):
        font=Path(os.getenv('WINDIR','C:/Windows'))/'Fonts'/name
        if font.exists():QFontDatabase.addApplicationFont(str(font))
    for identifier,row in records['title'].items():
        sprite='UI_CMN_Shougou_'+str(row['rarity']);base=shared.get(sprite)
        if not base:missing.append({'kind':'title','id':identifier,'reason':'rarity background unavailable'});continue
        original=QPixmap(str(out/base));width=768;height=max(64,round(original.height()*width/original.width()))
        preview=original.scaled(width,height,Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.SmoothTransformation)
        painter=QPainter(preview);painter.setRenderHint(QPainter.RenderHint.Antialiasing);font=QFont('Microsoft YaHei');font.setBold(True);size=min(42,height//2)
        while size>9:
            font.setPixelSize(size)
            if QFontMetrics(font).horizontalAdvance(row['name'])<=width-70:break
            size-=1
        painter.setFont(font);metrics=QFontMetrics(font);text_width=metrics.horizontalAdvance(row['name'])
        glyphs=QPainterPath();glyphs.addText((width-text_width)/2,(height-metrics.height())/2+metrics.ascent(),font,row['name'])
        painter.setPen(QPen(QColor('#ffffff'),max(1,size/12)));painter.setBrush(QColor('#20252d'));painter.drawPath(glyphs);painter.end()
        filename=f'collection-title-{identifier}.png';assert preview.save(str(out/filename),'PNG')
        entries[f'title:{identifier}']={'file':filename,'source':f'Title.xml name/str + rareType {row["rarity"]} -> {sprite}; Qt text preview, not a standalone game texture','renderedText':True,'name':row['name'],'rarity':row['rarity']};counts['title']+=1
    manifest.update(entries=entries,collectionImageCounts=dict(counts),missingCollectionImages=missing,
                    collectionImageSource='Latest local AssetBundleImages by A-version; exact shared sprites from user-selected game package; titles composed with original rarity backgrounds and XML text.')
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'counts':dict(counts),'missing':missing},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('game',type=Path);parser.add_argument('ipa',type=Path);parser.add_argument('--output',type=Path,default=Path('data/report_assets/archive'))
    parser.add_argument('--jackets-only',action='store_true')
    args=parser.parse_args()
    if not args.jackets_only:build(args.game,args.ipa,args.output)
    supplement_jackets(args.game,args.output)
