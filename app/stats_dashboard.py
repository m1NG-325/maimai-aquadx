"""Compact native statistics dashboard; aggregates imported best charts only."""
from collections import Counter
import math
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QColor,QPainter,QPen,QFont
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QScrollArea,QTableWidget,QTableWidgetItem,QHeaderView,QFrame
from app.calculations import rating
from app.parser import DIFFICULTIES,FC

COLORS=['#89b5ed','#89cbb4','#e9c47d','#c4a4e9','#edb6d5']
RANKS=[('SSS+',100.5),('SSS',100),('SS+',99.5),('SS',99),('S+',98),('S',97),('AAA 及以下',0)]

def summarize(rows):
    marks=Counter();ranks=Counter();kinds=Counter();sync=Counter();difficulties={};values=[]
    for r in rows:
        a=r.get('achievements');a=float(a) if isinstance(a,(int,float)) and math.isfinite(a) and 0<=a<=101 else None
        mark=FC.get(r.get('comboStatus'),r.get('fc') or '') or ''
        marks[mark if mark in ('','fc','fcp','ap','app') else '未知']+=1
        sync[r.get('fs') or '无 FS']+=1
        mid=r.get('musicId',0);kind='宴 / 特殊' if mid>=100000 or r.get('level',0)>=5 else 'DX' if mid>=10000 else '标准'
        kinds[kind]+=1
        if a is not None:
            values.append(a);ranks[next(name for name,low in RANKS if a>=low)]+=1
        else:ranks['达成率未知']+=1
        level=r.get('level',-1);d=difficulties.setdefault(level,{'count':0,'acc':[],'s':0,'fc':0,'ap':0})
        d['count']+=1
        if a is not None:d['acc'].append(a);d['s']+=a>=97
        d['fc']+=mark in ('fc','fcp','ap','app');d['ap']+=mark in ('ap','app')
    return dict(total=len(rows),marks=marks,ranks=ranks,kinds=kinds,sync=sync,difficulties=difficulties,average=sum(values)/len(values) if values else None,highest=max(values) if values else None,known=len(values))

class Distribution(QWidget):
    def __init__(self,donut=False):
        super().__init__();self.rows=[];self.total=0;self.donut=donut;self.setMinimumHeight(230)
    def set_rows(self,rows,total):self.rows=rows;self.total=total;self.update()
    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.total:
            p.setPen(QColor('#8f9fb5'));p.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,'导入成绩后查看分布');return
        if self.donut:
            diameter=min(self.height()-30,self.width()*.48,320);group=min(self.width(),diameter+220);x=max(0,(self.width()-group)/2);y=(self.height()-diameter)/2
            rect=QRectF(x+12,y+12,diameter-24,diameter-24);p.setPen(QPen(QColor('#2b3749'),18));p.drawEllipse(rect)
            angle=90*16
            for title,value,color in self.rows:
                span=round(value/self.total*360*16)
                if span:p.setPen(QPen(QColor(color),18));p.drawArc(rect,angle,-span);angle-=span
            p.setPen(QColor('#e4edf8'));font=QFont(p.font());font.setPixelSize(27);font.setBold(True);p.setFont(font)
            p.drawText(rect,Qt.AlignmentFlag.AlignCenter,str(self.total))
            x=x+diameter+28;width=min(220,self.width()-x)
        else:x=0;width=self.width()
        font=QFont(p.font());font.setPixelSize(12);font.setBold(False);p.setFont(font)
        n=max(1,len(self.rows));step=min(49,(self.height()-12)/n);top=(self.height()-step*n)/2
        maximum=max([r[1] for r in self.rows] or [1]) or 1
        for i,(title,value,color) in enumerate(self.rows):
            y=top+i*step
            if self.donut:
                p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor(color));p.drawRoundedRect(QRectF(x,y+8,7,7),2,2)
                p.setPen(QColor('#b8c9df'));p.drawText(QRectF(x+15,y,width-15,22),Qt.AlignmentFlag.AlignLeft,title)
                p.setPen(QColor('#edf3fb'));p.drawText(QRectF(x+15,y+20,width-15,20),Qt.AlignmentFlag.AlignLeft,f'{value:,}   ·   {value/self.total:.1%}')
            else:
                p.setPen(QColor('#c4d1e4'));p.drawText(QRectF(x,y,110,20),Qt.AlignmentFlag.AlignLeft,title)
                p.drawText(QRectF(x+width-118,y,118,20),Qt.AlignmentFlag.AlignRight,f'{value:,}   {value/self.total:.1%}')
                track=QRectF(x,y+24,width,6);p.setPen(Qt.PenStyle.NoPen);p.setBrush(QColor('#2b3749'));p.drawRoundedRect(track,3,3)
                if value:p.setBrush(QColor(color));p.drawRoundedRect(QRectF(x,y+24,width*value/maximum,6),3,3)

