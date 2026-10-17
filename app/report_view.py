"""Native, scalable report canvases matching the KarenBot image layout."""
import math
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QSize, Signal,QPointF
from PySide6.QtGui import QPainter, QImage, QColor, QFont, QFontMetrics, QPen, QPainterPath,QLinearGradient
from PySide6.QtWidgets import QWidget, QToolTip, QSizePolicy
from app.calculations import rating

COLORS=['#43bd77','#efb535','#ff586d','#a15cdb','#c690e4']
DIFF=['Basic','Advanced','Expert','Master','ReMaster']


class ReportCanvas(QWidget):
    songClicked=Signal(int)

    def __init__(self, assets, cache, kind='b50'):
        super().__init__()
        self.assets=Path(assets);self.cache=Path(cache);self.kind=kind
        self.model=None;self.hitboxes=[];self.images={};self.report_height=1280
        self.fit_window=kind=='b50'
        self.zoom=1.;self.pan=QPointF();self.press_position=None;self.dragged=False
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.setMouseTracking(True)

    def set_report(self,model):
        self.reset_view()
        self.model=model
        if self.kind=='b50':
            old=max(35 if model.get('label')!='旧版 B40 估算' else 25,len(model['old']))
            self.report_height=max(1280,195+math.ceil(old/5)*94+67+math.ceil(max(15,len(model['new']))/5)*94+65)
        else:
            self.report_height=max(1280,210+sum(max(1,math.ceil(len(g['charts'])/12))*90+18 for g in model['groups'])+100)
        self.hitboxes=[];self.updateGeometry();self.fit_height();self.update()

    def sizeHint(self):return QSize(1,1) if self.fit_window else QSize(1280,self.report_height)

    def fit_height(self):
        self.setMinimumWidth(0 if self.fit_window else 640)
        self.setMinimumHeight(0 if self.fit_window else math.ceil(self.report_height*self.width()/1280))

    def set_fit_window(self,enabled):
        self.fit_window=enabled;self.reset_view();self.fit_height();self.updateGeometry();self.update()

    def reset_view(self):
        self.zoom=1.;self.pan=QPointF();self.update()

    def report_transform(self):
        scale=min(self.width()/1280,self.height()/self.report_height) if self.fit_window else self.width()/1280
        if self.fit_window:scale*=self.zoom
        return scale,(self.width()-1280*scale)/2+self.pan.x(),((self.height()-self.report_height*scale)/2+self.pan.y()) if self.fit_window else 0

    def resizeEvent(self,event):super().resizeEvent(event);self.fit_height()

    def image(self,name,cover=False):
        key=('cover:' if cover else '')+name
        if key not in self.images:
            path=self.cache/name if cover and (self.cache/name).exists() else self.assets/('covers' if cover else '')/name
            self.images[key]=QImage(str(path))
        return self.images[key]

    def clear_covers(self):
        self.images={k:v for k,v in self.images.items() if not k.startswith('cover:')};self.update()

    def report_font(self,size,bold=False):
        f=QFont('Microsoft YaHei');f.setPixelSize(size);f.setBold(bold);return f

    def text(self,p,rect,text,size=16,color='#ffffff',bold=False,align=Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter):
        p.setFont(self.report_font(size,bold));p.setPen(QColor(color));p.drawText(QRectF(*rect),align,str(text))

    def sprite(self,p,name,rect):
        image=self.image(name)
        if image.isNull():return False
        p.drawImage(QRectF(*rect),image);return True

    def cover(self,p,mid,rect):
        image=self.image(f'{mid%10000}.png',True)
        if image.isNull():
            p.fillRect(QRectF(*rect),QColor('#adbdcb'))
            self.text(p,rect,'♪',34,'#ffffff',True,Qt.AlignmentFlag.AlignCenter)
        else:p.drawImage(QRectF(*rect),image)

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scale,x,y=self.report_transform();p.translate(x,y);p.scale(scale,scale);self.paint_report(p);p.end()

    def paint_report(self,p):
        background=self.image(('rating' if self.kind=='b50' else 'level')+'-background.png')
        if background.isNull():p.fillRect(QRectF(0,0,1280,self.report_height),QColor('#ffd8e1'))
        else:p.drawImage(QRectF(0,0,1280,self.report_height),background)
        self.hitboxes=[]
        if self.model:
            if self.kind=='b50':self.paint_b50(p)
            else:self.paint_plate(p)
        else:self.text(p,(40,40,1100,80),'导入成绩后生成图鉴',30,'#173b62',True)
        p.fillRect(QRectF(0,self.report_height-55,1280,55),QColor('#063564'))
        self.text(p,(25,self.report_height-55,1230,55),'AquaSync  ·  本地成绩图鉴  |  样式素材：KarenBot',22,bold=True,align=Qt.AlignmentFlag.AlignCenter)

    def paint_b50(self,p):
        m=self.model
        p.setPen(QPen(QColor('#efb438'),4));p.setBrush(QColor('#f8fcff'));p.drawRoundedRect(QRectF(48,38,780,121),8,8)
        p.fillRect(QRectF(56,46,108,104),QColor('#55c1ec'))
        p.setBrush(QColor('#2a80f1'));p.setPen(Qt.PenStyle.NoPen);p.drawEllipse(QRectF(86,56,48,48));p.drawRoundedRect(QRectF(70,102,80,43),20,20)
        p.setBrush(QColor('#b782ed'));p.drawRoundedRect(QRectF(176,48,192,34),5,5)
        self.text(p,(185,48,170,34),'DX RATING  '+str(m.get('rating') if m.get('rating') is not None else '—'),17,bold=True)
        self.text(p,(177,83,630,38),m.get('player','本地玩家'),28,'#111111',True)
        self.text(p,(179,119,635,24),f"[{m['label']}] {m.get('oldRating','—')} + {m.get('newRating','—')} = {m.get('rating','—')}",16,'#44515b',True)
        self.text(p,(48,164,1185,22),'每张卡片显示 定数 → 单曲 Rating；按参考定数计算，原报总分保留。FC / FS 为独立最佳标记。',14,'#344d62')
        y=194
        old_slots=25 if m['label']=='旧版 B40 估算' else 35
        for group,slots in [('old',max(old_slots,len(m['old']))),('new',max(15,len(m['new'])))]:
            if group=='new':
                self.sprite(p,'rating-icon_b15.png',(588,y-2,105,60));y+=62
            rows=m[group]
            for i in range(slots):
                x=46+(i%5)*239;top=y+(i//5)*94
                self.paint_card(p,rows[i] if i<len(rows) else None,x,top)
            y+=math.ceil(slots/5)*94+5

    def paint_card(self,p,r,x,y):
        index=min(r['level'],4) if r else None
        self.sprite(p,'rating-base_'+(DIFF[index] if r else 'None')+'.png',(x,y,238,96))
        if not r:return
        mid=r['musicId'];self.cover(p,mid,(x+11,y+11,72,72))
        self.paint_type_badge(p,r['type'],x+12,y+12)
        self.text(p,(x+90,y+8,139,14),f"#{r['position']}  {mid}",10,bold=True)
        title=r.get('title') or '未知曲目'
        metrics=QFontMetrics(self.report_font(12,True));shown=metrics.elidedText(title,Qt.TextElideMode.ElideRight,137)
        self.text(p,(x+90,y+22,138,16),shown,12,bold=True)
        # The template's white band starts at y=63, not y=72.
        p.save();p.setClipRect(QRectF(x+88,y+35,143,27))
        self.text(p,(x+89,y+35,141,27),f"{r['achievements']:.4f}%",22,bold=True)
        p.restore()
        ds=r.get('ds');ra=r.get('ra');label=f"{ds if ds is not None else '—'}→{ra if ra is not None else '—'}"
        self.text(p,(x+90,y+64,70,22),label,11,COLORS[index],True)
        rank=rating(1,r['achievements'])[1]
        self.sprite(p,'rating-rank_'+rank+'.png',(x+162,y+67.5,30,15))
        for offset,key in [(194,'fc'),(212,'fs')]:self.sprite(p,'rating-icon_'+(r.get(key) or 'none')+'.png',(x+offset,y+67,16,16))
        self.hitboxes.append((QRectF(x,y,238,92),mid,f"{title}\n{r.get('difficulty','')} · 达成率 {r['achievements']:.4f}%\n参考定数 {ds if ds is not None else '待核实'} · Rating {ra if ra is not None else '缺定数'}\nFC {r.get('fc') or '—'} / FS {r.get('fs') or '—'}"))

    def paint_type_badge(self,p,kind,x,y):
        """Native vector lettering stays sharp at screen and export scales."""
        p.save();p.setPen(QPen(QColor('#ffffff'),.8))
        gradient=QLinearGradient(x,y,x,y+13)
        gradient.setColorAt(0,QColor('#fff1a5' if kind=='DX' else '#61d6ff'))
        gradient.setColorAt(1,QColor('#ffad24' if kind=='DX' else '#1684df'))
        p.setBrush(gradient);p.drawRoundedRect(QRectF(x,y,27,13),2,2)
        font=self.report_font(11 if kind=='DX' else 9,True);font.setItalic(kind=='DX')
        path=QPainterPath();path.addText(x+(4 if kind=='DX' else 4.5),y+10,font,'DX' if kind=='DX' else '标准')
        p.setPen(QPen(QColor('#8d4b13' if kind=='DX' else '#1670b5'),.8));p.setBrush(QColor('#ffffff'));p.drawPath(path)
        p.restore()

    def paint_plate(self,p):
        m=self.model
        heading=QPainterPath();heading.addText(56,99,self.report_font(36,True),m['title'])
        p.setPen(QPen(QColor('#e64775'),9,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin));p.setBrush(QColor('#fffaf1'));p.drawPath(heading)
        p.setPen(Qt.PenStyle.NoPen);p.drawPath(heading)
        self.text(p,(54,118,1150,27),f"{m['version']} · {'未完成筛选 · ' if m['onlyMissing'] else ''}总进度 {m['completed']} / {m['total']} · 当前展示 {DIFF[m['difficulty']]} · 分母：{m.get('scopeLabel','原分析曲库')}",14,'#314960',True)
        start=310 if len(m['title'])<9 else 760
        for i,c in enumerate(m['counts']):
            x=start+i*91
            p.fillRect(QRectF(x,68,82,18),QColor('#f1e5f9'))
            p.fillRect(QRectF(x,68,82*c['completed']/c['total'],18),QColor(COLORS[c['level']]))
            self.text(p,(x,92,82,20),f"{c['completed']}/{c['total']}",15,COLORS[c['level']],True,Qt.AlignmentFlag.AlignCenter)
        if not m['supported']:
            self.text(p,(54,175,1100,50),'此版本不支持该牌子',26,'#e64775',True);return
        y=182;color=COLORS[m['difficulty']]
        for group in m['groups']:
            self.sprite(p,'level-level.png',(61,y+4,80,80))
            self.text(p,(64,y+26,74,32),group['level'],23,bold=True,align=Qt.AlignmentFlag.AlignCenter)
            for i,c in enumerate(group['charts']):
                x=163+(i%12)*87;top=y+(i//12)*90
                p.fillRect(QRectF(x,top,80,80),QColor(color));self.cover(p,c['music_id'],(x+4,top+4,72,72))
                self.sprite(p,'rating-type_'+c['type']+'.png',(x+5,top+5,18,9))
                p.fillRect(QRectF(x+44,top,36,15),QColor(color));self.text(p,(x+44,top,35,15),str(c['music_id']),10,bold=True,align=Qt.AlignmentFlag.AlignCenter)
                if c['complete']:
                    p.fillRect(QRectF(x+4,top+4,72,72),QColor(255,255,255,170))
                    self.text(p,(x+5,top+17,70,42),'✓',34,'#16a16d',True,Qt.AlignmentFlag.AlignCenter)
                self.hitboxes.append((QRectF(x,top,80,80),c['music_id'],f"{c['title']}\n{DIFF[c['level_index']]} · {c['level']} / {c['ds']}\n{'已完成' if c['complete'] else '未完成'}"))
            y+=max(1,math.ceil(len(group['charts'])/12))*90+18
        if not m['groups']:self.text(p,(54,200,1100,60),'没有符合条件的谱面',26,'#344d62',True)

    def mouseMoveEvent(self,event):
        if self.fit_window and self.press_position is not None:
            delta=event.position()-self.press_position
            if self.dragged or delta.manhattanLength()>=6:
                self.dragged=True;self.pan=self.press_pan+delta;self.setCursor(Qt.CursorShape.ClosedHandCursor);QToolTip.hideText();self.update();return
        scale,x,y=self.report_transform();pos=(event.position()-self.rect().topLeft())
        from PySide6.QtCore import QPointF
        pos=(pos-QPointF(x,y))/scale
        for rect,mid,text in self.hitboxes:
            if rect.contains(pos):QToolTip.showText(event.globalPosition().toPoint(),text,self);self.setCursor(Qt.CursorShape.PointingHandCursor);return
        self.setCursor(Qt.CursorShape.ArrowCursor);QToolTip.hideText()

    def mouseReleaseEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton:return
        moved=self.dragged;self.press_position=None;self.dragged=False
        if moved:self.setCursor(Qt.CursorShape.ArrowCursor);return
        scale,x,y=self.report_transform()
        from PySide6.QtCore import QPointF
        pos=(event.position()-QPointF(x,y))/scale
        for rect,mid,text in self.hitboxes:
            if rect.contains(pos):self.songClicked.emit(mid);return

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self.press_position=event.position();self.press_pan=QPointF(self.pan);self.dragged=False

    def wheelEvent(self,event):
        if not self.fit_window:return super().wheelEvent(event)
        delta=event.angleDelta().y() or event.pixelDelta().y()
        if not delta:return
        scale,x,y=self.report_transform();point=(event.position()-QPointF(x,y))/scale
        self.zoom=max(.25,min(8.,self.zoom*1.15**(delta/120)))
        new_scale,nx,ny=self.report_transform()
        self.pan+=event.position()-(point*new_scale+QPointF(nx,ny))
        QToolTip.hideText();self.update();event.accept()

    def export_image(self,path):
        image=QImage(1280,self.report_height,QImage.Format.Format_ARGB32);image.fill(Qt.GlobalColor.transparent)
        p=QPainter(image);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform);self.paint_report(p);p.end()
        return image.save(str(path),'PNG')
