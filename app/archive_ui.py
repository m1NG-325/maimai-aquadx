"""AquaSync 2.0 native personal archive pages; all operations are local."""
from app.image_assets import image_path
from datetime import datetime
from PySide6.QtCore import Qt,QDate
from PySide6.QtGui import QColor,QTextCharFormat
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QPushButton,
    QTabWidget,QSplitter,QCheckBox,QCalendarWidget,QDateEdit,QFileDialog,QGroupBox,QGridLayout,QScrollArea,QDoubleSpinBox)
from app.archive_data import NOTE_TYPES,JUDGEMENTS,ITEM_KINDS
from app.archive_analysis import filter_logs,filter_accuracy,log_statistics,rating_candidates,favorite_music_ids,number
from app.archive_widgets import ArchiveTable,TimelinePlot,shown,HistorySplitter
from app.collection_metadata import entity_name,entity_image
from app.parser import DIFFICULTIES,FC
from app.calculations import rating
from app.score_times import LOCAL_TIMEZONE

LABELS={
 'userName':'昵称','isNetMember':'联网会员标记','playCount':'累计游玩次数','playerRating':'原报 DX Rating','highestRating':'原报最高 Rating',
 'playerOldRating':'原报旧曲 Rating','playerNewRating':'原报新曲 Rating','musicRating':'音乐 Rating 原值','gradeRating':'段位 Rating 原值',
 'gradeRank':'段位编码','classRank':'CLASS 编码','courseRank':'课程段位编码','totalAwake':'累计觉醒值',
 'nameplateId':'姓名框 ID','iconId':'头像 ID','trophyId':'奖杯 ID','plateId':'牌子 ID','titleId':'称号 ID','partnerId':'搭档 ID','frameId':'背景框 ID','selectMapId':'选中地图 ID',
 'firstPlayDate':'初次游玩时间','lastPlayDate':'最近游玩时间','lastLoginDate':'最近登录时间','firstGameId':'初次游戏 ID','lastGameId':'最近游戏 ID',
 'firstRomVersion':'初次游戏版本','firstDataVersion':'初次数据版本','lastRomVersion':'最近游戏版本','lastDataVersion':'最近数据版本',
 'lastPlaceId':'最近地点 ID','lastPlaceName':'最近地点名称','lastRegionId':'最近地区 ID','lastRegionName':'最近地区名称','lastCountryCode':'最近国家代码',
 'lastPlayCredit':'最近投币统计原值','lastPlayMode':'最近模式编码','lastSelectCourse':'最近选择课程 ID','lastCountCourse':'最近课程计数',
 'totalDeluxscore':'累计 DX 分','totalHiscore':'累计普通分','totalSync':'累计同步值','totalAchievement':'累计达成率原值',
 'playVsCount':'对战次数','playSyncCount':'同步游玩次数','winCount':'胜利计数','helpCount':'帮助计数','comboCount':'连击计数',
 'point':'点数','totalPoint':'累计点数','currentPlayCount':'当前游玩计数','mapStock':'地图库存','renameCredit':'改名额度原值',
 'noteSpeed':'音符流速档位','slideSpeed':'SLIDE 流速档位','touchSpeed':'TOUCH 流速档位','adjustTiming':'判定调整编码','judgeTiming':'判定时机编码',
 'mirrorMode':'镜像模式','brightness':'亮度档位','headPhoneVolume':'耳机音量','ansVolume':'应答音音量',
 'tapSe':'TAP 音效','breakSe':'BREAK 音效','criticalSe':'Critical 音效','tapDesign':'TAP 外观','holdDesign':'HOLD 外观','slideDesign':'SLIDE 外观',
 'starType':'星星类型','starRotate':'星星旋转','outlineDesign':'外框样式','noteSize':'音符大小','slideSize':'SLIDE 大小','touchSize':'TOUCH 大小',
 'dispCenter':'中央显示模式','dispChain':'连击显示模式','dispRate':'达成率显示模式','dispBar':'信息条显示','dispJudge':'判定显示',
 'dispJudgePos':'判定位置','dispJudgeTouchPos':'TOUCH 判定位置','touchEffect':'TOUCH 效果','trackSkip':'跳过曲目设置',
 'matching':'匹配设置','sortMusic':'曲目排序编码','sortTab':'分类排序编码','optionKind':'设置类型编码',
 'tapHoldVolume':'TAP/HOLD 音量','breakVolume':'BREAK 音量','slideVolume':'SLIDE 音量','touchVolume':'TOUCH 音量',
 'touchHoldVolume':'TOUCH HOLD 音量','exVolume':'EX 音量','damageSeVolume':'受击音量','breakSlideVolume':'BREAK SLIDE 音量','slideSe':'SLIDE 音效','exSe':'EX 音效',
 'submonitorAchive':'副屏达成率','submonitorAnimation':'副屏动画','submonitorAppeal':'副屏展示','outFrameType':'外框类型',
 'characterId':'角色 ID','level':'等级','awakening':'觉醒状态原值','useCount':'使用次数','count':'持有计数','favorite':'收藏标记',
 'nextAwake':'下一觉醒值','nextAwakePercent':'下一觉醒进度原值','distance':'行进距离','isClear':'已通关','isComplete':'已完成','isLock':'锁定',
 'courseId':'课程 ID','gateId':'门 ID','bestAchievement':'最佳总达成率','bestAchievementDate':'最佳达成率时间','bestDeluxscore':'最佳 DX 分',
 'bestDeluxscoreDate':'最佳 DX 分时间','clearDate':'通关时间','isLastClear':'最近一次通关','totalRestlife':'累计剩余血量原值','totalRestLife':'累计剩余血量原值',
 'totalDeluxscore':'累计 DX 分','intimateLevel':'亲密度等级','intimateCountRewarded':'已领奖计数','bonusId':'奖励 ID','isCurrent':'当前奖励',
 'isGateFound':'已发现门','isKeyFound':'已发现钥匙','isInfoWatched':'已查看信息','seasonId':'赛季 ID','rank':'排名','recordDate':'记录日期','rewardGet':'奖励已领取',
 'rate':'当前对战 Rate','maxRate':'最高对战 Rate','classValue':'当前 CLASS 原值','maxClassValue':'最高 CLASS 原值',
 'totalWinNum':'累计胜场','totalLoseNum':'累计负场','winNum':'当前胜场计数','loseNum':'当前负场计数','maxWinNum':'最高胜场计数','maxLoseNum':'最高负场计数',
 'npcTotalWinNum':'NPC 累计胜场','npcTotalLoseNum':'NPC 累计负场','npcWinNum':'NPC 胜场计数','npcLoseNum':'NPC 负场计数','npcMaxWinNum':'NPC 最高胜场计数','npcMaxLoseNum':'NPC 最高负场计数',
}
NOTE_LABELS={'tap':'TAP','hold':'HOLD','slide':'SLIDE','touch':'TOUCH','break':'BREAK'}
EQUIPMENT={'nameplateId':'nameplate','plateId':'plate','iconId':'icon','titleId':'title','partnerId':'partner','frameId':'frame','selectMapId':'map'}
OTHER_SECTIONS={'userActList':'活动记录（原始编码）','userRegionsList':'地区游玩记录','userChargeList':'付费项目库存',
    'userCardList':'角色卡记录','userPrintDetailList':'打印记录（已剔除设备序列号）','mapEncountNpcList':'地图 NPC 记录','userGeneralDataList':'扩展记录'}


