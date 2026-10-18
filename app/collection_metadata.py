"""Read names from user-owned game XML; no executable or image extraction."""
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

XML_KINDS={'Chara.xml':'chara','Map.xml':'map','Course.xml':'course','Partner.xml':'partner',
    'Plate.xml':'plate','NamePlate.xml':'nameplate','Icon.xml':'icon','Title.xml':'title','Frame.xml':'frame',
    'Ticket.xml':'ticket','LoginBonus.xml':'bonus','KaleidxScopeGate.xml':'gate','KaleidxScopeCourse.xml':'kaleidx',
    'CardChara.xml':'card','MapTreasure.xml':'treasure'}


def read_xml_names(directory):
    root=Path(directory)
    if not root.is_dir():raise ValueError('请选择包含游戏 XML 的目录')
    paths=[p for p in root.rglob('*.xml') if p.name in XML_KINDS]
    paths.sort(key=lambda p:(max([int(v) for v in re.findall(r'(?:^|[/\\])A(\d+)(?:[/\\]|$)',p.relative_to(root).as_posix())] or [0]),p.as_posix()))
    entries={};digest=hashlib.sha256();failed=0;parsed=0
    for path in paths:
        if path.stat().st_size>5_000_000:failed+=1;continue
        blob=path.read_bytes()
        if b'<!DOCTYPE' in blob.upper():failed+=1;continue
        try:
            tree=ET.fromstring(blob);mid=tree.findtext('name/id');title=tree.findtext('name/str')
            if mid is None or not mid.isdigit() or not title:continue
            record={'name':title,'disabled':tree.findtext('disable','false').lower()=='true'}
            if XML_KINDS[path.name]=='map':
                distances=[int(n.text) for n in tree.findall('.//Distance') if n.text and n.text.isdigit()]
                record['lastRewardDistance']=max(distances) if distances else None
                record['infinite']=tree.findtext('IsInfinity','false').lower()=='true'
            entries.setdefault(XML_KINDS[path.name],{})[mid]=record
            digest.update(path.relative_to(root).as_posix().encode());digest.update(hashlib.sha256(blob).digest());parsed+=1
        except (ET.ParseError,ValueError):failed+=1
    if not entries:raise ValueError('没有找到可识别的角色、地图或收藏品名称 XML')
    return {'schema':1,'source':'用户本地游戏 XML 名称快照；可能包含修改内容，非官方完整清单',
            'sourceFiles':parsed,'skipped':failed,'snapshotSha256':digest.hexdigest(),'entries':entries}


def load_names(bundled,local):
    result={}
    for path in (bundled,local):
        if Path(path).exists():
            try:
                for kind,rows in json.loads(Path(path).read_text(encoding='utf-8')).get('entries',{}).items():
                    result.setdefault(kind,{}).update(rows)
            except (ValueError,AttributeError,TypeError):continue
    return result


def entity_name(metadata,kind,identifier):
    value=metadata.get(kind,{}).get(str(identifier))
    return value.get('name') if isinstance(value,dict) else f'{kind} · ID {identifier}（名称未收录）'


def entity_image(directory,kind,identifier):
    """Only resolve manifest-listed thumbnails inside the bundled asset directory."""
    filename=_entity_image_index(str(directory)).get(f'{kind}:{identifier}')
    if filename is None:return None
    from app.image_assets import image_path
    root=Path(directory).resolve();path=image_path(root/filename).resolve()
    return str(path) if path.parent==root and path.is_file() else None


from functools import lru_cache
@lru_cache(maxsize=4)
def _entity_image_index(directory):
    root=Path(directory)
    try:entries=json.loads((root/'manifest.json').read_text(encoding='utf-8')).get('entries',{})
    except (OSError,ValueError):return {}
    result={}
    for key,row in entries.items():
        if not isinstance(row,dict) or not isinstance(row.get('file'),str):continue
        filename=row['file']
        if Path(filename).name==filename and filename not in ('.','..'):result[key]=filename
    return result
