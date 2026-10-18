"""Reusable native archive tables, calendar-friendly plots and judgement details."""
import csv
import json
import math
from PySide6.QtCore import Qt,QRectF,QPointF,Signal,QSize
from PySide6.QtGui import QColor,QPainter,QPen,QFont,QPixmap,QIcon
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QTableWidget,
    QTableWidgetItem,QHeaderView,QFileDialog,QToolTip,QComboBox,QSplitter)
from app.archive_analysis import number


def shown(value):
    if value is None:return '未提供'
    if isinstance(value,bool):return '是' if value else '否'
    if isinstance(value,(list,dict)):return json.dumps(value,ensure_ascii=False)
    return str(value)


class ArchiveTable(QWidget):
    """Sort/filter the WHOLE data set before pagination; row identity survives both."""
    rowsChanged=Signal()
    def __init__(self,columns,parent=None):
        super().__init__(parent);self.columns=columns;self.rows=[];self.filtered=[];self.page=0;self.limit=100
        self.sort_column=None;self.descending=False;self.centered_columns=set()
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        controls=QHBoxLayout();self.controls=controls;layout.addLayout(controls)
        self.query=QLineEdit();self.query.setPlaceholderText('筛选当前表：名称、ID 或字段值');controls.addWidget(self.query,1)
        self.export_button=QPushButton('导出筛选结果 CSV');self.export_button.clicked.connect(self.export_csv);controls.addWidget(self.export_button)
        self.table=QTableWidget(0,len(columns));layout.addWidget(self.table,1)
        self.footer=QHBoxLayout();layout.addLayout(self.footer)
        self.info=QLabel();self.footer.addWidget(self.info,1)
        self.page_size=QComboBox()
        for count in (10,20,50,100):self.page_size.addItem(f'{count} 条 / 页',count)
        self.page_size.setCurrentIndex(3);self.page_size.setToolTip('每页显示数量，排序与筛选仍作用于全部记录');self.footer.addWidget(self.page_size)
        self.page_buttons=[]
        for title,action in [('上一页',lambda:self.move(-1)),('下一页',lambda:self.move(1))]:
            button=QPushButton(title);button.clicked.connect(action);self.footer.addWidget(button);self.page_buttons.append(button)
        self.page_size.currentIndexChanged.connect(self.change_page_size)
        self.table.setHorizontalHeaderLabels([c[0] for c in columns]);self.table.verticalHeader().hide()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setIconSize(QSize(120,64))
        self.table.setAlternatingRowColors(True);self.table.setWordWrap(False)
        header=self.table.horizontalHeader();header.setSectionsClickable(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive);header.setStretchLastSection(True)
        for i,(label,_) in enumerate(columns):
            self.table.setColumnWidth(i,230 if i==0 else 165 if '时间' in label or '日期' in label else 100)
            self.table.horizontalHeaderItem(i).setToolTip('点击对全部筛选记录排序，再次点击切换方向')
        header.sectionClicked.connect(self.sort)
        self.query.textChanged.connect(self.reset_page)

    def set_compact(self):
        self.limit=500
        self.query.hide();self.page_size.hide()
        for button in self.page_buttons:button.hide()
        self.controls.removeWidget(self.export_button);self.footer.addWidget(self.export_button)
        self.export_button.setText('CSV');self.export_button.setToolTip('导出当前筛选结果')

    def change_page_size(self):
        self.limit=self.page_size.currentData();self.reset_page()

    def fit_content(self,tight=False):
        """Full labels and all judgement rows visible at the initial detail-table size."""
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.resizeColumnsToContents();self.table.resizeRowsToContents()
        for i in range(self.table.columnCount()):self.table.setColumnWidth(i,max(60,self.table.columnWidth(i)))
        for i in range(self.table.rowCount()):self.table.setRowHeight(i,max(34,self.table.rowHeight(i)))
        height=self.table.horizontalHeader().height()+sum(self.table.rowHeight(i) for i in range(self.table.rowCount()))+6
        self.table.setMinimumHeight(height)
        if tight:
            width=sum(self.table.columnWidth(i) for i in range(self.table.columnCount()))+self.table.frameWidth()*2+2
            self.table.setFixedSize(width,height)
            self.setMaximumWidth(max(width,self.layout().minimumSize().width()))
            self.setFixedHeight(self.layout().sizeHint().height())
            self.table.setStyleSheet(self.table.styleSheet()+'QTableWidget{border:0;border-radius:0;background:transparent;}')

    def set_rows(self,rows):
        self.rows=rows;self.reset_page()

    def reset_page(self,*args):self.page=0;self.render()

    def move(self,delta):
        self.page=max(0,min(max(0,(len(self.filtered)-1)//self.limit),self.page+delta));self.render()

    def sort(self,column):
        self.descending=not self.descending if self.sort_column==column else False;self.sort_column=column
        header=self.table.horizontalHeader();header.setSortIndicatorShown(True)
        header.setSortIndicator(column,Qt.SortOrder.DescendingOrder if self.descending else Qt.SortOrder.AscendingOrder)
        self.reset_page()

    def render(self):
        query=self.query.text().casefold().strip()
        self.filtered=[r for r in self.rows if not query or any(query in shown(r.get(k)).casefold() for _,k in self.columns)]
        if self.sort_column is not None:
            key=self.columns[self.sort_column][1]
            def sort_key(row):
                value=row.get('_sort',{}).get(key,row.get(key));n=number(value)
                return (0,n) if n is not None else (1,shown(value).casefold())
            def has_value(row):return row.get('_sort',{}).get(key,row.get(key)) is not None
            present=[r for r in self.filtered if has_value(r)];missing=[r for r in self.filtered if not has_value(r)]
            self.filtered=sorted(present,key=sort_key,reverse=self.descending)+missing
        self.page=min(self.page,max(0,(len(self.filtered)-1)//self.limit))
        rows=self.filtered[self.page*self.limit:(self.page+1)*self.limit]
        self.table.setUpdatesEnabled(False);self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            for j,(_,key) in enumerate(self.columns):
                item=QTableWidgetItem(shown(row.get(key)));item.setToolTip(shown(row.get(key)))
                if j==row.get('_imageColumn',0):
                    if row.get('_imagePaths'):
                        paths=row['_imagePaths'];preview=QPixmap(56*len(paths),56);preview.fill(Qt.GlobalColor.transparent);painter=QPainter(preview)
                        for offset,path in enumerate(paths):
                            pix=QPixmap(path).scaled(56,56,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation);painter.drawPixmap(offset*56,0,pix)
                        painter.end();item.setIcon(QIcon(preview))
                    elif row.get('_imagePath'):item.setIcon(QIcon(row['_imagePath']))
                if j in self.centered_columns:item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setData(Qt.ItemDataRole.UserRole,row.get('_source',row));self.table.setItem(i,j,item)
                if '_level' in row:
                    from app.desktop_ui import difficulty_background
                    item.setBackground(difficulty_background(row['_level']))
            self.table.setRowHeight(i,72 if row.get('_imagePath') else 58 if '_musicId' in row else 35)
        uses_covers=any('_musicId' in r for r in rows)
        if hasattr(self,'cover_delegate') and not uses_covers:
            self.table.setItemDelegateForColumn(0,self.table.itemDelegate())
        if uses_covers:
            from app.desktop_ui import CoverDelegate,DifficultyTableDelegate
            if not hasattr(self,'cover_delegate'):
                from app.desktop_core import ASSETS
                self.cover_delegate=CoverDelegate(ASSETS/'data/report_assets/covers',self.table)
                self.table.setItemDelegateForColumn(0,self.cover_delegate);self.table.setItemDelegate(DifficultyTableDelegate(self.table))
            self.table.setItemDelegateForColumn(0,self.cover_delegate)
            # CoverDelegate expects an integer only in the first column; retain source in other cells.
            for i,row in enumerate(rows):self.table.item(i,0).setData(Qt.ItemDataRole.UserRole,row.get('_musicId'))
        self.table.setUpdatesEnabled(True)
        self.info.setText(f'{len(self.filtered)} 条 · 第 {self.page+1}/{max(1,math.ceil(len(self.filtered)/self.limit))} 页')
        self.rowsChanged.emit()

    def selected_source(self,row):
        if not 0<=row<len(self.filtered)-self.page*self.limit:return None
        value=self.filtered[self.page*self.limit+row]
        return value.get('_source',value)

    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,'保存当前筛选结果','AquaSync-records.csv','CSV (*.csv)')
        if not path:return
        try:
            with open(path,'w',encoding='utf-8-sig',newline='') as stream:
                writer=csv.writer(stream);writer.writerow([title for title,_ in self.columns])
                # Avoid spreadsheet formula execution in names supplied by an export.
                def safe(v):
                    text=shown(v);return "'"+text if text.startswith(('=','+','-','@','\t','\r')) else text
                writer.writerows([[safe(r.get(key)) for _,key in self.columns] for r in self.filtered])
        except OSError as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self,'导出失败',str(exc))


class HistorySplitter(QSplitter):
    """Stack history and details when side-by-side panes would clip their controls."""
    def resizeEvent(self,event):
        orientation=Qt.Orientation.Vertical if self.width()<950 else Qt.Orientation.Horizontal
        if orientation!=self.orientation():
            self.setOrientation(orientation)
            self.setSizes([max(200,self.height()//2)]*2 if orientation==Qt.Orientation.Vertical else [900,500])
        super().resizeEvent(event)


class TimelinePlot(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.points=[];self.label='';self.hit=[];self.integer_ticks=False;self.axis_decimals=1;self.setMinimumHeight(210);self.setMouseTracking(True)

    def set_points(self,points,label):self.points=points;self.label=label;self.update()

    def axis_scale(self,ymin,ymax):
        if self.integer_ticks:
            step=max(1,math.ceil((ymax-ymin)/4));low=math.floor(ymin/step)*step;high=max(low+step,math.ceil(ymax/step)*step)
            return low,high,list(range(high,low-1,-step))
        return ymin,ymax,[ymax-i*(ymax-ymin)/4 for i in range(5)]

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=QRectF(self.rect()).adjusted(66,28,-22,-42);p.fillRect(self.rect(),QColor(18,27,46,140))
        p.setPen(QColor('#c7d8f3'));p.drawText(QRectF(12,2,self.width()-24,24),self.label)
        points=[r for r in self.points if number(r[0]) is not None and number(r[1]) is not None];self.hit=[]
        if not points:
            p.drawText(rect,Qt.AlignmentFlag.AlignCenter,'没有带有效时间的记录；重新导入完整 JSON 后查看');return
        xs=[r[0] for r in points];ys=[r[1] for r in points];xmin,xmax=min(xs),max(xs);ymin,ymax=min(ys),max(ys)
        if ymax==ymin:ymin-=1;ymax+=1
        margin=(ymax-ymin)*.08;ymin-=margin;ymax+=margin
        if min(ys)>=0:ymin=max(0,ymin)
        if self.label.startswith('达成率'):ymax=min(101,ymax)
        ymin,ymax,ticks=self.axis_scale(ymin,ymax)
        for v in ticks:
            y=rect.bottom()-(v-ymin)/(ymax-ymin)*rect.height()
            p.setPen(QPen(QColor('#3c4b67'),1));p.drawLine(QPointF(rect.left(),y),QPointF(rect.right(),y))
            p.setPen(QColor('#b5c7df'));p.drawText(QRectF(0,y-10,61,20),Qt.AlignmentFlag.AlignRight,str(int(v)) if self.integer_ticks else f'{v:.{self.axis_decimals}f}')
        previous=None
        for x,y,label in points:
            position=QPointF(rect.left()+(x-xmin)/(xmax-xmin or 1)*rect.width(),rect.bottom()-(y-ymin)/(ymax-ymin)*rect.height())
            p.setPen(QPen(QColor('#83d9ee'),2))
            if previous is not None:p.drawLine(previous,position)
            p.setBrush(QColor('#a3e7d1'));p.drawEllipse(position,3,3);self.hit.append((position,label));previous=position
        p.setPen(QColor('#b5c7df'))
        p.drawText(QRectF(rect.left(),rect.bottom()+8,rect.width()/2,22),points[0][2].split('\n')[0])
        p.drawText(QRectF(rect.center().x(),rect.bottom()+8,rect.width()/2,22),Qt.AlignmentFlag.AlignRight,points[-1][2].split('\n')[0])

    def nearest_hit(self,position):
        if not self.hit:return None
        item=min(self.hit,key=lambda v:(v[0].x()-position.x())**2+(v[0].y()-position.y())**2)
        distance=(item[0].x()-position.x())**2+(item[0].y()-position.y())**2
        return item if distance<=20**2 else None

    def mouseMoveEvent(self,event):
        item=self.nearest_hit(event.position())
        if item:QToolTip.showText(event.globalPosition().toPoint(),item[1],self)
        else:QToolTip.hideText()
        super().mouseMoveEvent(event)
