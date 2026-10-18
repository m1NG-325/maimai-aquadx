"""Embedded course and login-bonus inspectors using explicit reference IDs."""
from pathlib import Path
from PySide6.QtCore import Qt,QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QScrollArea,QSizePolicy
from app.archive_widgets import ArchiveTable,shown
from app.map_details_ui import reward_image
from app.collection_metadata import entity_image
from app.parser import DIFFICULTIES

def bonus_image(assets,metadata,cache=None):
 r=metadata.get('reward',{})
 if r.get('kind')=='Ticket':return entity_image(assets,'ticket',r.get('elementId'))
 if r.get('kind')=='Partner':return entity_image(assets,'partner',r.get('elementId'))
 return reward_image(assets,r,cache)

def course_rows(owner,metadata,charts=None):
 if metadata.get('random'):return []
 catalog={(r['music_id'],r['level_index']):r for r in (owner.archives.charts if charts is None else charts)}
 best={(r['musicId'],r['level']):r for r in (owner.data or {}).get('privateCatalog',{}).get('rows',[])}
 rows=[]
 from app.desktop_core import ASSETS
 for music in metadata.get('musics',[]):
  mid=music['musicId'];level=music['level'];ref=catalog.get((mid,level),{});score=best.get((mid,level))
  rows.append(dict(name=music.get('name') or ref.get('title') or f'ID {mid}',difficulty=DIFFICULTIES[level] if 0<=level<5 else '特殊',ds=ref.get('ds'),acc=f"{score['achievements']:.4f}%" if score else '未玩',mark=(score.get('fc') or '—').upper() if score else '—',_imagePath=reward_image(ASSETS/'data/report_assets/archive',{'kind':'MusicNew','elementId':str(mid)},owner.core.directory/'covers'),_level=level,_source=music))
 return rows

def activity_panel(owner,section,metadata,current,assets):
 scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();scroll.setWidget(body);layout=QVBoxLayout(body);layout.setContentsMargins(12,12,12,12);layout.setSpacing(10)
 def text(value,style=''):
  label=QLabel(value);label.setTextFormat(Qt.TextFormat.PlainText);label.setWordWrap(True)
  if style:label.setStyleSheet(style)
  layout.addWidget(label);return label
 text(metadata.get('name') or current.get('name') or '未收录资料','font-size:18px;font-weight:600;')
 if section=='userCourseList':
  text(f"课程 ID {current.get('courseId')} · {metadata.get('mode') or '模式未收录'}\n游玩次数 {shown(current.get('playCount'))} · 最近通关 {shown(current.get('isLastClear'))}\n最佳总达成率 {current.get('bestAcc') or '未提供'} · 最佳 DX 分 {shown(current.get('bestDeluxscore'))}")
  text(f"初始血量 {shown(metadata.get('life'))} · 每首回复 {shown(metadata.get('recover'))}\n扣血配置原值："+' / '.join(f'{k} {shown(v)}' for k,v in metadata.get('damage',{}).items()))
  dates=[f'{label}：{shown(current.get(key))}' for label,key in [('通关时间','clearDate'),('最近游玩','lastPlayDate'),('最佳达成率时间','bestAchievementDate'),('最佳 DX 分时间','bestDeluxscoreDate')] if current.get(key)]
  text('\n'.join(dates) if dates else '时间字段：本次导出未提供。')
  if metadata.get('random'):text(f"随机选曲课程 · 随机范围原值 {shown(metadata.get('lower'))}～{shown(metadata.get('upper'))}\n该挑战记录未包含实际选曲列表，不把 XML 占位曲目当作实际游玩曲目。")
  else:
   text('课程曲目与各谱面最佳成绩','font-size:14px;font-weight:600;')
   table=ArchiveTable([('曲目','name'),('难度','difficulty'),('定数','ds'),('单曲最佳','acc'),('FC / AP','mark')]);table.centered_columns={1,2,3,4};table.table.setIconSize(QSize(56,56));table.set_rows(course_rows(owner,metadata));table.table.setColumnWidth(0,200);table.table.setColumnWidth(1,90);table.table.setColumnWidth(2,70);table.setMinimumHeight(380);layout.addWidget(table);scroll.song_table=table
  text('单曲成绩为导入快照中的该谱面最佳，不代表此次课程逐曲成绩。课程配置与定数为参考。','font-size:11px;color:#9cafc7;')
 else:
  r=metadata.get('reward',{});path=bonus_image(assets,metadata,owner.core.directory/'covers')
  if path:
   label=QLabel();label.setPixmap(QPixmap(path).scaled(360,150,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation));label.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Preferred);label.setAlignment(Qt.AlignmentFlag.AlignCenter);layout.addWidget(label)
  else:text('未匹配独立奖励图片。','color:#9cafc7;')
  text(f"奖励 ID {current.get('bonusId')}\n内容：{r.get('kindLabel') or '未收录类型'} · {r.get('name') or '未收录名称'}（ID {shown(r.get('elementId'))}）\n点数：{shown(current.get('point'))} / {shown(metadata.get('maxPoint'))}\n当前奖励 {shown(current.get('isCurrent'))} · 已完成 {shown(current.get('isComplete'))}")
  text(f"重复领取配置：{shown(metadata.get('repeat'))}\n联动配置：{shown(metadata.get('collabo'))}\n开放事件：{metadata.get('openEvent') or '未收录'}（ID {shown(metadata.get('openEventId'))}）")
  text('所需点数与奖励类型来自参考 XML；当前点数和完成状态来自导出。重复奖励不根据点数推断是否实际领奖。','font-size:11px;color:#9cafc7;')
 if not metadata:text('未收录该 ID 的参考 XML；可通过“补充本地游戏名称资料”导入游戏目录。')
 layout.addStretch();return scroll
