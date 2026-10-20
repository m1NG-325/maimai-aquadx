"""Optional Studio presentation. Installed only by desktop_studio.py."""
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPainter,QLinearGradient
from PySide6.QtWidgets import QWidget,QLabel,QTableWidget,QPushButton,QAbstractItemView

STYLE='''
QWidget{background:transparent;color:#dce2eb;font-family:"Microsoft YaHei UI","Microsoft YaHei";font-size:12px;}
QMainWindow{background:#11151c;}
QLabel{background:transparent;border:0;}
QLabel#brand{font-size:20px;font-weight:600;color:#f4f6fa;padding:4px 0;}
QLabel#pageTitle{font-size:22px;font-weight:600;color:#f1f4fa;padding-top:6px;}
QLabel#pageHint{font-size:11px;color:#929eaf;padding:0 0 8px;}
QLabel#metric{font-size:12px;color:#b9c9df;background:#1b2330;border:1px solid #2b3545;border-radius:8px;padding:10px 14px;}
QLineEdit,QComboBox,QDoubleSpinBox,QSpinBox,QDateEdit{background:#1b222d;border:1px solid #323c4b;border-radius:6px;padding:7px 10px;selection-background-color:#3b5479;color:#e0e6ef;}
QLineEdit:focus,QComboBox:focus,QDoubleSpinBox:focus,QDateEdit:focus{border-color:#8baee8;}
QComboBox::drop-down,QDateEdit::drop-down{border:0;width:24px;}
QComboBox::down-arrow,QDateEdit::down-arrow{image:url(DOWN_ICON);width:10px;height:10px;}
QDoubleSpinBox::up-button,QSpinBox::up-button{width:19px;border:0;subcontrol-origin:border;subcontrol-position:top right;}
QDoubleSpinBox::down-button,QSpinBox::down-button{width:19px;border:0;subcontrol-origin:border;subcontrol-position:bottom right;}
QDoubleSpinBox::up-arrow,QSpinBox::up-arrow{image:url(UP_ICON);width:8px;height:8px;}
QDoubleSpinBox::down-arrow,QSpinBox::down-arrow{image:url(DOWN_ICON);width:8px;height:8px;}
QComboBox QAbstractItemView{background:#202a38;border:1px solid #3b475a;padding:5px;selection-background-color:#334664;color:#e7edf7;}
QPushButton{background:#263244;border:1px solid #3a4960;border-radius:6px;padding:8px 13px;color:#dce7f7;}
QPushButton:hover{background:#334560;border-color:#718eb5;}
QPushButton:pressed{background:#1e2b40;}
QPushButton:disabled{color:#667386;background:#1a212c;border-color:#293342;}
QPushButton#primaryAction{background:#aec9f0;color:#15243a;border-color:#aec9f0;font-weight:600;}
QPushButton#primaryAction:hover{background:#c9ddf8;}
QListWidget{background:rgba(23,29,39,220);border:1px solid #293240;border-radius:10px;padding:8px 6px;outline:0;}
QListWidget::item{height:33px;padding:0 12px;margin:2px 0;border-radius:6px;color:#9eacbf;}
QListWidget::item:hover{background:#242e3c;color:#edf3fa;}
QListWidget::item:selected{background:#2d405b;color:#dae9ff;border-left:3px solid #aec9f0;padding-left:9px;}
QTableWidget{background:#181f2a;alternate-background-color:#1c2431;border:1px solid #2d3848;border-radius:7px;gridline-color:#293444;selection-color:#f4f7fc;}
QTableWidget::item{padding:4px 8px;border:0;}
QTableWidget::item:selected{background:rgba(150,181,227,40);color:#f4f7fc;}
QHeaderView::section{background:#232d3c;color:#aebfd5;padding:9px 8px;border:0;border-bottom:1px solid #3a4659;font-size:11px;font-weight:600;}
QTableCornerButton::section{background:#232d3c;border:0;}
QTabWidget::pane{border:0;background:transparent;}
QTabBar::tab{background:transparent;color:#8f9fb5;padding:9px 12px;margin-right:4px;border:0;border-bottom:2px solid transparent;}
QTabBar::tab:selected{color:#d9e8ff;border-bottom:2px solid #aec9f0;background:rgba(130,165,218,16);}
QTabBar::tab:hover{color:#e0eafa;background:#222e3f;}
QGroupBox{background:rgba(26,34,47,190);border:1px solid #344153;border-radius:8px;margin-top:16px;padding:14px;}
QGroupBox::title{subcontrol-origin:margin;left:14px;color:#bbcde6;padding:0 4px;}
QScrollArea{border:0;background:transparent;}
QScrollArea QWidget{background:transparent;}
QCheckBox{spacing:7px;padding:4px;color:#afbed2;}
QCheckBox::indicator{width:14px;height:14px;border:1px solid #64748c;border-radius:3px;background:#1c2533;}
QCheckBox::indicator:checked{background:#aec9f0;border-color:#aec9f0;image:url(CHECK_ICON);}
QScrollBar:vertical{background:transparent;width:10px;margin:2px;}
QScrollBar::handle:vertical{background:#46556b;border-radius:3px;min-height:28px;}
QScrollBar:horizontal{background:transparent;height:10px;margin:2px;}
QScrollBar::handle:horizontal{background:#46556b;border-radius:3px;min-width:28px;}
QScrollBar::handle:hover{background:#778eae;}
QScrollBar::add-line,QScrollBar::sub-line{width:0;height:0;border:0;background:transparent;}
QScrollBar::add-page,QScrollBar::sub-page{background:transparent;}
QSplitter::handle{background:transparent;}
QSplitter::handle:hover{background:#445b7c;}
QStatusBar{background:#121821;color:#7e8fa8;font-size:11px;border-top:1px solid #283242;padding:3px;}
QDockWidget{color:#c9d9ef;}
QDockWidget::title{background:#222e3f;padding:10px;border:0;}
QToolTip{background:#29374c;color:#eff5ff;border:1px solid #617b9e;padding:8px;}
QTextBrowser{background:#19222f;color:#dce5f2;border:1px solid #344154;border-radius:8px;padding:12px;}
'''

