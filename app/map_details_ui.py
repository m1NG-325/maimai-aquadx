"""Embedded, non-modal map route inspector."""
from app.image_assets import image_path
from pathlib import Path
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QScrollArea,QSizePolicy
from app.archive_widgets import ArchiveTable,shown
from app.collection_metadata import entity_image

def map_image(assets,metadata):
    pid=str(metadata.get('lastPlateId') or '')
    if not pid.isdigit():return None
    path=image_path(Path(assets)/f'map-plate-{pid}.png')
    return str(path) if path.is_file() else None

def reward_image(assets,reward,cache=None):
    if assets is None:return None
    root=Path(assets);kind=reward.get('kind');identifier=str(reward.get('elementId') or '')
    mid=reward.get('musicId') if kind=='Challenge' else identifier if kind in ('MusicNew','MapTaskMusic') else None
    if mid is not None and str(mid).isdigit():
        name=f'{int(mid)%10000}.png'
        for folder in ([Path(cache)] if cache is not None else [])+[root.parent/'covers']:
            path=image_path(folder/name)
            if path.is_file():return str(path)
    if not identifier.isdigit():return None
    if kind=='Character':return entity_image(root,'chara',identifier)
    if kind=='Title':return entity_image(root,'title',identifier)
    if kind in ('NamePlate','Frame','Icon'):return entity_image(root,'reward-'+kind,identifier)
    return None

def reward_rows(metadata,current,assets=None,cache=None):
    distance=current.get('distance');valid=isinstance(distance,(int,float))
    rows=[]
    for r in metadata.get('rewards',[]):
        target=r.get('distance');reached=valid and target is not None and distance>=target
        name=r.get('name') or '未知奖励'
        if r.get('musicName') and r['musicName'] not in name:name+=' · '+r['musicName']
        rows.append(dict(distance=target,kind=r.get('kindLabel'),name=name,id=r.get('elementId') or r.get('treasureId'),quantity=r.get('quantity'),state='达到参考距离' if reached else '未达到参考距离' if valid and target is not None else '距离未知',flag=r.get('flag'),_imagePath=reward_image(assets,r,cache),_imageColumn=2,_sort={'distance':target}))
    return rows

def map_panel(owner,metadata,current,assets):
    scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body);layout.setContentsMargins(12,12,12,12);layout.setSpacing(10)
    def text(value,style=''):
        label=QLabel(value);label.setTextFormat(Qt.TextFormat.PlainText);label.setWordWrap(True)
        if style:label.setStyleSheet(style)
        layout.addWidget(label);return label
    title=metadata.get('name') or current.get('name') or f"地图 ID {current.get('mapId')}"
    text(title,'font-size:18px;font-weight:600;')
    path=map_image(assets,metadata)
    if path:
        image=QLabel();pix=QPixmap(path);image.setPixmap(pix.scaled(360,120,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));image.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);image.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(image)
    else:text('该地图未收录名牌板奖励或对应图片。','color:#9cafc7;')
    text(f"地图 ID {current.get('mapId')} · 当前距离 {shown(current.get('distance'))}\n已通关 {shown(current.get('isClear'))} · 已完成 {shown(current.get('isComplete'))} · 锁定 {shown(current.get('isLock'))}")
    end=metadata.get('lastRewardDistance')
    text(f"参考路线：{'无限地图' if metadata.get('infinite') else '最后奖励距离 '+shown(end)}\n最后名牌板：{metadata.get('lastPlateName') or '未收录'} · 参考距离 {shown(metadata.get('lastPlateDistance'))}")
    conditions=metadata.get('unlockConditions',[])
    lines=[f"{r.get('name') or '条件 ID'} · {r.get('id')}" for r in conditions]
    text('开放与解禁条件','font-weight:600;font-size:14px;')
    text(('\n'.join(lines) if lines else 'XML 未列出额外路线条件。')+f"\n开放事件：{metadata.get('openEvent') or '未收录'}（ID {shown(metadata.get('openEventId'))}）\n加成曲组：{metadata.get('bonusMusic') or '未收录'}（ID {shown(metadata.get('bonusMusicId'))}）\n加成倍率原值：{shown(metadata.get('bonusMagnification'))}")
    text('奖励与解禁节点','font-weight:600;font-size:14px;')
    table=ArchiveTable([('距离','distance'),('奖励类型','kind'),('奖励 / 解禁要素','name'),('ID','id'),('数量原值','quantity'),('参考进度','state'),('节点标记原值','flag')]);table.centered_columns={0,3,4};table.table.setIconSize(QSize(72,56));table.set_rows(reward_rows(metadata,current,assets,owner.core.directory/'covers'));table.table.setColumnWidth(0,70);table.table.setColumnWidth(1,95);table.table.setColumnWidth(2,220);table.table.setColumnWidth(5,130);table.setMinimumHeight(310);layout.addWidget(table)
    if not metadata:text('未收录该地图的 XML 路线。可使用“补充本地游戏名称资料”导入游戏目录。')
    text('参考路线来自本地游戏 XML，可能与私服修改不同。距离为游戏原始单位；达到参考距离不代表奖励已实际领取。原始条件 ID 和节点标记未推测其含义。','font-size:11px;color:#9cafc7;')
    scroll.reward_table=table;return scroll
