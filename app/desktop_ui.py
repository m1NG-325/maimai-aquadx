"""Native Qt widgets, without a browser or HTTP listener."""
import json
import random
from pathlib import Path
from PySide6.QtCore import Qt, QObject, Signal, QRunnable, QThreadPool, QSize, QRect,QEvent,QTimer,QPoint
from PySide6.QtGui import QColor,QIcon,QFontMetrics,QPixmap,QPainter,QFont,QPolygon
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QListWidget, QStackedWidget, QSplitter,
    QDoubleSpinBox, QCheckBox, QScrollArea, QGridLayout, QGroupBox,QDockWidget,QTabWidget,QTabBar,QTextBrowser)
from PySide6.QtWidgets import QStyledItemDelegate,QStyleOptionViewItem,QStyle,QApplication
from app.calculations import rating
from app.parser import DIFFICULTIES
from app.desktop_tools import score_line, today_pick, completion, custom_best, best40
from datetime import date
from app.desktop_core import ASSETS
from app.report_view import ReportCanvas
from app.report_models import b50_report, plate_report
from app.private_catalog import display_catalog
from app.cover_cache import fetch_covers
from app.glass_theme import GLASS_STYLE,GlassBackground
from app.versions import version_order
from app import __version__

STYLE = '''QWidget{background:#101b29;color:#e7f1f8;font-family:"Microsoft YaHei";font-size:12px;}
QMainWindow{background:#0c1520;} QLineEdit,QComboBox,QDoubleSpinBox{background:#182a3a;border:1px solid #355064;border-radius:5px;padding:7px;}
QPushButton{background:#213c4b;border:1px solid #38606a;border-radius:6px;padding:8px 13px;} QPushButton:hover{background:#2b545f;} QPushButton:disabled{color:#71808c;}
QListWidget{background:#111f30;border:0;padding:10px;} QListWidget::item{padding:13px;border-radius:6px;} QListWidget::item:selected{background:#20454b;color:#77e9d8;}
QHeaderView::section{background:#203447;color:#b9d0df;padding:8px;border:0;} QTableWidget{background:#132332;gridline-color:#273d4d;border:1px solid #2b4253;}
QTableWidget::item:selected{background:#265963;} QGroupBox{border:1px solid #314c5c;border-radius:9px;margin-top:13px;padding:15px;} QGroupBox::title{subcontrol-origin:margin;left:12px;color:#75dfd1;}
QScrollArea{border:0;} QCheckBox{padding:6px;} QLabel#metric{font-size:20px;color:#78e5d5;padding:10px;background:#192e3d;border-radius:7px;}
'''

PRIVATE_COLOR='#9bd8ff'
LXNS_COLOR='#f6c481'


class SortItem(QTableWidgetItem):
    def __init__(self,text,key):super().__init__(str(text));self.sort_key=key
    def __lt__(self,other):return self.sort_key<other.sort_key


class SortHeader(QHeaderView):
    """Always show both sort directions; highlight the active direction."""
    def __init__(self,parent):
        super().__init__(Qt.Orientation.Horizontal,parent)
        self.setSectionsClickable(True);self.setSortIndicatorShown(False)
        self.sortIndicatorChanged.connect(lambda *_:self.viewport().update())

    def paintSection(self,painter,rect,index):
        super().paintSection(painter,rect,index)
        painter.save();painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        x,y=rect.right()-12,rect.center().y()
        for order,points in [(Qt.SortOrder.AscendingOrder,[(x-4,y-2),(x+4,y-2),(x,y-7)]),
                             (Qt.SortOrder.DescendingOrder,[(x-4,y+2),(x+4,y+2),(x,y+7)])]:
            active=index==self.sortIndicatorSection() and order==self.sortIndicatorOrder()
            painter.setBrush(QColor('#78e5d5' if active else '#8293ad'))
            painter.drawPolygon(QPolygon([QPoint(a,b) for a,b in points]))
        painter.restore()


def sortable(t):
    t.setHorizontalHeader(SortHeader(t))
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    t.horizontalHeader().setSortIndicator(-1,Qt.SortOrder.AscendingOrder)
    t.setSortingEnabled(True)
    for column in range(t.columnCount()):
        t.horizontalHeaderItem(column).setToolTip('点击按本列排序，再次点击切换升序 / 降序')


class Signals(QObject):
    done = Signal(object)
    failed = Signal(str)


class Worker(QRunnable):
    def __init__(self, work):
        super().__init__()
        self.work, self.signals = work, Signals()

    def run(self):
        try:
            self.signals.done.emit(self.work())
        except Exception as error:
            self.signals.failed.emit(str(getattr(error, 'detail', error)))