class StudioBackground(QWidget):
    def __init__(self,assets):super().__init__()
    def paintEvent(self,event):
        p=QPainter(self);g=QLinearGradient(0,0,self.width(),self.height());g.setColorAt(0,QColor('#1c2533'));g.setColorAt(.45,QColor('#151c27'));g.setColorAt(1,QColor('#111820'));p.fillRect(self.rect(),g)


def install():
    """Keep the standard entry point and its visuals unchanged."""
    from app import desktop_ui
    from app.desktop_core import ASSETS
    original=desktop_ui.MainWindow
    class StudioWindow(original):
        def __init__(self,core):
            super().__init__(core)
            from app import __version__
            self.setWindowTitle(f'AquaSync Studio · {__version__}')
            style=STYLE
            for token,name in [('CHECK_ICON','check'),('DOWN_ICON','down'),('UP_ICON','up')]:style=style.replace(token,(ASSETS/f'data/report_assets/studio/{name}.svg').as_posix())
            self.setStyleSheet(style)
            outer=self.centralWidget().layout();outer.setContentsMargins(18,12,18,8);outer.setSpacing(12)
            self.nav.setMinimumWidth(174);self.nav.setMaximumWidth(188);self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            for page in range(self.pages.count()):
                layout=self.pages.widget(page).layout()
                if layout:
                    layout.setContentsMargins(20,0,0,0);layout.setSpacing(8)
                    for i,name in [(0,'pageTitle'),(1,'pageHint')]:
                        item=layout.itemAt(i);label=item.widget() if item else None
                        if isinstance(label,QLabel):label.setStyleSheet('');label.setObjectName(name)
            brand=outer.itemAt(0).layout().itemAt(0).widget();brand.setText('AquaSync  /  STUDIO');brand.setStyleSheet('');brand.setObjectName('brand')
            for table in self.findChildren(QTableWidget):
                table.setShowGrid(False);table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                table.verticalHeader().setDefaultSectionSize(38)
            for button in self.findChildren(QPushButton):
                if button.text()=='导入 AquaDX JSON':button.setObjectName('primaryAction')
            self.setStyleSheet(self.styleSheet())
    desktop_ui.GlassBackground=StudioBackground
    desktop_ui.MainWindow=StudioWindow
    return StudioWindow