def label(key):
    if key in LABELS:return LABELS[key]
    for suffix,title in [('Deluxscore','累计 DX 分'),('Highscore','累计普通分'),('Sync','累计同步值'),('Achievement','累计达成率原值')]:
        if key.startswith('total') and key.endswith(suffix):return key[5:-len(suffix)]+' '+title
    return key+'（原始字段）'


def percent(raw):
    value=number(raw,0);return f'{value/10000:.4f}%' if value is not None else None


def diff_name(level):return DIFFICULTIES[level] if isinstance(level,int) and 0<=level<5 else f'特殊难度 {level}'


def mark(row):
    raw=row.get('comboStatus')
    return (FC[raw] or '—') if raw in FC else '未提供' if raw is None else f'未知({raw})'



class ArchivePages:
    def __init__(self,owner):
        self.owner=owner;self.archive={};self.sections={};self.logs=[];self.names={};self.charts=[];self.filtered=[];self.progress_views={}
        self.make_history();self.make_rating();self.make_progress();self.make_profile()
        for index,title in [(13,'游玩历史与判定'),(14,'Rating 走势'),(15,'冒险与养成'),(16,'个人档案与收藏')]:
            self.owner.nav.item(index).setText(title);self.owner.nav.item(index).setToolTip(title)
        for page in range(13,17):
            for view in self.owner.pages.widget(page).findChildren(QLabel):view.setTextFormat(Qt.TextFormat.PlainText)
        self.refresh()

    def make_history(self):
        layout=self.owner.page('游玩历史与判定','逐局记录只覆盖导出保留的日志；最佳成绩页仍是各谱面 Best。缺失时间不推测，空白日期不代表没有游玩。')
        self.history_hint=QLabel();self.history_hint.setWordWrap(True);layout.addWidget(self.history_hint)
        controls=QHBoxLayout();layout.addLayout(controls)
        self.history_query=QLineEdit();self.history_query.setPlaceholderText('曲名或 musicId');controls.addWidget(self.history_query,1)
        self.history_diff=QComboBox();self.history_diff.addItems(['全部难度',*DIFFICULTIES,'特殊谱面']);controls.addWidget(self.history_diff)
        self.date_filter=QCheckBox('按日期');controls.addWidget(self.date_filter)
        self.start=QDateEdit();self.end=QDateEdit()
        for view in (self.start,self.end):view.setCalendarPopup(True);view.setDisplayFormat('yyyy-MM-dd');controls.addWidget(view)
        self.only_new=QCheckBox('只看刷新纪录');controls.addWidget(self.only_new)
        reset=QPushButton('重置');reset.clicked.connect(self.reset_filters);controls.addWidget(reset)
        self.history_tabs=QTabWidget();layout.addWidget(self.history_tabs,1)
        records=QWidget();r=QVBoxLayout(records);self.history_tabs.addTab(records,'逐局记录')
        split=HistorySplitter();r.addWidget(split,1)
        self.history_table=ArchiveTable([('曲目','title'),('游玩时间','time'),('难度','difficulty'),('定数','ds'),('达成率','acc'),('DX 分','dx'),('FC / AP','mark'),('FAST / LATE','timing'),('DX Rating 变化','delta')]);split.addWidget(self.history_table)
        self.history_table.centered_columns=set(range(1,len(self.history_table.columns)))
        details=QWidget();detail=QVBoxLayout(details);detail.setContentsMargins(12,12,12,12);detail.setSpacing(8)
        self.play_scroll=QScrollArea();self.play_scroll.setWidgetResizable(True);self.play_scroll.setWidget(details)
        self.play_scroll.setMinimumWidth(460);split.addWidget(self.play_scroll);split.setSizes([900,500]);split.setChildrenCollapsible(False)
        head=QHBoxLayout();head.setSpacing(12);detail.addLayout(head)
        self.play_cover=QLabel();self.play_cover.setFixedSize(76,76);head.addWidget(self.play_cover)
        titles=QVBoxLayout();head.addLayout(titles,1)
        self.play_title=QLabel('选择一条记录查看当局判定');self.play_title.setWordWrap(True);self.play_title.setStyleSheet('font-size:17px;font-weight:600;');titles.addWidget(self.play_title)
        self.play_meta=QLabel();self.play_meta.setWordWrap(True);self.play_meta.setStyleSheet('color:#b7c9e1;');titles.addWidget(self.play_meta)
        accuracy=QHBoxLayout();accuracy.setSpacing(10);detail.addLayout(accuracy)
        self.play_accuracy=QLabel();self.play_accuracy.setStyleSheet('font-size:28px;font-weight:700;color:#afd9ff;');accuracy.addWidget(self.play_accuracy)
        self.play_rank=QLabel();accuracy.addWidget(self.play_rank);accuracy.addStretch()
        self.play_fc=QLabel();accuracy.addWidget(self.play_fc);self.play_mark=QLabel();accuracy.addWidget(self.play_mark)
        self.play_values={};grid=QGridLayout();grid.setSpacing(8);detail.addLayout(grid)
        for i,(key,title) in enumerate([('ds','参考定数'),('ra','单曲 Rating'),('dx','DX 分'),('combo','最大连击 / 总连击'),('fast','FAST'),('late','LATE')]):
            tile=QWidget();tile.setObjectName('playMetric');tile.setStyleSheet('QWidget#playMetric{background:rgba(25,33,52,125);border:1px solid rgba(218,227,255,45);border-radius:8px;}');tile_layout=QVBoxLayout(tile);tile_layout.setContentsMargins(8,6,8,6);tile_layout.setSpacing(3)
            caption=QLabel(title);caption.setStyleSheet('color:#b7c9e1;font-size:11px;');tile_layout.addWidget(caption)
            value=QLabel('—');value.setStyleSheet('font-size:15px;font-weight:600;');value.setWordWrap(True);tile_layout.addWidget(value)
            self.play_values[key]=value;grid.addWidget(tile,i//3,i%3)
        self.play_info=QLabel();self.play_info.setWordWrap(True);self.play_info.setStyleSheet('color:#b7c9e1;');detail.addWidget(self.play_info)
        self.play_detail_tabs=QTabWidget();self.play_detail_tabs.setStyleSheet('QTabWidget::pane{border:0;}');detail.addWidget(self.play_detail_tabs)
        self.play_judgements=ArchiveTable([('音符\\判定','note'),('CP','CriticalPerfect'),('P','Perfect'),('Great','Great'),('Good','Good'),('Miss','Miss')]);self.play_detail_tabs.addTab(self.play_judgements,'音符判定')
        self.play_raw=ArchiveTable([('当局字段','field'),('原值','value')]);self.play_detail_tabs.addTab(self.play_raw,'完整字段')
        self.play_judgements.centered_columns=set(range(6))
        self.play_judgements.set_compact();self.play_raw.set_compact()
        self.play_judgements.table.setStyleSheet('QHeaderView::section{padding:6px 8px;font-size:12px;}')
        self.play_judgements.table.horizontalHeaderItem(0).setToolTip('列：判定；行：音符。点击表头排序。')
        self.play_raw.table.setColumnWidth(0,170);self.play_raw.table.setMinimumHeight(220)
        detail.addStretch()
        self.history_table.rowsChanged.connect(self.clear_play)
        self.history_table.table.cellClicked.connect(self.show_play)
        self.history_table.table.cellDoubleClicked.connect(lambda row,col:self.open_song(self.history_table.selected_source(row)))
        calendar_page=QWidget();cal=QVBoxLayout(calendar_page);self.history_tabs.addTab(calendar_page,'游玩日历')
        self.calendar_summary=QLabel();self.calendar_summary.setWordWrap(True);cal.addWidget(self.calendar_summary)
        self.calendar=QCalendarWidget();self.calendar.setGridVisible(True);self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        header_format=QTextCharFormat();header_format.setBackground(QColor('#283c56'));header_format.setForeground(QColor('#e4edfa'));self.calendar.setHeaderTextFormat(header_format)
        self.calendar.clicked.connect(self.select_day)
        self.calendar_panels=QSplitter(Qt.Orientation.Vertical);cal.addWidget(self.calendar_panels,1)
        self.day_plot=TimelinePlot();self.day_plot.integer_ticks=True;self.day_plot.setMinimumHeight(160);self.calendar_panels.addWidget(self.day_plot)
        self.calendar_bottom=QSplitter();self.calendar_panels.addWidget(self.calendar_bottom);self.calendar_bottom.addWidget(self.calendar)
        self.calendar.setStyleSheet('QCalendarWidget QAbstractItemView{background:#1e2c43;color:#ecf1fa;selection-background-color:#547d97;}')
        self.day_table=ArchiveTable([('日期','day'),('游玩记录数','count')]);self.calendar_bottom.addWidget(self.day_table)
        self.calendar_bottom.setSizes([650,650]);self.calendar_panels.setSizes([340,360])
        self.day_table.centered_columns={0,1};self.day_table.table.cellDoubleClicked.connect(self.select_day_row)
        stats_page=QWidget();stats=QVBoxLayout(stats_page);self.history_tabs.addTab(stats_page,'判定与节奏分析')
        acc_controls=QHBoxLayout();stats.addLayout(acc_controls)
        self.acc_filter=QCheckBox('按 ACC 区间分析');acc_controls.addWidget(self.acc_filter)
        self.acc_min=QDoubleSpinBox();self.acc_max=QDoubleSpinBox()
        for view in (self.acc_min,self.acc_max):view.setRange(0,101);view.setDecimals(4);view.setSuffix('%');view.setSingleStep(.1);view.setMinimumWidth(140)
        self.acc_max.setValue(101);acc_controls.addWidget(QLabel('最低'));acc_controls.addWidget(self.acc_min)
        acc_controls.addWidget(QLabel('最高'));acc_controls.addWidget(self.acc_max);acc_controls.addStretch()
        self.judge_summary=QLabel();self.judge_summary.setWordWrap(True);stats.addWidget(self.judge_summary)
        stats_content=QWidget();stats_layout=QVBoxLayout(stats_content);stats_layout.setContentsMargins(0,0,0,0)
        stats_scroll=QScrollArea();stats_scroll.setWidgetResizable(True);stats_scroll.setWidget(stats_content);stats_scroll.setStyleSheet('QScrollArea{border:0;background:transparent;}');stats.addWidget(stats_scroll,1)
        self.judge_table=ArchiveTable([('音符\\判定','note'),*[(j,j) for j in JUDGEMENTS],('字段覆盖记录数','coverage')]);stats_layout.addWidget(self.judge_table,0,Qt.AlignmentFlag.AlignLeft);stats_layout.addStretch()
        self.judge_table.centered_columns=set(range(7))
        self.judge_table.page_size.hide()
        for button in self.judge_table.page_buttons:button.hide()
        self.judge_table.table.horizontalHeaderItem(6).setToolTip('覆盖数顺序：CriticalPerfect / Perfect / Great / Good / Miss；未提供的字段不计入覆盖。')
        stats_note=QLabel('判定直接汇总原始计数，不据此重算达成率；缺失字段不当作零。ACC区间包含两端，仅影响本页分析；FAST占比只使用同时提供FAST/LATE的记录。');stats_note.setWordWrap(True);stats.addWidget(stats_note)
        for signal in (self.acc_filter.toggled,self.acc_min.valueChanged,self.acc_max.valueChanged):signal.connect(self.render_judgements)
        for signal in (self.history_query.textChanged,self.history_diff.currentIndexChanged,self.date_filter.toggled,self.start.dateChanged,self.end.dateChanged,self.only_new.toggled):signal.connect(self.render_history)

    def make_rating(self):
        layout=self.owner.page('Rating 与单曲走势','曲线只展示日志中记录的数值；有日志缺口时不代表完整成长史。单曲 Rating 使用当前参考定数，可能与当时私服不同。')
        controls=QHBoxLayout();layout.addLayout(controls)
        self.rating_metric=QComboBox();self.rating_metric.addItems(['DX Rating（afterDeluxRating）','基础 Rating（afterRating）']);controls.addWidget(self.rating_metric)
        self.trend_song=QComboBox();self.trend_song.setMinimumWidth(280);self.trend_song.setMaximumWidth(650);controls.addWidget(self.trend_song,1)
        self.trend_filtered=QCheckBox('使用历史页筛选');self.trend_filtered.setToolTip('使用游玩历史页的曲名、难度、日期和新纪录筛选范围');controls.addWidget(self.trend_filtered)
        self.trend_acc_controls=QWidget();acc_line=QHBoxLayout(self.trend_acc_controls);acc_line.setContentsMargins(0,0,0,0);layout.addWidget(self.trend_acc_controls)
        self.trend_acc_filter=QCheckBox('按 ACC 区间查看');acc_line.addWidget(self.trend_acc_filter)
        self.trend_acc_min=QDoubleSpinBox();self.trend_acc_max=QDoubleSpinBox()
        for view in (self.trend_acc_min,self.trend_acc_max):view.setRange(0,101);view.setDecimals(4);view.setSuffix('%');view.setSingleStep(.1);view.setMinimumWidth(140)
        self.trend_acc_min.setValue(97);self.trend_acc_filter.setChecked(True);self.trend_acc_max.setValue(101);acc_line.addWidget(QLabel('最低'));acc_line.addWidget(self.trend_acc_min)
        acc_line.addWidget(QLabel('最高'));acc_line.addWidget(self.trend_acc_max);acc_line.addStretch()
        dates=QHBoxLayout();layout.addLayout(dates)
        self.trend_date_filter=QCheckBox('按日期区间');dates.addWidget(self.trend_date_filter)
        self.trend_start=QDateEdit();self.trend_end=QDateEdit()
        for title,view in [('开始',self.trend_start),('结束',self.trend_end)]:
            dates.addWidget(QLabel(title));view.setCalendarPopup(True);view.setDisplayFormat('yyyy-MM-dd');dates.addWidget(view)
        dates.addStretch()
        self.rating_summary=QLabel();self.rating_summary.setWordWrap(True);layout.addWidget(self.rating_summary)
        split=QSplitter(Qt.Orientation.Vertical);layout.addWidget(split,1)
        self.rating_chart_tabs=QTabWidget();split.addWidget(self.rating_chart_tabs)
        self.rating_plot=TimelinePlot();self.rating_plot.integer_ticks=True;self.song_plot=TimelinePlot();self.song_plot.axis_decimals=4;self.rating_plot.setMinimumHeight(140);self.song_plot.setMinimumHeight(140);self.rating_chart_tabs.addTab(self.rating_plot,'账号 Rating 走势');self.rating_chart_tabs.addTab(self.song_plot,'单曲达成率走势')
        details=QTabWidget();self.rating_detail_tabs=details;split.addWidget(details)
        self.rating_records=ArchiveTable([('游玩时间','time'),('曲目','title'),('游玩前','before'),('游玩后','after'),('变化','delta'),('日志内新高','peak')]);details.addTab(self.rating_records,'Rating 变动记录')
        self.candidates=ArchiveTable([('曲目','title'),('原始候选组','group'),('位置','position'),('难度','difficulty'),('达成率','acc'),('参考单曲 Rating','ra')]);details.addTab(self.candidates,'原始候选名单')
        self.song_records=ArchiveTable([('游玩时间','time'),('曲目','title'),('难度','difficulty'),('ACC','acc'),('定数','ds'),('参考 Rating','ra'),('DX 分','dx'),('FC / AP','mark')]);details.addTab(self.song_records,'单曲游玩记录')
        self.rating_records.centered_columns={0,2,3,4,5};self.rating_records.table.setColumnWidth(1,260)
        self.song_records.centered_columns={0,2,3,4,5,6,7};self.song_records.table.setColumnWidth(1,260)
        for view in (self.rating_records,self.song_records):view.table.horizontalHeader().setStretchLastSection(False)
        for view in (self.rating_records,self.song_records):
            view.table.cellDoubleClicked.connect(lambda row,col,table=view:self.select_song_trend(table,row))
        for signal in (self.trend_date_filter.toggled,self.trend_start.dateChanged,self.trend_end.dateChanged):signal.connect(self.render_rating)
        split.setSizes([300,350])
        self.rating_chart_tabs.currentChanged.connect(self.rating_tab_changed)
        for signal in (self.trend_acc_filter.toggled,self.trend_acc_min.valueChanged,self.trend_acc_max.valueChanged):signal.connect(self.render_rating)
        self.rating_metric.currentIndexChanged.connect(self.render_rating);self.trend_song.currentIndexChanged.connect(self.render_rating);self.trend_filtered.toggled.connect(self.render_rating)

    def make_progress(self):
        layout=self.owner.page('冒险与养成','地图、角色、搭档、实际课程挑战、万华镜和登录奖励。状态按导出原值显示；地图参考距离不等于授牌或通关条件。')
        controls=QHBoxLayout();layout.addLayout(controls)
        self.progress_summary=QLabel();self.progress_summary.setWordWrap(True);controls.addWidget(self.progress_summary,1)
        self.metadata_button=QPushButton('补充本地游戏名称资料');controls.addWidget(self.metadata_button);self.metadata_button.clicked.connect(self.import_names)
        self.progress_tabs=QTabWidget();layout.addWidget(self.progress_tabs,1)
        definitions=[
          ('userMapList','地图',[('地图','name'),('ID','mapId'),('距离','distance'),('已通关','isClear'),('已完成','isComplete'),('锁定','isLock'),('最后奖励参考距离','referenceEnd'),('距最后奖励参考','remaining')]),
          ('userCharacterList','角色',[('角色','name'),('ID','characterId'),('等级','level'),('觉醒原值','awakening'),('使用次数','useCount'),('收藏','favorite'),('点数','point'),('持有计数','count'),('下一觉醒','nextAwake'),('下一觉醒进度原值','nextAwakePercent')]),
          ('userIntimateList','搭档亲密度',[('搭档','name'),('ID','partnerId'),('亲密等级','intimateLevel'),('已领奖计数','intimateCountRewarded')]),
          ('userCourseList','课程挑战记录',[('课程','name'),('选曲方式','selection'),('参考曲数','songCount'),('ID','courseId'),('次数','playCount'),('最近通关','isLastClear'),('最佳总达成率','bestAcc'),('最佳 DX 分','bestDeluxscore'),('累计剩余血量原值','totalRestlife'),('通关时间','clearDate'),('最近游玩时间','lastPlayDate'),('最佳达成率时间','bestAchievementDate'),('最佳 DX 分时间','bestDeluxscoreDate'),('累计达成率原值','totalAchievement'),('累计 DX 分','totalDeluxscore')]),
          ('userKaleidxScopeList','万华镜',[('门','name'),('ID','gateId'),('已发现门','isGateFound'),('已发现钥匙','isKeyFound'),('已查看信息','isInfoWatched'),('已通关','isClear'),('次数','playCount'),('最佳总达成率','bestAcc'),('最佳 DX 分','bestDeluxscore'),('剩余血量累计原值','totalRestLife'),('通关时间','clearDate'),('最近游玩时间','lastPlayDate'),('最佳达成率时间','bestAchievementDate'),('最佳 DX 时间','bestDeluxscoreDate'),('累计达成率原值','totalAchievement'),('累计 DX 分','totalDeluxscore')]),
          ('userLoginBonusList','登录奖励',[('奖励','name'),('奖励类型','kindLabel'),('所需点数','required'),('ID','bonusId'),('点数','point'),('当前','isCurrent'),('已完成','isComplete')])]
        self.activity_detail_tabs={}
        for key,title,columns in definitions:
            view=ArchiveTable(columns);self.progress_views[key]=view
            if key=='userMapList':
                self.map_split=QSplitter();self.map_split.addWidget(view)
                self.map_detail_tabs=QTabWidget();self.map_detail_tabs.setTabsClosable(True);self.map_detail_tabs.setMinimumWidth(420);self.map_split.addWidget(self.map_detail_tabs);self.map_detail_tabs.hide()
                self.map_detail_tabs.tabCloseRequested.connect(self.close_map_detail)
                self.map_split.setSizes([800,520]);self.progress_tabs.addTab(self.map_split,title)
                view.table.cellDoubleClicked.connect(self.open_map_detail)
            elif key in ('userCourseList','userLoginBonusList'):
                split=QSplitter();split.addWidget(view);tabs=QTabWidget();tabs.setTabsClosable(True);tabs.setMinimumWidth(420);split.addWidget(tabs);tabs.hide();split.setSizes([800,520])
                self.activity_detail_tabs[key]=tabs;tabs.tabCloseRequested.connect(lambda index,section=key:self.close_activity_detail(section,index));view.table.cellDoubleClicked.connect(lambda row,col,section=key:self.open_activity_detail(section,row));self.progress_tabs.addTab(split,title)
            else:self.progress_tabs.addTab(view,title)
            if key in ('userCharacterList','userCourseList','userLoginBonusList'):view.centered_columns=set(range(1,len(columns)))
        self.progress_note=QLabel();self.progress_note.setWordWrap(True);layout.addWidget(self.progress_note)

    def make_profile(self):
        from app.profile_dashboard import ProfileHero,EquipmentPanel,ProfileOverview,CollectionPreview,CollectionSplit
        from PySide6.QtWidgets import QHeaderView
        layout=self.owner.page('个人档案与收藏','资料、累计统计、操作设置、收藏和解锁、排名及其他记录均保存在用户本地。档位或枚举未核实的字段保留原始编码。')
        self.profile_hero=ProfileHero();layout.addWidget(self.profile_hero)
        summary=QHBoxLayout();layout.addLayout(summary);self.profile_summary=QLabel();self.profile_summary.setWordWrap(True);summary.addWidget(self.profile_summary,1)
        self.profile_raw=QCheckBox('显示原始字段名');summary.addWidget(self.profile_raw)
        tabs=QTabWidget();self.profile_tabs=tabs;layout.addWidget(tabs,1)
        self.profile_table=ArchiveTable([('项目','field'),('值 / 名称','value'),('原始字段','key')]);self.profile_equipment=EquipmentPanel();tabs.addTab(ProfileOverview(self.profile_table,self.profile_equipment),'档案概览')
        self.option_table=ArchiveTable([('游戏设置','field'),('原始档位 / 值','value'),('原始字段','key')]);tabs.addTab(self.option_table,'操作设置')
        self.extend_table=ArchiveTable([('选曲与显示状态','field'),('值','value'),('原始字段','key')]);tabs.addTab(self.extend_table,'选曲状态')
        collection=QWidget();col=QVBoxLayout(collection);tabs.addTab(collection,'收藏与解锁')
        line=QHBoxLayout();col.addLayout(line);self.collection_mode=QComboBox();self.collection_mode.addItems(['物品与解锁','收藏项目','收藏歌曲']);line.addWidget(self.collection_mode)
        self.collection_kind=QComboBox();line.addWidget(self.collection_kind);self.valid_items=QCheckBox('仅有效物品');line.addWidget(self.valid_items)
        self.collection_table=ArchiveTable([('名称','name'),('种类','kind'),('ID','id'),('库存','stock'),('有效','valid')]);self.collection_preview=CollectionPreview();self.collection_split=CollectionSplit(self.collection_table,self.collection_preview);col.addWidget(self.collection_split,1)
        self.collection_table.centered_columns={1,2,3,4};self.collection_table.table.setColumnWidth(0,300);self.collection_table.table.horizontalHeader().setStretchLastSection(False)
        self.collection_table.table.setStyleSheet('QTableWidget{selection-background-color:#30445d;}QTableWidget::item:selected{background:#30445d;}')
        self.collection_table.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
        for index in range(1,5):self.collection_table.table.setColumnWidth(index,85 if index!=1 else 110)
        self.collection_table.table.currentCellChanged.connect(lambda row,*args:self.collection_preview.set_row(self.collection_table.selected_source(row)))
        self.collection_table.rowsChanged.connect(self.refresh_collection_preview)
        for signal in (self.collection_mode.currentIndexChanged,self.collection_kind.currentIndexChanged,self.valid_items.toggled):signal.connect(self.render_collections)
        ranking=QWidget();rank=QVBoxLayout(ranking);tabs.addTab(ranking,'排名与对战')
        self.rank_summary=QLabel();rank.addWidget(self.rank_summary)
        self.udemae=ArchiveTable([('对战项目','field'),('原值','value'),('原始字段','key')])
        self.seasons=ArchiveTable([('赛季 ID','seasonId'),('排名','rank'),('点数','point'),('记录日期','recordDate'),('已领奖','rewardGet')]);rank_split=QSplitter();rank_split.addWidget(self.udemae);rank_split.addWidget(self.seasons);rank_split.setSizes([500,600]);rank.addWidget(rank_split,1)
        self.seasons.centered_columns=set(range(5))
        extras=QWidget();ex=QVBoxLayout(extras);tabs.addTab(extras,'其他记录')
        self.other_choice=QComboBox();self.other_choice.addItems(list(OTHER_SECTIONS.values()));self.other_choice.currentIndexChanged.connect(self.render_other);ex.addWidget(self.other_choice)
        self.other_hint=QLabel();self.other_hint.setWordWrap(True);ex.addWidget(self.other_hint)
        self.other_table=ArchiveTable([('记录','record'),('字段','field'),('原值','value')]);ex.addWidget(self.other_table,1)
        for view in (self.profile_table,self.option_table,self.extend_table,self.udemae):
            header=view.table.horizontalHeader();header.setStretchLastSection(False);header.setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch);view.table.setColumnWidth(0,205);view.table.setColumnWidth(2,210);view.table.setColumnHidden(2,True)
            view.page_size.hide()
            for button in view.page_buttons:button.hide()
            view.limit=1000
        self.profile_raw.toggled.connect(lambda checked:[v.table.setColumnHidden(2,not checked) for v in (self.profile_table,self.option_table,self.extend_table,self.udemae)])

    def refresh(self):
        core=self.owner.core;self.archive=core.archive(self.owner.uid());self.sections=self.archive.get('sections',{})
        self.map_metadata=core.map_details();self.activity_metadata=core.activity_details()
        for tabs in getattr(self,'activity_detail_tabs',{}).values():
            while tabs.count():tabs.widget(0).deleteLater();tabs.removeTab(0)
            tabs.hide()
        if hasattr(self,'map_detail_tabs'):
            while self.map_detail_tabs.count():self.map_detail_tabs.widget(0).deleteLater();self.map_detail_tabs.removeTab(0)
            self.map_detail_tabs.hide()
        self.names=core.collection_names();self.charts=core.catalog('private');self.logs=core.archive_logs(self.owner.uid())
        days=[r['day'] for r in self.logs if r['day']]
        for view in (self.start,self.end):view.blockSignals(True)
        self.start.setDate(QDate.fromString(min(days),'yyyy-MM-dd') if days else QDate.currentDate())
        self.end.setDate(QDate.fromString(max(days),'yyyy-MM-dd') if days else QDate.currentDate())
        for view in (self.start,self.end):view.blockSignals(False)
        for view,date in ((self.trend_start,self.start.date()),(self.trend_end,self.end.date())):
            view.blockSignals(True);view.setDate(date);view.blockSignals(False)
        self.trend_song.blockSignals(True);self.trend_song.clear();self.trend_song.addItem('全部谱面（逐局达成率）',None)
        for key,row in sorted({(r['musicId'],r['level']):r for r in self.logs}.items(),key=lambda item:(item[1]['title'].casefold(),item[0])):
            self.trend_song.addItem(f"{row['title']} · {diff_name(row['level'])}",key)
        self.trend_song.blockSignals(False)
        kinds=sorted({r.get('itemKind') for section in ('userItemList','userFavoriteList') for r in self.sections.get(section,[]) if isinstance(r.get('itemKind'),int)})
        self.collection_kind.blockSignals(True);self.collection_kind.clear();self.collection_kind.addItem('全部种类',None)
        for kind in kinds:self.collection_kind.addItem(ITEM_KINDS.get(kind,('',f'未知类型 {kind}'))[1],kind)
        self.collection_kind.blockSignals(False)
        self.clear_play();self.render_history();self.render_rating();self.render_progress();self.render_profile()

    def reset_filters(self):
        self.history_query.clear();self.history_diff.setCurrentIndex(0);self.date_filter.setChecked(False);self.only_new.setChecked(False)
        self.history_table.query.clear();self.acc_filter.setChecked(False);self.acc_min.setValue(0);self.acc_max.setValue(101);self.render_history()

    def select_day(self,day):
        self.start.setDate(day);self.end.setDate(day);self.date_filter.setChecked(True);self.history_tabs.setCurrentIndex(0);self.render_history()

    def select_day_row(self,row,col=0):
        record=self.day_table.selected_source(row)
        if record:self.select_day(QDate.fromString(record['day'],'yyyy-MM-dd'))

    def render_history(self,*args):
        if not hasattr(self,'logs'):return
        diff=self.history_diff.currentIndex()-1 if self.history_diff.currentIndex() else None
        self.filtered=filter_logs(self.logs,self.history_query.text(),None if diff==5 else diff,
            self.start.date().toString('yyyy-MM-dd') if self.date_filter.isChecked() else '',
            self.end.date().toString('yyyy-MM-dd') if self.date_filter.isChecked() else '',self.only_new.isChecked())
        if diff==5:self.filtered=[r for r in self.filtered if r['level']>=5]
        warnings='；'.join(self.archive.get('warnings',[]))
        state='旧快照没有完整档案，请重新导入完整 AquaDX JSON。' if not self.archive.get('available') else '仅为本次导出所保留的历史。'
        self.history_hint.setText(f'导入日志 {len(self.logs)} 条 · 当前筛选 {len(self.filtered)} 条。{state} '+warnings)
        rows=[]
        for r in sorted(self.filtered,key=lambda r:(r.get('lastPlayedTimestamp') is None,-r.get('lastPlayedTimestamp',0),r['sourceIndex'])):
            rows.append(dict(title=r['title'],time=r['timeLabel'],difficulty=diff_name(r['level']),ds=r.get('ds'),acc=percent(r.get('achievement')),dx=r.get('deluxscore'),
                mark=mark(r),timing=f"{shown(r.get('fastCount'))} / {shown(r.get('lateCount'))}",delta=r.get('ratingDelta'),_source=r,_musicId=r['musicId'],_level=r['level'],
                _sort={'time':r.get('lastPlayedTimestamp'),'acc':r.get('achievements')}))
        self.history_table.set_rows(rows);self.clear_play()
        stats=log_statistics(self.filtered);days=stats['days']
        self.calendar_summary.setText(f"覆盖 {len(days)} 个日期 · 无有效时间 {stats['undated']} 条。颜色越深记录越多，点击日期查看当日；上方筛选同样生效。")
        self.calendar.setDateTextFormat(QDate(),QTextCharFormat())
        for day,count in days.items():
            fmt=QTextCharFormat();fmt.setBackground(QColor(35,90+round(100*count/max(days.values())),125));fmt.setForeground(QColor('#ffffff'));fmt.setToolTip(f'{day} · {count} 条记录')
            self.calendar.setDateTextFormat(QDate.fromString(day,'yyyy-MM-dd'),fmt)
        if days:
            last=QDate.fromString(max(days),'yyyy-MM-dd');self.calendar.setCurrentPage(last.year(),last.month())
        self.day_table.set_rows([dict(day=day,count=count) for day,count in sorted(days.items(),reverse=True)])
        self.day_plot.set_points([(datetime.strptime(day,'%Y-%m-%d').replace(tzinfo=LOCAL_TIMEZONE).timestamp(),count,f'{day}\n{count} 次游玩记录') for day,count in sorted(days.items())],
            '每日游玩次数 · 导出保留的记录（缺失日期不补零）')
        self.render_judgements()
        if hasattr(self,'trend_filtered') and self.trend_filtered.isChecked():self.render_rating()

    def render_judgements(self,*args):
        rows=self.filtered
        if self.acc_filter.isChecked():rows=filter_accuracy(rows,self.acc_min.value(),self.acc_max.value())
        self.judgement_rows=rows;stats=log_statistics(rows)
        ratio=f"{stats['fastPercent']:.1f}%" if stats['fastPercent'] is not None else '未提供/无快慢判定'
        self.judge_summary.setText(f"当前筛选 {stats['logs']} 局 · FC及以上 {stats['fcLogs']} 局 / AP及以上 {stats['apLogs']} 局\nFAST {shown(stats['fast'])}（{stats['fastCoverage']}局有字段） / LATE {shown(stats['late'])}（{stats['lateCoverage']}局有字段） · 成对字段 {stats['pairedTimingLogs']} 局中的 FAST 占比 {ratio}")
        self.judge_table.set_rows([dict(note=NOTE_LABELS[n],coverage=' / '.join(str(stats['coverage'][n+j]) for j in JUDGEMENTS),**{j:stats['judgements'][n+j] for j in JUDGEMENTS}) for n in NOTE_TYPES])
        if self.acc_filter.isChecked() and self.acc_min.value()>self.acc_max.value():self.judge_summary.setText('ACC下限不能大于上限，请调整区间。')
        self.judge_table.fit_content(tight=True)

    def clear_play(self):
        for view in (self.play_cover,self.play_rank,self.play_fc,self.play_meta,self.play_accuracy,self.play_mark,self.play_info):view.clear()
        self.play_title.setText('选择一条记录查看当局判定')
        for value in self.play_values.values():value.setText('—')
        self.play_judgements.set_rows([]);self.play_raw.set_rows([])

    def show_play(self,row,col=0):
        r=self.history_table.selected_source(row)
        if not r:return
        self.clear_play()
        from app.desktop_core import ASSETS
        from app.desktop_ui import crisp_pixmap
        resource=f"{r['musicId']%10000}.png";path=self.owner.core.directory/'covers'/resource
        if not path.exists():path=image_path(ASSETS/'data/report_assets/covers'/resource)
        self.play_cover.setPixmap(crisp_pixmap(path,76,76,self.owner.devicePixelRatioF()))
        self.play_title.setText(r['title']);self.play_meta.setText(f"#{r['musicId']} · {diff_name(r['level'])}")
        self.play_accuracy.setText(percent(r.get('achievement')) or '未提供')
        if r['achievements'] is not None:
            rank=rating(1,r['achievements'])[1];self.play_rank.setPixmap(crisp_pixmap(ASSETS/f'data/report_assets/rating-rank_{rank}.png',70,32,self.owner.devicePixelRatioF()))
        name=FC.get(r.get('comboStatus'))
        if name:self.play_fc.setPixmap(crisp_pixmap(ASSETS/f'data/report_assets/rating-icon_{name}.png',28,28,self.owner.devicePixelRatioF()))
        self.play_mark.setText(mark(r).upper())
        values={'ds':shown(r.get('ds')),'ra':shown(r.get('referenceRating')),'dx':shown(r.get('deluxscore')),
            'combo':f"{r.get('maxCombo') if r.get('maxCombo') is not None else '—'} / {r.get('totalCombo') if r.get('totalCombo') is not None else '—'}",'fast':shown(r.get('fastCount')),'late':shown(r.get('lateCount'))}
        for key,value in values.items():self.play_values[key].setText(value)
        self.play_info.setText(f"游玩时间：{r['timeLabel']}\n当局地点：{shown(r.get('placeName'))}")
        self.play_judgements.set_rows([dict(note=NOTE_LABELS[n],**{j:r.get(n+j) for j in JUDGEMENTS}) for n in NOTE_TYPES]);self.play_judgements.fit_content(tight=True)
        self.play_raw.set_rows([dict(field=k,value=v) for k,v in r.items() if k not in ('title','day','timeLabel','referenceRating','versionName')])
        self.play_scroll.verticalScrollBar().setValue(0)

    def open_song(self,row):
        if row and isinstance(row.get('musicId'),int):self.owner.song_detail(row['musicId'])

    def select_song_trend(self,table,row):
        source=table.selected_source(row)
        if not source:return
        key=(source.get('musicId'),source.get('level'))
        for index in range(self.trend_song.count()):
            if self.trend_song.itemData(index)==key:
                self.trend_song.setCurrentIndex(index);self.rating_chart_tabs.setCurrentIndex(1);self.rating_detail_tabs.setCurrentIndex(2);self.render_rating();return

    def rating_tab_changed(self,index):
        self.rating_detail_tabs.setCurrentIndex(2 if index==1 else 0)
        self.render_rating()

    def render_rating(self,*args):
        field='afterDeluxRating' if self.rating_metric.currentIndex()==0 else 'afterRating';before='beforeDeluxRating' if self.rating_metric.currentIndex()==0 else 'beforeRating'
        points=[];rows=[];peak=None;unknown=0
        logs=self.filtered if self.trend_filtered.isChecked() else self.logs
        if self.trend_date_filter.isChecked():
            start=self.trend_start.date().toString('yyyy-MM-dd');end=self.trend_end.date().toString('yyyy-MM-dd')
            logs=[r for r in logs if r.get('day') and start<=r['day']<=end]
        for r in logs:
            value=number(r.get(field));old=number(r.get(before));timestamp=r.get('lastPlayedTimestamp')
            if value is not None and timestamp is not None:
                points.append((timestamp,value,f"{r['timeLabel']}\n{r['title']}\n{value}"))
                is_peak=peak is not None and value>peak;peak=max(value,peak) if peak is not None else value
            else:is_peak=False;unknown+=1
            rows.append(dict(time=r['timeLabel'],title=r['title'],before=old,after=value,delta=value-old if old is not None and value is not None else None,peak=is_peak,_source=r,_sort={'time':timestamp} ))
        self.rating_plot.set_points(points,self.rating_metric.currentText()+' · 账号全部谱面日志观测值')
        key=self.trend_song.currentData();song=[r for r in logs if key is None or (r['musicId'],r['level'])==key]
        total_song=len(song)
        if self.trend_acc_filter.isChecked():song=filter_accuracy(song,self.trend_acc_min.value(),self.trend_acc_max.value())
        self.trend_rows=song
        self.song_plot.set_points([(r['lastPlayedTimestamp'],r['achievements'],f"{r['timeLabel']}\n{r['title']}\n{r['achievements']:.4f}%") for r in song if r.get('lastPlayedTimestamp') is not None and r['achievements'] is not None],
            '达成率走势 · '+('全部谱面，不同谱面不可直接比较' if key is None else self.trend_song.currentText()))
        self.song_records.set_rows([dict(time=r['timeLabel'],title=r['title'],difficulty=diff_name(r['level']),acc=percent(r.get('achievement')),ds=r.get('ds'),ra=r.get('referenceRating'),dx=r.get('deluxscore'),mark=mark(r),_sort={'time':r.get('lastPlayedTimestamp'),'acc':r.get('achievements')},_source=r) for r in reversed(song)])
        profile=self.sections.get('userData',{})
        single=self.rating_chart_tabs.currentIndex()==1
        self.rating_metric.setVisible(not single);self.trend_song.setVisible(single);self.trend_acc_controls.setVisible(single)
        if single:
            scope=f'{self.trend_acc_min.value():.4f}% ~ {self.trend_acc_max.value():.4f}%' if self.trend_acc_filter.isChecked() else '全部ACC'
            self.rating_summary.setText(f"{self.trend_song.currentText()} · {scope} · 筛选 {len(song)} / {total_song} 局 · 有效绘图点 {len(self.song_plot.points)}。下表可查看对应单曲记录；区间仅影响本图和单曲记录。")
            if self.trend_acc_filter.isChecked() and self.trend_acc_min.value()>self.trend_acc_max.value():self.rating_summary.setText('ACC下限不能大于上限，请调整区间。')
        else:
            drops=sum(points[i][1]<points[i-1][1] for i in range(1,len(points)))
            self.rating_summary.setText(f"原报当前 Rating {shown(profile.get('playerRating'))} · 历史最高 {shown(profile.get('highestRating'))} · 账号全部谱面有效点 {len(points)} · 时间/字段缺失 {unknown} · 下降记录 {drops} 次（按日志原值保留）。选曲与ACC区间仅在单曲达成率标签生效。")
        if self.trend_date_filter.isChecked() and self.trend_start.date()>self.trend_end.date():self.rating_summary.setText('开始日期不能晚于结束日期，请调整区间。')
        self.rating_records.set_rows(list(reversed(rows)))
        self.candidates.set_rows([dict(title=r['title'],group=r['group'],position=r['position'],difficulty=diff_name(r['level']),acc=f"{r['achievements']:.4f}%",ra=r['referenceRating'],_musicId=r['musicId'],_level=r['level'],_source=r) for r in rating_candidates(self.archive,self.charts)])

    def render_progress(self):
        specs={'userMapList':('map','mapId'),'userCharacterList':('chara','characterId'),'userIntimateList':('partner','partnerId'),
            'userCourseList':('course','courseId'),'userKaleidxScopeList':('gate','gateId'),'userLoginBonusList':('bonus','bonusId')}
        for section,(kind,key) in specs.items():
            rows=[]
            for source in self.sections.get(section,[]):
                r=dict(source);r['name']=entity_name(self.names,kind,r.get(key));r['bestAcc']=percent(r.get('bestAchievement'))
                from app.desktop_core import ASSETS
                r['_imagePath']=entity_image(ASSETS/'data/report_assets/archive',kind,r.get(key))
                if section in ('userCourseList','userLoginBonusList'):
                    from app.activity_details_ui import bonus_image,course_rows
                    category='courses' if section=='userCourseList' else 'bonuses';metadata=self.activity_metadata[category].get(str(r.get(key)),{})
                    r['name']=metadata.get('name') or r['name']
                    if section=='userCourseList':
                        r['selection']='随机' if metadata.get('random') else '固定' if metadata else '未收录';r['songCount']=None if metadata.get('random') or not metadata else len(metadata.get('musics',[]))
                        r['_imagePaths']=[n['_imagePath'] for n in course_rows(self.owner,metadata,self.charts) if n.get('_imagePath')]
                        r['_imagePath']=r['_imagePaths'][0] if r['_imagePaths'] else None
                    else:
                        r['kindLabel']=metadata.get('reward',{}).get('kindLabel');r['required']=metadata.get('maxPoint');r['_imagePath']=bonus_image(ASSETS/'data/report_assets/archive',metadata,self.owner.core.directory/'covers')
                if section=='userMapList':
                    from app.map_details_ui import map_image
                    r['_imagePath']=map_image(ASSETS/'data/report_assets/archive',self.map_metadata.get(str(r.get('mapId')),{}))
                if section=='userMapList':
                    metadata=self.map_metadata.get(str(r.get('mapId')),self.names.get('map',{}).get(str(r.get('mapId')),{}));end=metadata.get('lastRewardDistance')
                    r['referenceEnd']=None if metadata.get('infinite') else end
                    distance=number(r.get('distance'),0);r['remaining']=max(0,end-distance) if r['referenceEnd'] and distance is not None else None
                rows.append(r)
            self.progress_views[section].set_rows(rows)
        counts=' · '.join(f'{title} {len(self.sections.get(key,[]))}' for key,title in [('userMapList','地图'),('userCharacterList','角色'),('userCourseList','课程'),('userKaleidxScopeList','万华镜')])
        self.progress_summary.setText(counts+f"\n名称资料 {sum(len(v) for v in self.names.values())} 项；缺名称保留类型与 ID。")
        missing=[key for key in specs if key not in self.archive.get('present',[])]
        self.progress_note.setText('未提供的区段：'+('、'.join(missing) if missing else '无；空列表表示导出有该区段但没有条目。')+'\n名称来自游戏 XML；图片按资源 ID 匹配，地图显示路线最后奖励的名牌板底板，课程显示所含曲绘。双击地图查看距离与奖励节点。未匹配到的图片不代填。距离为游戏原始单位。')

    def close_activity_detail(self,section,index):
        tabs=self.activity_detail_tabs[section];widget=tabs.widget(index);tabs.removeTab(index)
        if widget:widget.deleteLater()
        if not tabs.count():tabs.hide()

    def open_activity_detail(self,section,row):
        from app.activity_details_ui import activity_panel
        from app.desktop_core import ASSETS
        source=self.progress_views[section].selected_source(row)
        if not source:return
        key='courseId' if section=='userCourseList' else 'bonusId';identifier=str(source.get(key));tabs=self.activity_detail_tabs[section]
        for i in range(tabs.count()):
            if tabs.widget(i).property('activityId')==identifier:tabs.show();tabs.setCurrentIndex(i);return
        category='courses' if section=='userCourseList' else 'bonuses';metadata=self.activity_metadata[category].get(identifier,{})
        panel=activity_panel(self.owner,section,metadata,source,ASSETS/'data/report_assets/archive');panel.setProperty('activityId',identifier)
        tabs.addTab(panel,metadata.get('name') or source.get('name') or identifier);tabs.show();tabs.setCurrentWidget(panel)

    def close_map_detail(self,index):
        widget=self.map_detail_tabs.widget(index);self.map_detail_tabs.removeTab(index)
        if widget:widget.deleteLater()
        if not self.map_detail_tabs.count():self.map_detail_tabs.hide()

    def open_map_detail(self,row,column=0):
        from app.map_details_ui import map_panel
        from app.desktop_core import ASSETS
        source=self.progress_views['userMapList'].selected_source(row)
        if not source:return
        mid=str(source.get('mapId'))
        for i in range(self.map_detail_tabs.count()):
            if self.map_detail_tabs.widget(i).property('mapId')==mid:self.map_detail_tabs.show();self.map_detail_tabs.setCurrentIndex(i);return
        metadata=self.map_metadata.get(mid,{})
        panel=map_panel(self.owner,metadata,source,ASSETS/'data/report_assets/archive');panel.setProperty('mapId',mid)
        self.map_detail_tabs.addTab(panel,metadata.get('name') or source.get('name') or mid);self.map_detail_tabs.show();self.map_detail_tabs.setCurrentWidget(panel)

    def render_profile(self):
        def pairs(section):
            rows=[]
            for key,value in self.sections.get(section,{}).items():
                if section=='userData' and key=='nameplateId' and str(value)=='0':value='未设置（原始值 0）'
                elif section=='userData' and key in EQUIPMENT and value is not None:value=f'{value} · {entity_name(self.names,EQUIPMENT[key],value)}'
                rows.append(dict(field=label(key),value=value,key=key))
            return rows
        self.profile_table.set_rows(pairs('userData'));self.option_table.set_rows(pairs('userOption'));self.extend_table.set_rows(pairs('userExtend'));self.udemae.set_rows(pairs('userUdemae'))
        self.seasons.set_rows(self.sections.get('userFriendSeasonRankingList',[]));u=self.sections.get('userUdemae',{})
        wins,losses=number(u.get('totalWinNum'),0),number(u.get('totalLoseNum'),0)
        ratio=f'{100*wins/(wins+losses):.1f}%' if wins is not None and losses is not None and wins+losses else '未提供/无对局'
        self.rank_summary.setText(f'对战累计胜率 {ratio}；只依据原始累计胜负计数，NPC 独立显示，不与赛季排名混算。')
        present=self.archive.get('present',[])
        from app.desktop_core import ASSETS
        self.profile_hero.set_data(self.archive,ASSETS/'data/report_assets/archive');self.profile_equipment.set_data(self.sections.get('userData',{}),self.names,ASSETS/'data/report_assets/archive')
        self.profile_summary.setText(f"本地档案 · 已导入 {len(present)} 个区段 · 未核实的游戏设置保留原始档位")
        self.render_collections();self.render_other()

    def music_title(self,mid):
        return next((c['title'] for c in self.charts if c['music_id']==mid),f'待补充曲目 · ID {mid}')

    def render_collections(self,*args):
        if not hasattr(self,'collection_table'):return
        rows=[];mode=self.collection_mode.currentIndex();kind_filter=self.collection_kind.currentData()
        if mode==2:
            for mid in sorted(favorite_music_ids(self.archive)):rows.append(dict(name=self.music_title(mid),kind='收藏歌曲',id=mid,stock=None,valid=None,_musicId=mid))
        else:
            section='userItemList' if mode==0 else 'userFavoriteList'
            for r in self.sections.get(section,[]):
                kind=r.get('itemKind')
                if kind_filter is not None and kind!=kind_filter:continue
                if mode==0 and self.valid_items.isChecked() and r.get('isValid') is not True:continue
                entity,title=ITEM_KINDS.get(kind,('unknown',f'未知类型 {kind}'))
                ids=[r.get('itemId')] if mode==0 else r.get('itemIdList',[])
                for mid in ids:
                    rows.append(dict(name=self.music_title(mid) if entity=='music' else entity_name(self.names,entity,mid),kind=title,id=mid,stock=r.get('stock'),valid=r.get('isValid')))
        from app.desktop_core import ASSETS
        from app.map_details_ui import reward_image
        from app.profile_dashboard import profile_image
        assets=ASSETS/'data/report_assets/archive'
        for row in rows:
            if row['kind']=='称号':row['_imageNote']='使用游戏原始称号底板与配置中的名称、稀有度生成预览'
            if mode==2:row['_imagePath']=reward_image(assets,{'kind':'MusicNew','elementId':str(row['id'])},self.owner.core.directory/'covers')
            else:
                entity=next((entity for entity,title in ITEM_KINDS.values() if title==row['kind']),None)
                row['_imagePath']=reward_image(assets,{'kind':'MusicNew','elementId':str(row['id'])},self.owner.core.directory/'covers') if entity=='music' else profile_image(assets,entity,row['id'])
        self.collection_kind.setEnabled(mode!=2);self.valid_items.setEnabled(mode==0)
        self.collection_table.set_rows(rows)

    def refresh_collection_preview(self):
        table=self.collection_table.table
        if table.rowCount():table.setCurrentCell(0,0)
        self.collection_preview.set_row(self.collection_table.selected_source(table.currentRow()))

    def render_other(self,*args):
        if not hasattr(self,'other_table'):return
        section=list(OTHER_SECTIONS)[self.other_choice.currentIndex()];rows=[]
        for i,row in enumerate(self.sections.get(section,[]),1):
            for key,value in row.items():rows.append(dict(record=i,field=key,value=value))
        self.other_table.set_rows(rows)
        self.other_hint.setText(('该区段未包含在已保存快照中，请重新导入。' if section not in self.archive.get('present',[]) else f'导出保留 {len(self.sections.get(section,[]))} 条记录。')+' 活动 kind/param 和未知扩展字段仅按原值展示，不擅自解释为解锁或奖励。')

    def import_names(self):
        path=QFileDialog.getExistingDirectory(self.owner,'选择包含游戏 XML 的资料目录')
        if not path:return
        self.owner.background(lambda:self.owner.core.import_collection_names(path),lambda result:self.names_imported(result))

    def names_imported(self,result):
        self.refresh();self.owner.statusBar().showMessage(f"名称资料已更新 · 解析 {result['sourceFiles']} 个文件 · 跳过 {result['skipped']} 个 · 原始游戏文件未改动")
