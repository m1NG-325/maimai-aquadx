"""Translucent native panels over an application-owned painted backdrop."""
from pathlib import Path
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter,QLinearGradient,QColor,QImage
from PySide6.QtWidgets import QWidget

GLASS_STYLE='''
QWidget {background:transparent;color:#ecf1fa;font-family:"Microsoft YaHei";font-size:13px;}
QMainWindow {background:#202a43;}
QLabel {background:transparent;}
QLineEdit,QComboBox,QDoubleSpinBox {background:rgba(18,25,44,155);border:1px solid rgba(212,223,255,45);border-radius:9px;padding:8px;color:#eef2ff;}
QComboBox QAbstractItemView {background:#28334d;color:#eef2ff;selection-background-color:#516581;}
QPushButton {background:rgba(30,42,66,155);border:1px solid rgba(218,227,255,50);border-radius:10px;padding:9px 15px;color:#e7edf9;}
QPushButton:hover {background:rgba(89,112,155,175);border-color:rgba(187,211,255,110);}
QPushButton:disabled {color:#8090a8;}
QListWidget {background:rgba(18,24,43,125);border:1px solid rgba(220,231,255,35);border-radius:16px;padding:8px;}
QListWidget::item {padding:14px 10px;border-radius:10px;}
QListWidget::item:selected {background:rgba(127,166,219,62);color:#b6d4ff;}
QHeaderView::section {background:rgba(25,34,55,160);color:#c4d0e3;padding:11px;border:0;border-bottom:1px solid rgba(222,229,255,45);}
QTableWidget {background:rgba(18,24,41,140);alternate-background-color:rgba(65,77,102,38);border:1px solid rgba(222,229,255,45);border-radius:14px;gridline-color:rgba(224,232,255,25);}
QTableWidget::item {padding:5px;border-bottom:1px solid rgba(224,232,255,22);}
QTableWidget::item:selected {background:rgba(130,167,214,70);}
QGroupBox {background:rgba(25,33,52,125);border:1px solid rgba(218,227,255,45);border-radius:14px;margin-top:14px;padding:16px;}
QGroupBox::title {subcontrol-origin:margin;left:16px;color:#afd2ff;}
QScrollArea {background:rgba(18,24,42,75);border:1px solid rgba(212,224,255,35);border-radius:14px;}
QScrollArea QWidget {background:transparent;}
QCheckBox {padding:6px;}
QLabel#metric {font-size:16px;color:#a9ddd0;padding:10px 14px;background:rgba(20,28,46,140);border:1px solid rgba(213,225,255,50);border-radius:12px;}
QDockWidget {color:#dce9ff;font-weight:600;}
QDockWidget::title {background:rgba(35,47,72,230);padding:9px;border:1px solid rgba(213,225,255,50);}
QTabBar::tab {background:rgba(24,33,53,210);color:#b9c8de;padding:9px 13px;border:1px solid rgba(213,225,255,40);}
QTabBar::tab:selected {background:rgba(86,113,157,200);color:#eff6ff;}
QStatusBar {color:#aab8ce;background:rgba(17,23,39,100);}
QSplitter::handle:vertical {background:rgba(135,165,210,85);margin:2px 30px;border-radius:3px;}
QSplitter::handle:vertical:hover {background:rgba(170,205,255,160);}
QToolTip {background:#27344f;color:#f2f5ff;border:1px solid #7e92b7;padding:8px;}
'''


class GlassBackground(QWidget):
    def __init__(self,assets):
        super().__init__()
        # Use existing game art as a subtle backdrop, not the user's reference screenshot.
        self.art=QImage(str(Path(assets)/'covers/772.png'))
        if not self.art.isNull():self.art=self.art.scaled(32,32,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)

    def paintEvent(self,event):
        p=QPainter(self);p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        gradient=QLinearGradient(0,0,self.width(),self.height());gradient.setColorAt(0,QColor('#526184'));gradient.setColorAt(.45,QColor('#343a58'));gradient.setColorAt(1,QColor('#26374e'))
        p.fillRect(self.rect(),gradient)
        if not self.art.isNull():
            p.setOpacity(.13);p.drawImage(QRectF(0,0,self.width(),self.height()),self.art);p.setOpacity(1)
        p.fillRect(self.rect(),QColor(10,16,32,75));p.end()
