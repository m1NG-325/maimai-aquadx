"""Compact native profile summary and image previews; no inferred game enums."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QFrame,QLabel,QVBoxLayout,QHBoxLayout,QGridLayout,QScrollArea,QSplitter
from app.archive_widgets import shown
from app.collection_metadata import entity_name,entity_image
from app.archive_analysis import favorite_music_ids

STYLE='''QFrame#profileTile,QFrame#profilePanel{background:#1d2736;border:1px solid #344256;border-radius:10px;}
QLabel#profileTitle{font-size:23px;font-weight:700;color:#ecf3fc;}
QLabel#profileValue{font-size:22px;font-weight:600;color:#acd0ef;}
QLabel#profileMuted{font-size:11px;color:#95a8bf;}
'''

def plain(text='',name=''):
    label=QLabel(text);label.setTextFormat(Qt.TextFormat.PlainText);label.setWordWrap(True)
    if name:label.setObjectName(name)
    return label

def profile_image(assets,kind,identifier):
    path=entity_image(assets,kind,identifier)
    if path:return path
    from app.map_details_ui import reward_image
    reference={'icon':'Icon','plate':'NamePlate','frame':'Frame'}.get(kind)
    return reward_image(assets,{'kind':reference,'elementId':str(identifier)}) if reference else None

class ProfileHero(QWidget):
    def __init__(self):
        super().__init__();self.setStyleSheet(STYLE);self.grid=QGridLayout(self);self.grid.setContentsMargins(0,0,0,0);self.grid.setSpacing(8)
        self.identity=QFrame();self.identity.setObjectName('profilePanel');row=QHBoxLayout(self.identity);row.setContentsMargins(14,10,14,10)
        self.avatar=QLabel();self.avatar.setFixedSize(58,58);self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter);row.addWidget(self.avatar)
        text=QVBoxLayout();self.name=plain('尚未导入档案','profileTitle');self.dates=plain('导入 AquaDX JSON 后查看个人资料','profileMuted');text.addWidget(self.name);text.addWidget(self.dates);row.addLayout(text,1)
        self.tiles=[];self.values=[]
        for title in ('当前 DX Rating','历史最高 Rating','累计游玩次数','收藏歌曲'):
            tile=QFrame();tile.setObjectName('profileTile');layout=QVBoxLayout(tile);layout.setContentsMargins(14,9,14,9);layout.setSpacing(3)
            layout.addWidget(plain(title,'profileMuted'));value=plain('—','profileValue');layout.addWidget(value);self.tiles.append(tile);self.values.append(value)
        self.wide=None;self.arrange()
    def resizeEvent(self,event):super().resizeEvent(event);self.arrange()
    def arrange(self):
        wide=self.width()>=600
        if self.wide==wide:return
        self.wide=wide
        while self.grid.count():self.grid.takeAt(0)
        count=4 if wide else 2;self.grid.addWidget(self.identity,0,0,1,count)
        for i,tile in enumerate(self.tiles):self.grid.addWidget(tile,1+i//count,i%count)
        for i in range(4):self.grid.setColumnStretch(i,1 if i<count else 0)
    def set_data(self,archive,assets):
        profile=archive.get('sections',{}).get('userData',{})
        self.name.setText(shown(profile.get('userName')) if profile else '尚未导入档案')
        self.dates.setText('最近游玩  '+shown(profile.get('lastPlayDate'))+'   ·   初次游玩  '+shown(profile.get('firstPlayDate')))
        path=profile_image(assets,'icon',profile.get('iconId'));self.avatar.clear()
        if path:self.avatar.setPixmap(QPixmap(path).scaled(56,56,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:self.avatar.setText('档案');self.avatar.setStyleSheet('background:#2c3e52;border-radius:12px;color:#aec9e8;')
        favorites_known=any(key in archive.get('present',[]) for key in ('userFavoriteMusicList','userFavoriteList','userGeneralDataList'))
        values=[profile.get('playerRating'),profile.get('highestRating'),profile.get('playCount'),len(favorite_music_ids(archive)) if favorites_known else None]
        for label,value in zip(self.values,values):label.setText(f'{value:,}' if isinstance(value,(int,float)) else '—')

class EquipmentPanel(QScrollArea):
    def __init__(self):
        super().__init__();self.setWidgetResizable(True);self.setFrameShape(QFrame.Shape.NoFrame);self.setStyleSheet(STYLE)
        body=QWidget();self.setWidget(body);self.body=QVBoxLayout(body);self.body.setContentsMargins(6,0,0,0);self.body.setSpacing(8)
        self.body.addWidget(plain('当前装扮','profileValue'));self.cards=[]
        for key,title,kind in [('iconId','头像','icon'),('nameplateId','名牌底板','nameplate'),('plateId','姓名框','plate'),('titleId','称号','title'),('partnerId','搭档','partner'),('frameId','背景框','frame')]:
            card=QFrame();card.setObjectName('profilePanel');line=QHBoxLayout(card);line.setContentsMargins(10,8,10,8)
            image=QLabel();image.setFixedSize(86,54);image.setAlignment(Qt.AlignmentFlag.AlignCenter);line.addWidget(image)
            column=QVBoxLayout();column.setSpacing(3);heading=plain(title,'profileMuted');name=plain('未提供');column.addWidget(heading);column.addWidget(name);line.addLayout(column,1)
            self.body.addWidget(card);self.cards.append((key,kind,image,name,card))
        self.body.addStretch()
    def set_data(self,profile,names,assets):
        self.has_data=any(profile.get(key) is not None and not (kind=='nameplate' and str(profile.get(key))=='0') for key,kind,*_ in self.cards)
        self.setVisible(self.has_data and (not self.parentWidget() or self.parentWidget().width()>=650))
        for key,kind,image,label,card in self.cards:
            identifier=profile.get(key);card.setVisible(identifier is not None and not (kind=='nameplate' and str(identifier)=='0'));image.clear();path=profile_image(assets,kind,identifier)
            image.setToolTip('使用游戏原始称号底板与配置中的名称、稀有度生成预览' if kind=='title' else '')
            if path:image.setPixmap(QPixmap(path).scaled(86,54,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
            else:image.setText('暂无图片');image.setStyleSheet('color:#778ba4;font-size:11px;')
            label.setText(entity_name(names,kind,identifier) if identifier is not None else '导出未提供');label.setToolTip(f'ID {shown(identifier)}')

class ProfileOverview(QSplitter):
    def __init__(self,table,equipment):
        super().__init__();self.addWidget(table);self.addWidget(equipment);self.setChildrenCollapsible(False);self.setStretchFactor(0,3);self.setStretchFactor(1,2);self.setSizes([620,350]);self.wide=None
    def resizeEvent(self,event):
        super().resizeEvent(event);wide=self.width()>=650
        if wide!=self.wide:
            self.wide=wide;self.widget(1).setVisible(wide and getattr(self.widget(1),'has_data',True))

class CollectionPreview(QFrame):
    def __init__(self):
        super().__init__();self.setObjectName('profilePanel');self.setStyleSheet(STYLE);self.setMaximumWidth(280);self.setMinimumWidth(205)
        layout=QVBoxLayout(self);layout.setContentsMargins(14,14,14,14);layout.setSpacing(10)
        layout.addWidget(plain('收藏预览','profileMuted'));self.image=QLabel();self.image.setMinimumHeight(150);self.image.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(self.image)
        self.name=plain('选择一项查看');self.name.setStyleSheet('font-size:16px;font-weight:600;');layout.addWidget(self.name)
        self.info=plain('','profileMuted');layout.addWidget(self.info);layout.addStretch();self.set_row(None)
    def set_row(self,row):
        self.image.clear()
        self.image.setToolTip(row.get('_imageNote','') if row else '')
        if not row:self.name.setText('暂无符合条件的收藏');self.info.setText('切换类别或调整筛选条件');self.image.setText('暂无预览');return
        self.name.setText(shown(row.get('name')));self.info.setText(f"{shown(row.get('kind'))} · ID {shown(row.get('id'))}\n库存 {shown(row.get('stock'))} · 有效 {shown(row.get('valid'))}")
        if row.get('_imagePath'):self.image.setPixmap(QPixmap(row['_imagePath']).scaled(240,165,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:self.image.setText('该物品类型暂未识别' if str(row.get('kind','')).startswith('未知类型') else '未收录独立图片')

class CollectionSplit(QSplitter):
    def __init__(self,table,preview):
        super().__init__();self.addWidget(table);self.addWidget(preview);self.preview=preview;self.setStretchFactor(0,1);self.setSizes([800,260]);self.setChildrenCollapsible(False)
    def resizeEvent(self,event):
        super().resizeEvent(event);self.preview.setVisible(self.width()>=850)