class StatsDashboard(QScrollArea):
    def __init__(self):
        super().__init__();self.setWidgetResizable(True);self.setFrameShape(QFrame.Shape.NoFrame)
        self.content=QWidget();self.setWidget(self.content);outer=QVBoxLayout(self.content);outer.setContentsMargins(0,0,0,0);outer.setSpacing(14)
        self.metrics=QGridLayout();self.metrics.setSpacing(12);outer.addLayout(self.metrics)
        self.tiles=[];self.metric_values=[];self.metric_notes=[]
        for title in ['已玩最佳谱面','累计游玩次数','FC 及以上','AP 及以上']:
            tile=QFrame();tile.setObjectName('statTile');line=QVBoxLayout(tile);line.setContentsMargins(16,12,16,12);line.setSpacing(5)
            caption=QLabel(title);caption.setStyleSheet('color:#9cafc7;font-size:12px;');line.addWidget(caption)
            value=QLabel('—');value.setStyleSheet('color:#e7f0ff;font-size:28px;font-weight:600;');line.addWidget(value)
            note=QLabel('等待导入');note.setStyleSheet('color:#91a6c0;font-size:11px;');line.addWidget(note)
            self.tiles.append(tile);self.metric_values.append(value);self.metric_notes.append(note)
        self.panels=QGridLayout();self.panels.setSpacing(14);outer.addLayout(self.panels,1);self.cards=[]
        def panel(title,hint):
            card=QFrame();card.setObjectName('statPanel');layout=QVBoxLayout(card);layout.setContentsMargins(16,13,16,13);layout.setSpacing(7)
            heading=QLabel(title);heading.setStyleSheet('font-size:15px;font-weight:600;color:#e1eaf7;');layout.addWidget(heading)
            note=QLabel(hint);note.setWordWrap(True);note.setStyleSheet('font-size:11px;color:#91a3bb;');layout.addWidget(note);self.cards.append(card);return layout
        a=panel('评级分布','按每张谱面的最佳达成率统计');self.rank_chart=Distribution();a.addWidget(self.rank_chart,1)
        b=panel('FC / AP 完成情况','各标记独立计数；FC 及以上包含 AP');self.mark_chart=Distribution(True);b.addWidget(self.mark_chart,1)
        c=panel('各难度表现','平均达成率仅计算有有效成绩的谱面')
        self.difficulty=QTableWidget(0,6);self.difficulty.setHorizontalHeaderLabels(['难度','谱面','平均 ACC','S 及以上','FC 及以上','AP'])
        self.difficulty.verticalHeader().hide();self.difficulty.setShowGrid(False);self.difficulty.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.difficulty.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);self.difficulty.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.difficulty.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        self.difficulty.setStyleSheet('QTableWidget{font-size:11px;}QHeaderView::section{padding:8px 4px;font-size:11px;}')
        self.difficulty.setMinimumHeight(215);self.difficulty.setSelectionMode(QTableWidget.SelectionMode.NoSelection);c.addWidget(self.difficulty,1)
        d=panel('谱面概况','仅统计导入快照中的已玩谱面，不代表全曲库完成率')
        self.acc_summary=QLabel('暂无成绩');self.acc_summary.setWordWrap(True);self.acc_summary.setStyleSheet('color:#d1def0;font-size:14px;padding:6px 0;');d.addWidget(self.acc_summary)
        self.kind_chart=Distribution();self.kind_chart.setMinimumHeight(130);d.addWidget(self.kind_chart,1)
        self.fs_summary=QLabel();self.fs_summary.setWordWrap(True);self.fs_summary.setStyleSheet('color:#a4b7d0;font-size:12px;');d.addWidget(self.fs_summary)
        self.setStyleSheet('QFrame#statTile,QFrame#statPanel{background:rgba(29,39,54,210);border:1px solid #344256;border-radius:10px;}')
        self.wide=None;self.arrange()
    def resizeEvent(self,event):super().resizeEvent(event);self.arrange()
    def arrange(self):
        wide=self.viewport().width()>=1000
        if wide==self.wide:return
        self.wide=wide
        for i,tile in enumerate(self.tiles):self.metrics.addWidget(tile,i//(4 if wide else 2),i%(4 if wide else 2))
        for i,card in enumerate(self.cards):self.panels.addWidget(card,i//(2 if wide else 1),i%(2 if wide else 1))
        for i in range(2):self.panels.setColumnStretch(i,1 if wide or i==0 else 0)
    def set_data(self,data):
        self.summary=s=summarize(data.get('privateCatalog',{}).get('rows',[]));total=s['total'];marks=s['marks'];fc=sum(marks[m] for m in ('fc','fcp','ap','app'));ap=marks['ap']+marks['app']
        count=data.get('statistics',{}).get('chartPlayCount',0)
        for label,value in zip(self.metric_values,[total,count,fc,ap]):label.setText(f'{value:,}')
        notes=['每张谱面保留一份最佳成绩','谱面累计次数之和，非出勤天数',f'占已玩谱面 {fc/total:.1%}' if total else '暂无成绩',f'占已玩谱面 {ap/total:.1%}' if total else '暂无成绩']
        for label,note in zip(self.metric_notes,notes):label.setText(note)
        self.rank_chart.set_rows([(name,s['ranks'][name],COLORS[i%5]) for i,(name,_) in enumerate(RANKS)]+([('达成率未知',s['ranks']['达成率未知'],'#7f8da3')] if s['ranks']['达成率未知'] else []),total)
        self.mark_chart.set_rows([(title,marks[key],color) for key,title,color in [('', '无 FC','#62718a'),('fc','FC','#8bcbb0'),('fcp','FC+','#8fbced'),('ap','AP','#e9c47d'),('app','AP+','#dab1ed')]]+([('未知',marks['未知'],'#89919f')] if marks['未知'] else []),total)
        levels=list(range(5))+sorted(k for k in s['difficulties'] if k not in range(5));self.difficulty.setRowCount(len(levels))
        for i,level in enumerate(levels):
            row=s['difficulties'].get(level,{});acc=row.get('acc',[]);values=[DIFFICULTIES[level] if 0<=level<5 else '特殊谱面',row.get('count',0),f'{sum(acc)/len(acc):.4f}%' if acc else '—',row.get('s',0),row.get('fc',0),row.get('ap',0)]
            for j,value in enumerate(values):
                item=QTableWidgetItem(str(value));item.setTextAlignment(Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter if j==0 else Qt.AlignmentFlag.AlignCenter)
                if j==0:item.setForeground(QColor(['#8bcbb0','#e9c47d','#ee9bb0','#c3a0ed','#e1c8ee'][level] if 0<=level<5 else '#b1bed0'))
                self.difficulty.setItem(i,j,item)
        self.acc_summary.setText(f"平均达成率  {s['average']:.4f}%     最高  {s['highest']:.4f}%" if s['known'] else '暂无有效达成率')
        self.kind_chart.set_rows([(name,s['kinds'][name],COLORS[i]) for i,name in enumerate(['标准','DX','宴 / 特殊'])],total)
        self.fs_summary.setText('同步标记  ·  '+'   /   '.join(f'{name.upper() if name != "无 FS" else name} {count:,}' for name,count in sorted(s['sync'].items())))
