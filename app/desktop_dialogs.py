"""Small native dialogs shared by the desktop themes."""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextBrowser


class NoticeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('免费软件提示')
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet('''
            QWidget#noticeCard{background:#1c222c;border:1px solid #384254;border-radius:18px;}
            QLabel{background:transparent;color:#c3d2e8;font-family:"Microsoft YaHei";font-size:13px;}
            QLabel#noticeTitle{font-size:18px;font-weight:600;color:#f1f5fb;}
            QLabel#noticeHeading{font-size:16px;font-weight:600;color:#f1f5fb;}
            QPushButton{font-family:"Microsoft YaHei";font-size:13px;padding:8px 14px;border-radius:10px;}
            QPushButton#noticeClose{background:#3c242c;color:#f3e6eb;border:1px solid #60323e;}
            QPushButton#noticeClose:hover{background:#58313c;}
            QPushButton#noticeConfirm{background:#2f88ed;color:white;border:0;font-weight:600;}
            QPushButton#noticeConfirm:hover{background:#489bf6;}
        ''')
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        card = QWidget(); card.setObjectName('noticeCard'); outer.addWidget(card)
        layout = QVBoxLayout(card); layout.setContentsMargins(22, 18, 22, 20); layout.setSpacing(15)
        header = QHBoxLayout(); layout.addLayout(header)
        titles = QVBoxLayout(); titles.setSpacing(3); header.addLayout(titles, 1)
        title = QLabel('免费软件提示'); title.setObjectName('noticeTitle'); titles.addWidget(title)
        titles.addWidget(QLabel('AquaSync · 本地舞萌查分'))
        close = QPushButton('关闭'); close.setObjectName('noticeClose'); close.clicked.connect(self.reject); header.addWidget(close)
        heading = QLabel('本软件为免费软件'); heading.setObjectName('noticeHeading'); layout.addWidget(heading)
        text = QLabel('如果你是付费获取的，请向卖家申请退款。\n\n请勿将本软件倒卖或冒充官方收费版本。\n软件的正式版本与更新日志均在 GitHub 仓库发布。')
        text.setWordWrap(True); layout.addWidget(text)
        confirm = QPushButton('我知道了'); confirm.setObjectName('noticeConfirm'); confirm.setDefault(True)
        confirm.clicked.connect(self.accept); layout.addWidget(confirm)


class UpdateDialog(QDialog):
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle('检查更新'); self.resize(570, 430)
        self.setStyleSheet('QDialog{background:#1c222c;color:#e7edf8;}')
        layout = QVBoxLayout(self)
        message = {'newer': '发现新版本', 'current': '当前已是最新正式版', 'ahead': '当前版本高于已发布的正式版'}[result['state']]
        title = QLabel(message); title.setStyleSheet('font-size:19px;font-weight:600;padding:8px 0;'); layout.addWidget(title)
        layout.addWidget(QLabel(f"当前版本：{result['current']}    最新正式版：{result['latest']}"))
        notes = QTextBrowser(); notes.setPlainText(result['notes']); layout.addWidget(notes, 1)
        row = QHBoxLayout(); layout.addLayout(row)
        release = QPushButton('打开 Release 下载页面' if result['state']=='newer' else '查看 Release')
        release.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(result['url']))); row.addWidget(release)
        close = QPushButton('关闭'); close.clicked.connect(self.accept); row.addWidget(close)