def table(headers):
    t = QTableWidget(0, len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    t.setAlternatingRowColors(True)
    t.verticalHeader().hide()
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return t


def fill(t, rows):
    t.setUpdatesEnabled(False)
    t.setRowCount(len(rows))
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setToolTip(str(value))
            t.setItem(i, j, item)
    t.resizeRowsToContents()
    t.setUpdatesEnabled(True)


class CoverDelegate(QStyledItemDelegate):
    """Decode only visible covers; a full library should not load 6000 images."""
    def __init__(self,cache,parent):
        super().__init__(parent);self.cache=Path(cache);self.icons={}

    def sizeHint(self,option,index):
        view=self.parent();width=max(40,view.columnWidth(0)-80)
        height=QFontMetrics(option.font).boundingRect(QRect(0,0,width,10000),Qt.TextFlag.TextWordWrap,str(index.data() or '')).height()
        return QSize(view.columnWidth(0),max(68,height+12))

    def paint(self,painter,option,index):
        mid=index.data(Qt.ItemDataRole.UserRole)
        if mid is None:return super().paint(painter,option,index)
        resource=f'{mid%10000}.png'
        if resource not in self.icons:
            path=self.cache/resource
            if not path.exists():path=ASSETS/'data/report_assets/covers'/resource
            self.icons[resource]=QIcon(str(path)) if path.exists() else QIcon()
        styled=QStyleOptionViewItem(option);self.initStyleOption(styled,index)
        styled.icon=self.icons[resource];styled.decorationSize=QSize(58,58)
        styled.features|=QStyleOptionViewItem.ViewItemFeature.HasDecoration
        style=styled.widget.style() if styled.widget else QApplication.style()
        style.drawControl(QStyle.ControlElement.CE_ItemViewItem,styled,painter,styled.widget)


def cover_icons(t,mids,cache):
    t.setItemDelegateForColumn(0,CoverDelegate(cache,t))
    for i,mid in enumerate(mids):t.item(i,0).setData(Qt.ItemDataRole.UserRole,mid)
    t.resizeRowsToContents()


class ScoreCardDelegate(CoverDelegate):
    def sizeHint(self,option,index):return QSize(360,146)

    def paint(self,painter,option,index):
        r=index.data(Qt.ItemDataRole.UserRole)
        if not r:return
        painter.save();painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect=option.rect.adjusted(4,4,-4,-4);painter.setPen(QColor('#52607a'));painter.setBrush(QColor(25,35,56,190));painter.drawRoundedRect(rect,10,10)
        painter.translate(rect.topLeft());w=rect.width()
        resource=f"{r['musicId']%10000}.png"
        if resource not in self.icons:
            path=self.cache/resource
            if not path.exists():path=ASSETS/'data/report_assets/covers'/resource
            self.icons[resource]=QIcon(str(path))
        self.icons[resource].paint(painter,QRect(12,14,68,68))
        def text(x,y,width,height,value,size=12,color='#e7eefb',bold=False):
            font=QFont('Microsoft YaHei');font.setPixelSize(size);font.setBold(bold);painter.setFont(font);painter.setPen(QColor(color))
            shown=QFontMetrics(font).elidedText(str(value),Qt.TextElideMode.ElideRight,max(0,width))
            painter.drawText(QRect(x,y,max(0,width),height),Qt.AlignmentFlag.AlignVCenter,shown)
        text(92,9,w-104,22,r['title'] or f"待补充曲目 {r['musicId']}",13,bold=True)
        text(92,31,w-104,17,f"ID {r['musicId']} · {r['difficulty']}",10,'#abbcd5')
        text(92,49,w-104,27,f"{r['achievements']:.4f}%",20,'#a9d6ff',True)
        ra=rating(r['ds'],r['achievements'])[0] if r['ds'] is not None else '待核实'
        text(92,77,w-104,19,f"定数 {r['ds'] if r['ds'] is not None else '待核实'} · Rating {ra}",11)
        text(12,99,w-24,18,f"DX {r['dxScore']} · FC {r['fc'] or '—'} / FS {r['fs'] or '—'} · {r['playCount']} 次",11)
        text(12,118,w-24,16,r['version'] or '版本待核实',10,'#abbcd5');painter.restore()


class MainWindow(QMainWindow):
    def __init__(self, core):
        super().__init__()
        self.core, self.data, self.sid, self.plan = core, None, None, None
        self.workers = []
        self.detail_panels = []
        self.page_hidden_details = set()
        self.detail_tab_drag = None
        self.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks | QMainWindow.DockOption.AllowNestedDocks)
        self.setTabPosition(Qt.DockWidgetArea.RightDockWidgetArea, QTabWidget.TabPosition.North)
        self.setWindowTitle(f'AquaSync {__version__} · 本地舞萌查分')
        self.resize(1320, 900)
        self.setMinimumSize(920, 640)
        self.setStyleSheet(GLASS_STYLE)
        central = GlassBackground(ASSETS/'data/report_assets'); self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        bar = QHBoxLayout(); layout.addLayout(bar)
        title = QLabel(f'AquaSync {__version__}  ·  本地舞萌查分'); title.setStyleSheet('font-size:22px;font-weight:600;color:#78e5d5'); bar.addWidget(title)
        bar.addStretch(); self.user = QComboBox(); self.user.setEditable(True); self.user.setMinimumWidth(150); bar.addWidget(self.user)
        self.button(bar, '导入 AquaDX JSON', self.import_file)
        self.button(bar, '加载成绩', self.load)
        self.metric_label = QLabel('先导入成绩，也可以直接使用曲库和计算器。'); self.metric_label.setObjectName('metric');self.metric_label.setWordWrap(True); layout.addWidget(self.metric_label)
        split = QSplitter(); layout.addWidget(split, 1)
        self.nav = QListWidget(); self.nav.setMaximumWidth(160); split.addWidget(self.nav)
        self.pages = QStackedWidget(); split.addWidget(self.pages)
        self.make_b50(); self.make_comparison(); self.make_scores(); self.make_plates(); self.make_library(); self.make_recommend(); self.make_calculator(); self.make_stats(); self.make_game(); self.make_advanced(); self.make_courses(); self.make_sync(); self.make_help()
        self.nav.currentRowChanged.connect(self.switch_page)
        self.nav.setCurrentRow(0)
        self.statusBar().showMessage('本地运行 · 成绩与数据库保存在 '+str(core.directory))
        self.refresh_users()
        if self.core.db.users():
            self.load()

    def button(self, layout, text, function):
        b = QPushButton(text); b.clicked.connect(function); layout.addWidget(b); return b

    def switch_page(self,index):
        self.pages.setCurrentIndex(index)
        if index==0:
            for dock in list(self.page_hidden_details):dock.show()
            self.page_hidden_details.clear()
            QTimer.singleShot(0,self.watch_detail_tabs)
        else:
            for dock in self.detail_panels:
                if not dock.isFloating() and not dock.isHidden():
                    self.page_hidden_details.add(dock);dock.hide()

    def detail_floating_changed(self,dock,floating):
        dock.setWindowOpacity(.94 if floating else 1.)
        if floating:
            if dock in self.page_hidden_details:dock.show()
            self.page_hidden_details.discard(dock)
        elif self.nav.currentRow()!=0:
            self.page_hidden_details.add(dock);dock.hide()
        else:QTimer.singleShot(0,self.watch_detail_tabs)

    def forget_detail(self,dock):
        if dock in self.detail_panels:self.detail_panels.remove(dock)
        self.page_hidden_details.discard(dock)

    def watch_detail_tabs(self):
        titles={d.windowTitle() for d in self.detail_panels if not d.isFloating()}
        for bar in self.findChildren(QTabBar):
            if any(bar.tabText(i) in titles for i in range(bar.count())):
                bar.setProperty('songDetailTabs',True);bar.installEventFilter(self)

    def detach_detail(self,dock,position):
        if dock not in self.detail_panels:return
        dock.setFloating(True);dock.resize(410,760)
        dock.move(position-QPoint(70,15));dock.show();dock.raise_()

    def eventFilter(self,watched,event):
        if isinstance(watched,QTabBar) and watched.property('songDetailTabs'):
            if event.type()==QEvent.Type.MouseButtonPress and event.button()==Qt.MouseButton.LeftButton:
                index=watched.tabAt(event.position().toPoint())
                if index>=0:
                    title=watched.tabText(index)
                    matches=[d for d in self.detail_panels if not d.isFloating() and d.windowTitle()==title]
                    occurrence=sum(watched.tabText(i)==title for i in range(index))
                    if occurrence<len(matches):self.detail_tab_drag=(watched,matches[occurrence],event.globalPosition().toPoint())
            elif event.type()==QEvent.Type.MouseButtonRelease and self.detail_tab_drag:
                bar,dock,start=self.detail_tab_drag;self.detail_tab_drag=None
                position=event.globalPosition().toPoint()
                if (bar is watched and (position-start).manhattanLength()>=QApplication.startDragDistance()
                        and not bar.rect().adjusted(-12,-12,12,12).contains(event.position().toPoint())):
                    # Finish Qt's tab reorder gesture before changing the dock hierarchy.
                    QTimer.singleShot(0,lambda:self.detach_detail(dock,position))
        return super().eventFilter(watched,event)

    def page(self, name, hint):
        self.nav.addItem(name)
        widget = QWidget(); layout = QVBoxLayout(widget); self.pages.addWidget(widget)
        title = QLabel(name); title.setStyleSheet('font-size:22px;font-weight:600'); layout.addWidget(title)
        label = QLabel(hint); label.setWordWrap(True); label.setStyleSheet('color:#b2c0d5;padding:3px 0'); layout.addWidget(label)
        return layout

    def safe(self, fn):
        try:
            return fn()
        except Exception as e:
            QMessageBox.warning(self, '无法完成操作', str(getattr(e, 'detail', e)))

    def background(self, work, done):
        if self.workers:
            self.statusBar().showMessage('正在执行网络操作，请稍候。'); return
        worker = Worker(work); self.workers.append(worker)
        def finish(value):
            self.workers.remove(worker); self.safe(lambda: done(value))
        def failed(message):
            self.workers.remove(worker); QMessageBox.warning(self, '操作失败', message)
        worker.signals.done.connect(finish); worker.signals.failed.connect(failed)
        QThreadPool.globalInstance().start(worker)

    def refresh_users(self):
        previous = self.user.currentText(); self.user.clear()
        for u in self.core.db.users(): self.user.addItem(u['id'])
        self.user.setCurrentText(previous or (self.user.itemText(0) if self.user.count() else 'demo'))

    def uid(self):
        return self.user.currentText().strip() or 'demo'

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择 AquaDX 导出 JSON', '', 'JSON (*.json)')
        if not path: return
        if self.core.db.player(self.uid()) and QMessageBox.question(self, '更新本地快照', '导入会更新玩家 '+self.uid()+' 的本地成绩快照。继续？') != QMessageBox.StandardButton.Yes: return
        def work():
            self.core.import_file(path, self.uid()); self.refresh_users(); self.load()
        self.safe(work)

    def load(self):
        def work():
            self.data = self.core.overview(self.uid()); self.plan = None; self.remote_views = None
            fill(self.sync_table,[]);self.allow_lower.setChecked(False);self.allow_partial.setChecked(False)
            d = self.data; self.metric_label.setText(f"{d['player'].get('name') or self.uid()}    私服 Rating {d['player'].get('rating', '未知')}    最佳谱面 {d['statistics']['charts']}    FC / AP {d['statistics']['fcOrBetter']} / {d['statistics']['apOrBetter']}    曲名已知 {d['privateCatalog']['known']} / {d['statistics']['charts']}")
            self.render_b50(); self.render_comparison(); self.render_scores(); self.render_plates(); self.render_library(); self.render_recommend(); self.render_stats(); self.render_course()
            self.statusBar().showMessage('已加载 '+self.uid()+' · 本地查询无需联网 · 定数为公共参考')
        self.safe(work)

    def make_b50(self):
        layout = self.page('B50', '保留私服 B35 / B15 名单与原报总分；卡片显示参考定数 → 单曲 Rating。点击曲目打开软件内详情页签。')
        self.b50_mode = QComboBox(); self.b50_mode.addItems(['私服原始 B50', '本地分析估算', '落雪导入估算', '旧版 B40 估算']); self.b50_mode.currentIndexChanged.connect(self.render_b50); layout.addWidget(self.b50_mode)
        self.b50_info = QLabel(); self.b50_info.setWordWrap(True); layout.addWidget(self.b50_info)
        self.b50_scroll = QScrollArea(); self.b50_scroll.setWidgetResizable(True); layout.addWidget(self.b50_scroll)
        self.b50_canvas=ReportCanvas(ASSETS/'data/report_assets',self.core.directory/'covers')
        self.b50_canvas.songClicked.connect(self.song_detail);self.b50_scroll.setWidget(self.b50_canvas)
        actions=QHBoxLayout();layout.addLayout(actions)
        self.button(actions, '导出当前 B50 图片', self.export_b50_image)
        self.button(actions,'更新当前图鉴曲绘',self.update_report_covers)
        self.b50_fit=QCheckBox('整图适应窗口');self.b50_fit.setChecked(True);actions.addWidget(self.b50_fit)
        self.b50_fit.setToolTip('勾选后可滚轮缩放、按住左键拖动；重置缩放恢复完整适应。')
        self.b50_fit.toggled.connect(self.set_b50_fit)
        self.set_b50_fit(True)
        self.button(actions,'重置缩放',self.b50_canvas.reset_view)

    def set_b50_fit(self,enabled):
        self.b50_canvas.set_fit_window(enabled)
        policy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff if enabled else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        self.b50_scroll.setHorizontalScrollBarPolicy(policy);self.b50_scroll.setVerticalScrollBarPolicy(policy)

    def render_b50(self):
        if not self.data: return
        mode = self.b50_mode.currentIndex(); view = self.data['b50Views']['source'] if mode==0 else self.data['b50'] if mode==1 else self.data['b50Views']['target'] if mode==2 else best40(self.data['best'])
        self.b50_info.setText(f"旧曲 {view.get('oldRating', '未知')} + 新曲 {view.get('newRating', '未知')} = {view.get('rating', '未知')}" if view.get('available', True) else '快照没有原始分组，请重新导入原始 JSON。')
        if mode==0 and view.get('available'):
            delta=view['calculatedRating']-view['rating'] if view.get('rating') is not None else None
            self.b50_info.setText(self.b50_info.text()+f"（私服原报） · 单曲计算合计 {view['calculatedRating']}"+(f"（差 {delta:+d}）" if delta is not None else '')+f" · 缺定数 {view['uncalculated']} 张")
        labels=['私服原始 B50','本地分析估算','落雪导入估算','旧版 B40 估算']
        catalog=display_catalog(self.core.db.charts(),self.core.db.private_charts())
        self.b50_canvas.set_report(b50_report(self.data,view,catalog,labels[mode]))

    def export_b50_image(self):
        if not self.data: return
        path, _ = QFileDialog.getSaveFileName(self, '导出 B50 图片', 'AquaSync-B50.png', 'PNG (*.png)')
        if path:self.safe(lambda:self.b50_canvas.export_image(path))

    def make_comparison(self):
        layout=self.page('双 B50 对比','按 musicId + 难度对齐，显示分组、名次和达成率变化。私服单曲 Rating 按参考定数计算，落雪侧为估算。')
        self.compare_mode=QComboBox();self.compare_mode.addItems(['落雪导入估算','落雪已有账号估算（先读取备份）']);self.compare_mode.currentIndexChanged.connect(self.render_comparison);layout.addWidget(self.compare_mode)
        self.compare_info=QLabel();layout.addWidget(self.compare_info)
        self.compare_table=table(['曲目 / 难度','私服组 / 名次','私服达成率','落雪组 / 名次','落雪达成率','落雪 Rating','变化']);layout.addWidget(self.compare_table)

    def render_comparison(self):
        if not self.data:return
        views=getattr(self,'remote_views',None) if self.compare_mode.currentIndex() else self.data['b50Views']
        if not views:fill(self.compare_table,[]);self.compare_info.setText('请先到落雪同步读取已有成绩并备份。');return
        comparison=views['comparison'];self.compare_info.setText(f"<b style='color:{PRIVATE_COLOR}'>私服 {views['source']['rating']}</b> → <b style='color:{LXNS_COLOR}'>落雪估算 {views['target']['rating']}</b> · 估算差值 {comparison['ratingDelta']} · 同谱面对齐")
        changes={'same':'一致','source_only':'仅私服','target_only':'仅落雪','group_changed':'分组变化','score_changed':'达成率变化','rank_changed':'名次变化'}
        position=lambda r:('旧曲' if r['group']=='old' else '新曲')+' #'+str(r['position']) if r else '—'
        fill(self.compare_table,[[f"{r['title'] or 'ID '+str(r['musicId'])}\n{DIFFICULTIES[r['level']]}",position(r['source']),f"{r['source']['achievements']:.4f}%" if r['source'] else '—',position(r['target']),f"{r['target']['achievements']:.4f}%" if r['target'] else '—',r['target']['ra'] if r['target'] else '—',' / '.join(changes[k] for k in r['changes'])] for r in comparison['rows']])
        for i,r in enumerate(comparison['rows']):
            for j in (1,2):self.compare_table.item(i,j).setForeground(QColor(PRIVATE_COLOR))
            for j in (3,4,5):self.compare_table.item(i,j).setForeground(QColor(LXNS_COLOR))
            if r['changes']!=['same']:
                for j in range(self.compare_table.columnCount()):self.compare_table.item(i,j).setBackground(QColor('#233a4a'))

    def make_scores(self):
        layout = self.page('成绩查询', '全部最佳成绩，包括落雪未收录谱面。定数、版本为参考信息，未知曲目不猜测对应 ID。')
        controls = QHBoxLayout(); layout.addLayout(controls)
        self.score_query = QLineEdit(); self.score_query.setPlaceholderText('曲名 / musicId'); self.score_query.textChanged.connect(self.render_scores); controls.addWidget(self.score_query)
        self.score_mark = QComboBox(); self.score_mark.addItems(['全部','FC 及以上','AP 及以上','落雪未收录']); self.score_mark.currentIndexChanged.connect(self.render_scores); controls.addWidget(self.score_mark)
        self.button(controls, '导出全部 JSON', self.export_all)
        self.scores = table(['成绩','成绩']);self.scores.horizontalHeader().hide();self.scores.setShowGrid(False);layout.addWidget(self.scores)
        self.scores.setItemDelegate(ScoreCardDelegate(self.core.directory/'covers',self.scores))
        self.scores.cellDoubleClicked.connect(lambda i,j:self.song_detail(self.score_rows[i*2+j]['musicId']) if i*2+j<len(self.score_rows) else None)

    def render_scores(self):
        if not self.data: return
        q = self.score_query.text().casefold().strip(); mark = self.score_mark.currentIndex()
        self.score_rows = [r for r in self.data['privateCatalog']['rows'] if (not q or q in (r['title'] or '').casefold() or q in str(r['musicId'])) and (mark==0 or mark==1 and r['comboStatus']>=1 or mark==2 and r['comboStatus']>=3 or mark==3 and not r['lxnsSupported'])]
        self.score_rows.sort(key=lambda r:-r['achievement'])
        self.scores.setRowCount((len(self.score_rows)+1)//2);self.scores.clearContents()
        for i,r in enumerate(self.score_rows):
            item=QTableWidgetItem(r['title'] or f"ID {r['musicId']}");item.setData(Qt.ItemDataRole.UserRole,r)
            item.setToolTip(f"{r['title'] or '待补充曲目'}\n{r['difficulty']} · {r['version']}\n达成率 {r['achievements']:.4f}% · 定数 {r['ds']}\nDX {r['dxScore']} · FC {r['fc']} / FS {r['fs']} · {r['playCount']} 次")
            self.scores.setItem(i//2,i%2,item)
        self.scores.resizeRowsToContents()

    def export_all(self):
        if not self.data: return
        path, _ = QFileDialog.getSaveFileName(self, '完整私服成绩', 'AquaSync-private.json', 'JSON (*.json)')
        if path: self.safe(lambda: Path(path).write_text(json.dumps(self.data['privateCatalog'],ensure_ascii=False,indent=2),encoding='utf8'))

    def make_plates(self):
        layout = self.page('牌子进度', '私服曲库：日服现行谱面；国服曲库：可怜 bot 国服完成表；含删除曲目：日服现行与历史谱面。进度为参考，不代表游戏授牌。')
        filters=QHBoxLayout();layout.addLayout(filters)
        self.plate_scope=QComboBox();self.plate_scope.addItems(['私服曲库','国服曲库','私服曲库（含删除曲目）']);filters.addWidget(self.plate_scope)
        self.plate_scope.currentIndexChanged.connect(self.render_plates)
        self.plate_version=QComboBox();filters.addWidget(self.plate_version)
        self.plate_mark=QComboBox();self.plate_mark.addItems(['将','极','神','舞舞']);self.plate_mark.setCurrentIndex(1);filters.addWidget(self.plate_mark)
        self.plate_difficulty=QComboBox();self.plate_difficulty.addItems(list(DIFF_NAME for DIFF_NAME in DIFFICULTIES));self.plate_difficulty.setCurrentIndex(3);filters.addWidget(self.plate_difficulty)
        self.plate_only_missing=QCheckBox('只看未完成');filters.addWidget(self.plate_only_missing)
        for widget in [self.plate_version,self.plate_mark,self.plate_difficulty]:widget.currentIndexChanged.connect(self.render_plate_canvas)
        self.plate_only_missing.toggled.connect(self.render_plate_canvas)
        self.plate_scroll=QScrollArea();self.plate_scroll.setWidgetResizable(True)
        self.plate_canvas=ReportCanvas(ASSETS/'data/report_assets',self.core.directory/'covers','plate')
        self.plate_canvas.songClicked.connect(self.song_detail);self.plate_scroll.setWidget(self.plate_canvas)
        self.plate_split=QSplitter(Qt.Orientation.Vertical);self.plate_split.setHandleWidth(9);layout.addWidget(self.plate_split,1)
        top=QWidget();top_layout=QVBoxLayout(top);top_layout.setContentsMargins(0,0,0,0);top_layout.addWidget(self.plate_scroll,1);self.plate_split.addWidget(top)
        actions=QHBoxLayout();top_layout.addLayout(actions)
        self.button(actions,'导出完整完成表 PNG',self.export_plate_image)
        self.button(actions,'更新当前图鉴曲绘',self.update_report_covers)
        self.plate_fit=QCheckBox('整图适应窗口');actions.addWidget(self.plate_fit);self.plate_fit.toggled.connect(self.set_plate_fit);self.plate_fit.setChecked(True)
        self.plate_fit.setToolTip('勾选后可滚轮缩放、按住左键拖动；重置缩放恢复完整适应。')
        self.button(actions,'重置缩放',self.plate_canvas.reset_view)
        self.plate_legacy=QWidget();legacy=QVBoxLayout(self.plate_legacy);legacy.setContentsMargins(0,0,0,0)
        self.button(actions,'显示 / 隐藏总览表',self.toggle_plate_overview)
        self.plate_split.addWidget(self.plate_legacy);self.plate_legacy.hide()
        self.plate_tables_split=QSplitter(Qt.Orientation.Vertical);self.plate_tables_split.setHandleWidth(9);legacy.addWidget(self.plate_tables_split)
        self.plates = table(['版本','将','极','神','舞舞']);self.plate_tables_split.addWidget(self.plates)
        self.plates.cellDoubleClicked.connect(self.plate_detail)
        missing=QWidget();missing_layout=QVBoxLayout(missing);missing_layout.setContentsMargins(0,0,0,0)
        self.plate_label = QLabel('双击上方进度查看未完成曲目');missing_layout.addWidget(self.plate_label)
        self.plate_missing = table(['曲目','难度','ID']);missing_layout.addWidget(self.plate_missing)
        self.plate_tables_split.addWidget(missing);self.plate_tables_split.setSizes([180,180])

    def set_plate_fit(self,enabled):
        self.plate_canvas.set_fit_window(enabled)
        policy=Qt.ScrollBarPolicy.ScrollBarAlwaysOff if enabled else Qt.ScrollBarPolicy.ScrollBarAsNeeded
        self.plate_scroll.setHorizontalScrollBarPolicy(policy);self.plate_scroll.setVerticalScrollBarPolicy(policy)

    def toggle_plate_overview(self):
        show=not self.plate_legacy.isVisible();self.plate_legacy.setVisible(show)
        if show:self.plate_split.setSizes([550,300]);self.plate_tables_split.setSizes([150,150])

    def render_plates(self):
        if not self.data: return
        self.active_plate_data=dict(self.data)
        key=('jp','cn','jp_history')[self.plate_scope.currentIndex()]
        self.active_plate_data.update(self.data['plateScopes'][key])
        self.plate_scope.setToolTip(self.active_plate_data['plateDescription'])
        self.plate_names = list(self.active_plate_data['plates'])
        fill(self.plates, [[v]+[f"{m['completed']} / {m['total']} · {m['percent']}%" if m['supported'] else '不支持' for m in self.active_plate_data['plates'][v].values()] for v in self.plate_names])
        fill(self.plate_missing, [])
        previous=self.plate_version.currentText();self.plate_version.blockSignals(True);self.plate_version.clear();self.plate_version.addItems(self.plate_names)
        self.plate_version.setCurrentText(previous if previous in self.plate_names else (self.plate_names[-1] if self.plate_names else ''));self.plate_version.blockSignals(False)
        self.render_plate_canvas()

    def render_plate_canvas(self):
        if not self.data or not self.plate_version.currentText():return
        model=plate_report(self.active_plate_data,self.core.db.charts(),self.plate_version.currentText(),self.plate_mark.currentText(),self.plate_difficulty.currentIndex(),self.plate_only_missing.isChecked())
        self.plate_canvas.set_report(model)

    def export_plate_image(self):
        if not self.plate_canvas.model:return
        path,_=QFileDialog.getSaveFileName(self,'导出完成表','AquaSync-plate.png','PNG (*.png)')
        if path:self.safe(lambda:self.plate_canvas.export_image(path))

    def update_report_covers(self):
        ids=[]
        if self.b50_canvas.model:ids += [r['musicId'] for group in ('old','new') for r in self.b50_canvas.model[group] if r.get('title')]
        if self.plate_canvas.model:ids += [r['music_id'] for g in self.plate_canvas.model['groups'] for r in g['charts']]
        if not ids:return
        self.statusBar().showMessage('正在缓存公开曲绘，只请求歌曲 ID，不上传成绩。')
        def done(result):
            self.b50_canvas.clear_covers();self.plate_canvas.clear_covers()
            self.statusBar().showMessage(f"曲绘缓存：新增 {result['saved']}，已有 {result['skipped']}，暂不可用 {result['failed']}")
        self.background(lambda:fetch_covers(ids,self.core.directory/'covers',ASSETS/'data/report_assets/covers'),done)

    def plate_detail(self, i, j):
        if j==0 or not self.data: return
        version = self.plate_names[i]; mark=['将','极','神','舞舞'][j-1]; progress = self.active_plate_data['plates'][version][mark]
        self.plate_version.setCurrentText(version);self.plate_mark.setCurrentText(mark)
        self.plate_label.setText(f"{version} · {mark} · 剩余 {progress['remaining']} 张")
        fill(self.plate_missing,[[r['title'],DIFFICULTIES[r['level']],r['musicId']] for r in progress['missing']])

    def make_library(self):
        layout = self.page('曲库 / 随机选曲', '公共和日服参考库，双击曲目查看所有难度。不是私服已安装曲库的证明。')
        controls=QHBoxLayout(); layout.addLayout(controls)
        self.library_query=QLineEdit(); self.library_query.setPlaceholderText('曲名或 musicId'); controls.addWidget(self.library_query)
        self.library_kind=QComboBox(); self.library_kind.addItems(['全部类型','SD','DX']); controls.addWidget(self.library_kind)
        self.library_diff=QComboBox(); self.library_diff.addItems(['全部难度']+list(DIFFICULTIES)); controls.addWidget(self.library_diff)
        self.minimum=QDoubleSpinBox(); self.minimum.setRange(0,20); self.minimum.setPrefix('最低 '); controls.addWidget(self.minimum)
        self.maximum=QDoubleSpinBox(); self.maximum.setRange(0,20); self.maximum.setValue(20); self.maximum.setPrefix('最高 '); controls.addWidget(self.maximum)
        self.button(controls,'查询',self.render_library); self.button(controls,'随机一张',lambda:self.render_library(True))
        self.library_info=QLabel(); layout.addWidget(self.library_info)
        self.library_table=table(['曲目','类型 / 难度','定数参考','版本','最佳达成率']); layout.addWidget(self.library_table)
        sortable(self.library_table)
        self.library_table.cellDoubleClicked.connect(lambda i,j:self.song_detail(self.library_table.item(i,0).data(Qt.ItemDataRole.UserRole)))
        self.library_kind.currentIndexChanged.connect(lambda _:self.render_library())
        self.library_diff.currentIndexChanged.connect(lambda _:self.render_library())
        self.minimum.valueChanged.connect(lambda _:self.render_library())
        self.maximum.valueChanged.connect(lambda _:self.render_library())
        self.library_search_timer=QTimer(self);self.library_search_timer.setSingleShot(True);self.library_search_timer.setInterval(180)
        self.library_search_timer.timeout.connect(self.render_library)
        self.library_query.textChanged.connect(lambda _:self.library_search_timer.start())

    def render_library(self, random_one=False):
        if hasattr(self,'library_search_timer'):self.library_search_timer.stop()
        def work():
            rows=self.core.library(self.uid(),query=self.library_query.text(),kind=self.library_kind.currentText() if self.library_kind.currentIndex() else '',difficulty=self.library_diff.currentIndex()-1 if self.library_diff.currentIndex() else None,minimum=self.minimum.value(),maximum=self.maximum.value())
            total=len(rows); self.library_display=[random.choice(rows)] if random_one is True and rows else rows
            self.library_info.setText(f"符合条件 {total} 张"+(' · 随机选择' if random_one is True else ''))
            self.library_table.setSortingEnabled(False);self.library_table.setUpdatesEnabled(False)
            self.library_table.setRowCount(len(self.library_display))
            for i,r in enumerate(self.library_display):
                acc=r['score']['achievements'] if r['score'] else None
                values=[(r['title'],r['title'].casefold()),(f"{r['type']} · {r['difficulty']}",(r['type'],r['level_index'])),
                        (r['ds'] if r['ds'] is not None else '待核实',r['ds'] if r['ds'] is not None else -1),
                        (r['version'],version_order(r['version'])),(f'{acc:.4f}%' if acc is not None else '未玩',acc if acc is not None else -1)]
                for j,(value,key) in enumerate(values):
                    item=SortItem(value,key);item.setToolTip(str(value));self.library_table.setItem(i,j,item)
            cover_icons(self.library_table,[r['music_id'] for r in self.library_display],self.core.directory/'covers')
            self.library_table.setSortingEnabled(True);self.library_table.setUpdatesEnabled(True)
        self.safe(work)

    def song_detail(self, mid):
        rows=self.core.library(self.uid()); charts=[r for r in rows if r['music_id']%10000==mid%10000]
        if self.nav.currentRow()==3 and hasattr(self,'active_plate_data'):
            scores={(s['musicId'],s['level']):s for s in self.core.db.player(self.uid())['best']}
            charts=[dict(c,difficulty=DIFFICULTIES[c['level_index']],score=scores.get((c['music_id'],c['level_index']))) for c in self.active_plate_data['plateCatalog'] if c['music_id']%10000==mid%10000]
        if self.data:
            known={(r['music_id'],r['level_index']) for r in charts}
            for score in self.data['privateCatalog']['rows']:
                if score['musicId']%10000==mid%10000 and (score['musicId'],score['level']) not in known:
                    charts.append(dict(music_id=score['musicId'],level_index=score['level'],title=score.get('title') or f'待补充曲目 · ID {mid}',
                        difficulty=score['difficulty'],type='DX' if score['musicId']>=10000 else 'SD',ds=score.get('ds'),version=score.get('version') or '待核实',score=score))
        charts.sort(key=lambda r:(r['score'] is None,r['music_id'],r['level_index']))
        title=charts[0]['title'] if charts else f'待补充曲目 · ID {mid}'
        dock=QDockWidget(title,self);dock.setObjectName(f'song-{mid}-{len(self.detail_panels)}')
        dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea|Qt.DockWidgetArea.BottomDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable|QDockWidget.DockWidgetFeature.DockWidgetMovable|QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        dock.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        scroll=QScrollArea();scroll.setWidgetResizable(True);body=GlassBackground(ASSETS/'data/report_assets');layout=QVBoxLayout(body);scroll.setWidget(body);dock.setWidget(scroll)
        head=QHBoxLayout();layout.addLayout(head)
        cover=QLabel();cover.setFixedSize(112,112)
        path=self.core.directory/'covers'/f'{mid%10000}.png'
        if not path.exists():path=ASSETS/'data/report_assets/covers'/f'{mid%10000}.png'
        pix=QPixmap(str(path))
        if not pix.isNull():cover.setPixmap(pix.scaled(112,112,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        else:cover.setText('暂无封面')
        head.addWidget(cover);name=QLabel(f'{title}\nID {mid}');name.setWordWrap(True);name.setStyleSheet('font-size:17px;font-weight:600');head.addWidget(name,1)
        for r in charts:
            box=QGroupBox(f"{r['type']} · {r['difficulty']}");b=QVBoxLayout(box);layout.addWidget(box)
            info=QLabel(f"参考定数 {r['ds'] if r['ds'] is not None else '待核实'} · {r['version']}");info.setWordWrap(True);b.addWidget(info)
            score=r['score']
            if score:
                ra,rank=rating(r['ds'],score['achievements']) if r['ds'] is not None else (None,rating(1,score['achievements'])[1])
                line=QHBoxLayout();b.addLayout(line)
                value=QLabel(f"{score['achievements']:.4f}%\n单曲 Rating {ra if ra is not None else '待补定数'}");value.setStyleSheet('font-size:18px;color:#b6d4ff');line.addWidget(value,1)
                badge=QLabel();badge.setPixmap(QPixmap(str(ASSETS/f'data/report_assets/rating-rank_{rank}.png')).scaled(76,38,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));line.addWidget(badge)
                marks=QHBoxLayout();b.addLayout(marks)
                for field in ('fc','fs'):
                    icon=QLabel();icon.setPixmap(QPixmap(str(ASSETS/f"data/report_assets/rating-icon_{score.get(field) or 'none'}.png")).scaled(30,30,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));marks.addWidget(icon)
                marks.addWidget(QLabel(f"DX 分 {score['dxScore']} · 游玩 {score['playCount']} 次"),1)
            else:b.addWidget(QLabel('未游玩'))
        if not charts:layout.addWidget(QLabel('缺少可核实元数据；原始成绩已保留。'))
        sources=list(dict.fromkeys(str(r.get('source') or '本地曲库') for r in charts))
        provenance=QLabel('参考元数据：'+'、'.join(sources)+'\n定数所属版本可能与私服不同。');provenance.setObjectName('metadataFooter');provenance.setWordWrap(True);provenance.setStyleSheet('font-size:10px;color:#a5b3ca');layout.addWidget(provenance)
        layout.addStretch()
        previous=next((d for d in reversed(self.detail_panels) if not d.isFloating()),None)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,dock)
        if previous and self.nav.currentRow()==0:self.tabifyDockWidget(previous,dock)
        self.detail_panels.append(dock)
        dock.destroyed.connect(lambda:self.forget_detail(dock))
        dock.topLevelChanged.connect(lambda floating:self.detail_floating_changed(dock,floating))
        if self.nav.currentRow()!=0:dock.setFloating(True)
        dock.setMinimumWidth(330);self.resizeDocks([dock],[390],Qt.Orientation.Horizontal);dock.show();dock.raise_()
        QTimer.singleShot(0,self.watch_detail_tabs)

    def make_recommend(self):
        layout=self.page('推分推荐','按原本地曲库 B35/B15 门槛估算，按所需提升幅度排序；收益是单曲替换值，不可直接相加。')
        self.recommend=table(['曲目 / 难度','定数','当前达成率','目标达成率','目标 Rating','估算收益']); layout.addWidget(self.recommend)
        sortable(self.recommend)

    def render_recommend(self):
        rows=self.data['recommendations'];self.recommend.setSortingEnabled(False);self.recommend.setUpdatesEnabled(False)
        self.recommend.setRowCount(len(rows))
        for i,r in enumerate(rows):
            values=[(f"{r['title']} · {r['difficulty']}",r['title'].casefold()),(r['ds'],r['ds']),
                    (f"{r['achievements']:.4f}%",r['achievements']),(f"{r['goal']}%",r['goal']),
                    (r['targetRating'],r['targetRating']),(f"+{r['estimatedGain']}",r['estimatedGain'])]
            for j,(text,key) in enumerate(values):
                item=SortItem(text,key);item.setToolTip(str(text));self.recommend.setItem(i,j,item)
        cover_icons(self.recommend,[r['musicId'] for r in rows],self.core.directory/'covers')
        self.recommend.setSortingEnabled(True);self.recommend.setUpdatesEnabled(True)

    def make_calculator(self):
        layout=self.page('Rating 计算','达成率按 100.5% 封顶并向下取整；单曲 Rating 不等于总 Rating 增量。')
        line=QHBoxLayout(); layout.addLayout(line)
        self.calc_ds=QDoubleSpinBox(); self.calc_ds.setRange(.1,20); self.calc_ds.setValue(12.7); self.calc_ds.setPrefix('定数 '); line.addWidget(self.calc_ds)
        self.calc_a=QDoubleSpinBox(); self.calc_a.setRange(0,101); self.calc_a.setDecimals(4); self.calc_a.setValue(99.5); self.calc_a.setPrefix('达成率 '); line.addWidget(self.calc_a)
        self.calc_label=QLabel('—'); self.calc_label.setStyleSheet('font-size:40px;color:#78e5d5'); layout.addWidget(self.calc_label)
        self.button(line,'计算',self.calculate); layout.addStretch()

    def calculate(self):
        value,rank=rating(self.calc_ds.value(),self.calc_a.value()); self.calc_label.setText(f"{value} · {rank.upper()}")

    def make_stats(self):
        layout=self.page('成绩统计','统计最佳成绩；累计次数不是出勤日历。')
        self.stats=table(['项目','数量']); layout.addWidget(self.stats)

    def render_stats(self):
        s=self.data['statistics']; fill(self.stats,[['最佳谱面',s['charts']],['累计游玩',s['chartPlayCount']],['FC 及以上',s['fcOrBetter']],['AP 及以上',s['apOrBetter']]]+[[m or '无 FC',n] for m,n in s['marks'].items()]+[[m or '无 FS',n] for m,n in s['fsMarks'].items()])

    def make_game(self):
        layout=self.page('猜歌 / 开字母','本地文字猜歌：随机抽取曲库曲名，开字母显示匹配位置；支持完整曲名作答。')
        self.game_label=QLabel('点击新游戏开始'); self.game_label.setWordWrap(True); self.game_label.setStyleSheet('font-size:22px;color:#78e5d5'); layout.addWidget(self.game_label)
        self.game_hint=QLabel(); layout.addWidget(self.game_hint)
        self.game_input=QLineEdit(); self.game_input.setPlaceholderText('输入一个字母或完整曲名'); layout.addWidget(self.game_input)
        buttons=QHBoxLayout(); layout.addLayout(buttons)
        self.button(buttons,'新游戏',self.new_game); self.button(buttons,'开字母 / 答题',self.answer_game); self.button(buttons,'提示',self.hint_game); self.button(buttons,'揭晓',lambda:self.game_label.setText(getattr(self,'answer',{}).get('title','尚未开始'))); layout.addStretch()

    def new_game(self):
        choices=list({r['music_id']:r for r in self.core.library(self.uid())}.values())
        if not choices:return
        self.answer=random.choice(choices); self.opened=set(); self.hints=0; self.game_hint.setText(''); self.mask_game()

    def mask_game(self):
        self.game_label.setText(' '.join(c if c.isspace() or c.casefold() in self.opened else '□' for c in self.answer['title']))

    def answer_game(self):
        if not hasattr(self,'answer'):return
        value=self.game_input.text().strip().casefold(); self.game_input.clear()
        if value==self.answer['title'].casefold():self.game_label.setText('答对了！ '+self.answer['title'])
        elif len(value)==1:self.opened.add(value);self.mask_game()
        else:self.game_hint.setText('答案不对，可以继续开字母。')

    def hint_game(self):
        if not hasattr(self,'answer'):return
        hints=[self.answer['version'],f"谱面类型 {self.answer['type']}",f"曲名长度 {len(self.answer['title'])}",f"musicId {self.answer['music_id']}"]
        self.game_hint.setText(hints[min(self.hints,len(hints)-1)]);self.hints+=1

    def make_advanced(self):
        layout=self.page('进阶查分工具','分数线容错、今日舞萌、条件完成表和自选 Best 列表。公式和筛选功能参照 KarenBot 的公开舞萌模块，定数及物量仍为参考。')
        first=QHBoxLayout();layout.addLayout(first)
        self.line_id=QLineEdit('772');self.line_id.setPlaceholderText('musicId');first.addWidget(self.line_id)
        self.line_diff=QComboBox();self.line_diff.addItems(list(DIFFICULTIES));self.line_diff.setCurrentIndex(2);first.addWidget(self.line_diff)
        self.line_goal=QDoubleSpinBox();self.line_goal.setRange(0,101);self.line_goal.setDecimals(4);self.line_goal.setValue(100.5);first.addWidget(self.line_goal)
        self.button(first,'分数线容错',self.calc_score_line);self.button(first,'今日舞萌',self.today)
        self.advanced_info=QLabel('输入曲目 ID 和目标达成率计算 TAP GREAT / BREAK 50 落容错。');self.advanced_info.setWordWrap(True);layout.addWidget(self.advanced_info)
        second=QHBoxLayout();layout.addLayout(second)
        self.advanced_query=QLineEdit();self.advanced_query.setPlaceholderText('曲名、版本、谱师或曲师关键词');second.addWidget(self.advanced_query)
        self.advanced_goal=QComboBox();self.advanced_goal.addItems(['FC','AP','FSD','SSS','SSS+']);second.addWidget(self.advanced_goal)
        self.button(second,'条件完成 / 未完成表',self.advanced_completion)
        self.best_mark=QComboBox();self.best_mark.addItems(['全部成绩','FC','AP']);second.addWidget(self.best_mark)
        self.button(second,'自选 Best 50',self.advanced_best)
        self.advanced_table=table(['曲目','难度','定数参考','成绩 / 状态','说明']);layout.addWidget(self.advanced_table)

    def calc_score_line(self):
        def work():
            mid=int(self.line_id.text());diff=self.line_diff.currentIndex()
            chart=next((r for r in self.core.library(self.uid()) if r['music_id']==mid and r['level_index']==diff),None)
            if chart is None:raise ValueError('未找到该曲目和难度')
            value=score_line(chart.get('notes'),self.line_goal.value())
            self.advanced_info.setText(f"{chart['title']} · {DIFFICULTIES[diff]}\n允许 TAP GREAT 约 {value['maxTapGreat']:.2f} 个，每个损失 {value['tapGreatLossPercent']:.5f}%。"+(f" BREAK 50 落等价于 {value['break50Equivalent']:.3f} 个 TAP GREAT（-{value['break50LossPercent']:.5f}%）。" if value['break50Equivalent'] is not None else ' 无 BREAK。'))
        self.safe(work)

    def today(self):
        def work():
            value=today_pick(self.uid(),date.today().isoformat(),self.core.library(self.uid()))
            self.advanced_info.setText(f"{value['date']} · 今日幸运指数 {value['luck']}（娱乐）\n推荐曲目：{value['song']['title']} · {value['song']['difficulty']} · ID {value['song']['music_id']}")
        self.safe(work)

    def advanced_rows(self):
        query=self.advanced_query.text().strip().casefold()
        return [r for r in self.core.library(self.uid()) if not query or query in ' '.join(str(r.get(k) or '') for k in ['title','version','designer','artist']).casefold()]

    def advanced_completion(self):
        rows=self.advanced_rows();goal=self.advanced_goal.currentText();result=completion(rows,goal)
        self.advanced_info.setText(f"{goal} 完成 {result['completed']} / {result['total']}，以下为未完成谱面。分母为参考库筛选结果。")
        fill(self.advanced_table,[[r['title'],r['difficulty'],r['ds'],f"{r['score']['achievements']:.4f}%" if r['score'] else '未玩',r.get('designer') or '—'] for r in result['missing']])

    def advanced_best(self):
        if not self.data:return
        mark=self.best_mark.currentText() if self.best_mark.currentIndex() else ''
        rows=custom_best(self.data['best'],mark=mark);query=self.advanced_query.text().strip().casefold()
        rows=[r for r in rows if not query or query in (r['title'] or '').casefold() or query in (r['version'] or '').casefold()]
        self.advanced_info.setText(f"自选 Best 列表 {len(rows)} 张，未强制 B35/B15 分组，不代表游戏正式 B50。")
        fill(self.advanced_table,[[r['title'],r['difficulty'],r['ds'],f"{r['achievements']:.4f}%",f"Rating {r['ra']}"] for r in rows])

    def make_courses(self):
        layout=self.page('段位表','段位配置来自 KarenBot 公开资源，具体版本可能与私服不同。展示配置和单曲最佳成绩，不据此判定实际段位合格。')
        self.course_choice=QComboBox();self.course_choice.addItems([c['name'] for c in self.core.courses]);self.course_choice.currentIndexChanged.connect(self.render_course);layout.addWidget(self.course_choice)
        self.course_info=QLabel();self.course_info.setWordWrap(True);layout.addWidget(self.course_info)
        self.course_table=table(['曲目','難度','ID','单曲最佳','FC / FS']);layout.addWidget(self.course_table)
        self.render_course()

    def render_course(self):
        c=self.core.courses[self.course_choice.currentIndex()]
        info=f"初始血量 {c['life']} · 每首回复 {c['recover']} · 扣血 {json.dumps(c['damage'],ensure_ascii=False)}"
        if c['random']:info+=f"\n随机段位：定数范围 {c['lower']}..{c['upper']}，实际选曲由游戏决定。"
        self.course_info.setText(info)
        lookup={(r['musicId'],r['level']):r for r in self.data['best']} if self.data else {}
        rows=[]
        for m in c['musics']:
            r=lookup.get((m['id'],m['difficulty']))
            rows.append([m['name'] or 'ID '+str(m['id']),DIFFICULTIES[m['difficulty']] if m['difficulty']<5 else '特殊',m['id'],f"{r['achievements']:.4f}%" if r else '未玩',f"{r['fc'] or '—'} / {r['fs'] or '—'}" if r else '—'])
        fill(self.course_table,rows)

    def make_sync(self):
        layout=self.page('落雪同步','密钥仅在本次进程中暂存，30 分钟失效。读取并备份后选择成绩；不会自动上传。')
        controls=QHBoxLayout();layout.addLayout(controls)
        self.token=QLineEdit();self.token.setEchoMode(QLineEdit.EchoMode.Password);self.token.setPlaceholderText('落雪个人 API 密钥');controls.addWidget(self.token)
        self.button(controls,'连接',self.connect_lxns);self.button(controls,'断开',self.disconnect_lxns);self.button(controls,'读取 / 备份 / 对比',self.prepare_sync)
        self.sync_info=QLabel('未连接');layout.addWidget(self.sync_info)
        actions=QHBoxLayout();layout.addLayout(actions)
        self.button(actions,'全选差异',lambda:self.select_sync('all'));self.button(actions,'只选新增和提高',lambda:self.select_sync('recommended'));self.button(actions,'清空选择',lambda:self.select_sync('none'))
        self.sync_table=table(['选择','曲目 / 难度','原达成率','新达成率','DX 原 → 新','FC / FS 原 → 新','变化']);layout.addWidget(self.sync_table)
        self.allow_lower=QCheckBox('允许提交含降低字段的成绩（可能影响落雪现有最佳值）');layout.addWidget(self.allow_lower)
        self.allow_partial=QCheckBox('知道有未匹配谱面，只上传已匹配成绩');layout.addWidget(self.allow_partial)
        self.button(layout,'核对并上传所选',self.upload_sync)
        self.button(layout,'导出最近本地备份',self.export_backup)

    def connect_lxns(self):
        token=self.token.text();self.token.clear()
        if not token:return
        def done(value):self.sid,account=value;self.plan=None;self.sync_info.setText('已连接 '+account['name']+' · 好友码 '+str(account['friend_code']))
        self.background(lambda:self.core.lxns.connect(token,self.sid),done)

    def disconnect_lxns(self):
        self.core.lxns.disconnect(self.sid);self.sid=None;self.plan=None;fill(self.sync_table,[]);self.sync_info.setText('已断开，密钥已清除')

    def prepare_sync(self):
        if not self.data:return
        uid=self.uid();payload=self.core.db.player(uid)
        def done(plan):
            self.plan=plan;self.plan_user=uid;self.allow_lower.setChecked(False)
            from app.score_diff import normalize_scores
            from app.private_catalog import display_catalog
            snapshot=self.core.lxns.backups.get(uid,plan['backup']['id'])
            self.remote_views=self.core.lxns.b50_views(payload,display_catalog(self.core.db.charts(),self.core.db.private_charts()),normalize_scores(snapshot['response']))
            self.render_comparison()
            fill(self.sync_table,[['',f"{r['title']} · {r['difficulty']}",str((r.get('before') or {}).get('achievements','无')),str(r['after']['achievements']),f"{(r['before'] or {}).get('dx_score','无')} → {r['after']['dx_score']}",f"{(r['before'] or {}).get('fc') or '—'} / {(r['before'] or {}).get('fs') or '—'} → {r['after']['fc'] or '—'} / {r['after']['fs'] or '—'}",{'new':'新增','higher':'提高','lower':'降低','mixed':'有升有降','same':'相同'}[r['category']]] for r in plan['rows']])
            for i,r in enumerate(plan['rows']):
                item=self.sync_table.item(i,0);item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable);item.setCheckState(Qt.CheckState.Checked if r['recommended'] else Qt.CheckState.Unchecked)
            self.sync_info.setText(f"已备份 {plan['remoteCount']} 张落雪成绩 · 本地备份 {plan['backup']['id']} · 未上传")
        self.background(lambda:self.core.lxns.prepare(payload,self.sid,uid),done)

    def export_backup(self):
        backups=self.core.lxns.backups.list(self.uid())
        if not backups:QMessageBox.information(self,'没有备份','先读取落雪成绩并备份。');return
        path,_=QFileDialog.getSaveFileName(self,'导出最近备份','AquaSync-lxns-backup.json','JSON (*.json)')
        if path:self.safe(lambda:Path(path).write_text(json.dumps(self.core.lxns.backups.get(self.uid(),backups[0]['id']),ensure_ascii=False,indent=2),encoding='utf8'))

    def select_sync(self, mode):
        if not self.plan:return
        for i,r in enumerate(self.plan['rows']):
            checked=mode=='all' and r['category']!='same' or mode=='recommended' and r['recommended']
            self.sync_table.item(i,0).setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.allow_lower.setChecked(False)

    def upload_sync(self):
        if not self.plan:return
        uid=self.uid();plan=self.plan
        if uid!=self.plan_user:QMessageBox.warning(self,'需要重新预览','玩家已切换，请重新读取成绩。');return
        keys=[r['key'] for i,r in enumerate(plan['rows']) if self.sync_table.item(i,0).checkState()==Qt.CheckState.Checked]
        if not keys:return
        if QMessageBox.question(self,'确认上传',f"将 {len(keys)} 张成绩提交到 {plan['account']['name']}（{plan['account']['friend_code']}）。继续？")!=QMessageBox.StandardButton.Yes:return
        partial,lower=self.allow_partial.isChecked(),self.allow_lower.isChecked()
        def done(value):
            self.plan=None;fill(self.sync_table,[]);self.sync_info.setText(f"落雪已确认提交 {value['submitted']} 张。回读核对：{json.dumps(value['verification'],ensure_ascii=False)}")
        self.background(lambda:self.core.lxns.upload(self.core.db.player(uid),self.sid,plan['fingerprint'],partial,True,plan['plan_id'],keys,lower,uid),done)

    def make_help(self):
        from app.credits import CREDITS_HTML
        layout=self.page('功能与数据说明','本地数据设置、计算口径、参考源码与素材来源。')
        storage=QGroupBox('数据目录');group=QVBoxLayout(storage);layout.addWidget(storage)
        row=QHBoxLayout();group.addLayout(row)
        self.directory_display=QLineEdit(str(self.core.directory));self.directory_display.setReadOnly(True);row.addWidget(self.directory_display,1)
        self.button(row,'更改目录并迁移',self.change_data_directory)
        note=QLabel('选择独立空目录；自动迁移成绩、备份、曲库缓存和曲绘，校验成功后切换并记住。旧目录保留副本，落雪连接需重新建立。');note.setWordWrap(True);group.addWidget(note)
        self.help_browser=QTextBrowser();self.help_browser.setOpenExternalLinks(True)
        self.help_browser.setStyleSheet('QTextBrowser{background:rgba(18,24,43,140);border:1px solid #52617a;border-radius:12px;padding:14px;}')
        self.help_browser.setHtml('<style>body{color:#e7edf8;font-size:13px;}a{color:#9bd8ff;}h2{color:#b5d9ff;}p,li{line-height:1.5;}</style>'+CREDITS_HTML)
        layout.addWidget(self.help_browser,1)

    def change_data_directory(self):
        if self.workers:
            QMessageBox.information(self,'操作进行中','请等当前操作完成后再迁移数据。');return
        directory=QFileDialog.getExistingDirectory(self,'选择新的空数据目录',str(self.core.directory.parent))
        if not directory or Path(directory).resolve()==self.core.directory:return
        worker=Worker(lambda:self.core.migrate_directory(directory));self.workers.append(worker)
        self.setEnabled(False);self.statusBar().showMessage('正在复制并校验本地数据，完成后自动切换目录…')
        def finish(core):
            self.workers.remove(worker);self.setEnabled(True);self.safe(lambda:self.use_migrated_core(core))
        def failed(message):
            self.workers.remove(worker);self.setEnabled(True)
            self.statusBar().showMessage('迁移未完成，继续使用原数据目录。')
            QMessageBox.warning(self,'迁移失败',message)
        worker.signals.done.connect(finish);worker.signals.failed.connect(failed)
        QThreadPool.globalInstance().start(worker)

    def use_migrated_core(self,core):
        self.disconnect_lxns();self.core=core;self.remote_views=None
        self.directory_display.setText(str(core.directory))
        for canvas in (self.b50_canvas,self.plate_canvas):canvas.cache=core.directory/'covers';canvas.clear_covers()
        self.scores.setItemDelegate(ScoreCardDelegate(core.directory/'covers',self.scores))
        self.refresh_users()
        if core.db.users():self.load()
        else:self.render_library()
        self.sync_info.setText('数据目录已迁移；连接已清除，请重新连接落雪。')
        self.statusBar().showMessage('迁移完成 · 数据目录：'+str(core.directory)+' · 旧目录已保留副本')

    def closeEvent(self, event):
        if self.workers:
            QMessageBox.information(self,'操作进行中','请等当前操作完成后关闭。');event.ignore();return
        self.core.lxns.disconnect(self.sid);event.accept()
