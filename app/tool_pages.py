"""Compact native layouts for the guessing game and score utilities."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton, QTabWidget)
from app.parser import DIFFICULTIES


STYLE = '''
QFrame#toolCard{background:#1d2736;border:1px solid #344256;border-radius:12px;}
QLabel#toolEyebrow{color:#95a8bf;font-size:12px;}
QLabel#toolHeading{color:#e5edf7;font-size:18px;font-weight:600;}
QLabel#gamePuzzle{color:#b8d7fb;font-size:28px;font-weight:600;padding:24px;}
QLabel#toolResult{color:#c5dbf4;font-size:16px;padding:12px;}
'''


def label(text, name='toolEyebrow'):
    widget=QLabel(text);widget.setObjectName(name)
    widget.setTextFormat(Qt.TextFormat.PlainText);widget.setWordWrap(True)
    return widget


def card(parent):
    frame=QFrame();frame.setObjectName('toolCard');frame.setStyleSheet(STYLE)
    box=QVBoxLayout(frame);box.setContentsMargins(22,20,22,20);box.setSpacing(14)
    parent.addWidget(frame)
    return box


def action(text, callback, primary=False):
    button=QPushButton(text);button.clicked.connect(callback)
    if primary:button.setObjectName('primaryAction')
    return button


def game_page(owner, layout):
    board=card(layout)
    top=QHBoxLayout();board.addLayout(top)
    top.addWidget(label('文字猜歌', 'toolHeading'));top.addStretch()
    owner.game_status=label('准备开始');top.addWidget(owner.game_status)
    owner.game_label=label('从熟悉的曲库，猜出一首歌。','gamePuzzle')
    owner.game_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    owner.game_label.setMinimumHeight(160);board.addWidget(owner.game_label)
    owner.game_opened=label('已开字符：—');board.addWidget(owner.game_opened)
    row=QHBoxLayout();board.addLayout(row)
    owner.game_input=QLineEdit();owner.game_input.setPlaceholderText('输入一个字符开字母，或输入完整曲名作答')
    owner.game_input.setClearButtonEnabled(True);owner.game_input.returnPressed.connect(owner.answer_game)
    row.addWidget(owner.game_input,1);row.addWidget(action('提交答案',owner.answer_game,True))
    controls=QHBoxLayout();board.addLayout(controls)
    controls.addWidget(action('新的一局',owner.new_game));controls.addWidget(action('查看提示',owner.hint_game))
    controls.addStretch();controls.addWidget(action('揭晓答案',owner.reveal_game))
    hints=card(layout);hints.addWidget(label('线索与反馈','toolHeading'))
    owner.game_hint=label('点击“新的一局”开始。提示会逐步给出版本、谱面类型、曲名长度和 ID。','toolResult')
    hints.addWidget(owner.game_hint)
    hints.addWidget(label('玩法  ·  不区分字母大小写；空格会直接显示；输入框内按 Enter 即可提交。'))
    layout.addStretch(1)


def field(grid, column, title, widget):
    grid.addWidget(label(title),0,column);grid.addWidget(widget,1,column)


def advanced_page(owner, layout, table_factory):
    owner.advanced_tabs=QTabWidget();layout.addWidget(owner.advanced_tabs)
    owner.line_id=QLineEdit('772');owner.line_id.setPlaceholderText('输入 musicId')
    owner.line_diff=QComboBox();owner.line_diff.addItems(list(DIFFICULTIES));owner.line_diff.setCurrentIndex(2)
    owner.line_goal=QDoubleSpinBox();owner.line_goal.setRange(0,101);owner.line_goal.setDecimals(4)
    owner.line_goal.setSuffix(' %');owner.line_goal.setValue(100.5)
    owner.advanced_query=QLineEdit();owner.advanced_query.setClearButtonEnabled(True)
    owner.advanced_query.setPlaceholderText('曲名、版本、谱师或曲师关键词')
    owner.advanced_goal=QComboBox();owner.advanced_goal.addItems(['FC','AP','FSD','SSS','SSS+'])
    owner.best_query=QLineEdit();owner.best_query.setClearButtonEnabled(True)
    owner.best_query.setPlaceholderText('曲名或版本关键词')
    owner.best_mark=QComboBox();owner.best_mark.addItems(['全部成绩','FC','AP'])
    callbacks=[owner.calc_score_line,owner.today,owner.advanced_completion,owner.advanced_best]
    descriptions=[
        '按物量估算目标分数线的容错。计算使用参考谱面物量，不代表实际可混用的判定组合。',
        '每天固定的一首推荐曲目与幸运指数，仅供娱乐。',
        '按关键词缩小参考曲库范围，查看目标完成数量和未完成谱面。',
        '从已导入的最佳成绩中筛选 Best 50；不按 B35 / B15 分组。']
    titles=['分数线容错','今日舞萌','条件完成表','自选 Best 50']
    for index,title in enumerate(titles):
        page=QWidget();box=QVBoxLayout(page);box.setContentsMargins(18,16,18,18);box.setSpacing(14)
        box.addWidget(label(descriptions[index]))
        grid=QGridLayout();grid.setHorizontalSpacing(14);grid.setVerticalSpacing(6);box.addLayout(grid)
        if index==0:
            for col,(name,widget) in enumerate([('曲目 ID',owner.line_id),('难度',owner.line_diff),('目标达成率',owner.line_goal)]):field(grid,col,name,widget)
            owner.line_id.returnPressed.connect(owner.calc_score_line)
        elif index==2:
            field(grid,0,'曲库关键词',owner.advanced_query);field(grid,1,'完成目标',owner.advanced_goal);grid.setColumnStretch(0,3)
            owner.advanced_query.returnPressed.connect(owner.advanced_completion)
        elif index==3:
            field(grid,0,'成绩关键词',owner.best_query);field(grid,1,'完成标记',owner.best_mark);grid.setColumnStretch(0,3)
            owner.best_query.returnPressed.connect(owner.advanced_best)
        row=QHBoxLayout();box.addLayout(row);row.addStretch()
        row.addWidget(action(['计算容错','查看今日推荐','查看未完成谱面','生成 Best 50'][index],callbacks[index],True))
        owner.advanced_tabs.addTab(page,title)
    result=card(layout);owner.advanced_result_title=label('计算结果','toolHeading');result.addWidget(owner.advanced_result_title)
    owner.advanced_info=label('输入曲目 ID、难度和目标达成率，点击“计算容错”。','toolResult')
    owner.advanced_info.setMinimumHeight(80);result.addWidget(owner.advanced_info)
    owner.advanced_table=table_factory(['曲目','难度','定数参考','成绩 / 状态','说明'])
    layout.addWidget(owner.advanced_table,1)
    owner.advanced_empty=label('选择上方工具开始查询。');layout.addWidget(owner.advanced_empty)
    owner.advanced_spacer=QWidget();layout.addWidget(owner.advanced_spacer,1)
    owner.advanced_tabs.currentChanged.connect(owner.switch_advanced)
    owner.switch_advanced(0)
