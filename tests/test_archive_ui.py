import os,json,csv
from pathlib import Path
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtCore import QDate,Qt
from PySide6.QtWidgets import QApplication,QFileDialog
from app.desktop_core import DesktopCore
from app.desktop_ui import MainWindow,CoverDelegate
from tests.test_archive_data import export


def core_with_archive(tmp_path):
 core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json');raw=export()
 raw['userPlaylogList']=[dict(musicId=1+i%2,level=2,achievement=980000+i,deluxscore=i,userPlayDate=f'2026-01-{1+i//50:02d} 12:{i%50:02d}:00',beforeDeluxRating=1000+i,afterDeluxRating=1001+i,fastCount=i%3,lateCount=1,tapGreat=i%2,comboStatus=i%5,syncStatus=i%6) for i in range(137)]
 raw.update(userCourseList=[dict(courseId=1001,playCount=3,bestAchievement=3950000,totalRestlife=10)],userKaleidxScopeList=[dict(gateId=1,isClear=True)],userLoginBonusList=[dict(bonusId=1,point=1)],userIntimateList=[dict(partnerId=1,intimateLevel=2)],userItemList=[dict(itemId=101,itemKind=9,stock=1,isValid=True)],userFriendSeasonRankingList=[dict(seasonId=1,rank=5)],userUdemae={'totalWinNum':2,'totalLoseNum':1})
 source=tmp_path/'synthetic.json';source.write_text(json.dumps(raw),encoding='utf-8');core.import_file(source,'example');return core


def test_history_global_pagination_filters_calendar_and_detail(tmp_path):
 app=QApplication.instance() or QApplication([]);core=core_with_archive(tmp_path);before=core.db.player('example');w=MainWindow(core);w.show();a=w.archives
 try:
  assert w.pages.count()==17 and w.nav.item(12).text()=='游玩历史与判定'
  assert len(a.logs)==137 and a.history_table.table.rowCount()==100
  t=a.history_table;t.sort(5);t.sort(5)
  assert t.selected_source(0)['deluxscore']==136
  t.move(1);assert t.table.rowCount()==37 and t.selected_source(0)['deluxscore']==36
  a.show_play(0);assert len(a.play_raw.rows)>0 and a.play_judgements.rows[0]['Miss'] is None
  a.history_query.setText('1');assert len(a.filtered)==69
  a.select_day(QDate(2026,1,2));assert len(a.filtered)==25
  a.reset_filters();assert len(a.filtered)==137
  assert len(a.rating_plot.points)==137
  a.trend_song.setCurrentIndex(1);key=a.trend_song.currentData()
  expected=sum((r['musicId'],r['level'])==key for r in a.logs)
  assert expected>0 and len(a.song_plot.points)==expected
  a.history_query.setText('1');a.trend_filtered.setChecked(True);assert len(a.rating_plot.points)==69
  a.reset_filters();a.trend_filtered.setChecked(False)
  assert core.db.player('example')==before
 finally:w.close();app.processEvents()


def test_progress_collections_csv_and_legacy_refresh(tmp_path,monkeypatch):
 app=QApplication.instance() or QApplication([]);core=core_with_archive(tmp_path);w=MainWindow(core);a=w.archives
 try:
  assert len(a.progress_views)==6 and a.progress_views['userCourseList'].rows[0]['bestAcc']=='395.0000%'
  assert a.progress_views['userCharacterList'].rows[0]['characterId']==101
  a.collection_mode.setCurrentIndex(2);assert isinstance(a.collection_table.table.itemDelegateForColumn(0),CoverDelegate)
  a.collection_mode.setCurrentIndex(0);assert not isinstance(a.collection_table.table.itemDelegateForColumn(0),CoverDelegate)
  assert a.collection_table.rows[0]['kind']=='角色'
  a.collection_table.set_rows([dict(name='=UNTRUSTED()',kind='test',id=1)])
  dest=tmp_path/'export.csv';monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *args:(str(dest),'CSV'))
  a.collection_table.export_csv();assert list(csv.reader(dest.open(encoding='utf-8-sig')))[1][0]=="'=UNTRUSTED()"
  payload=core.db.player('example');payload.pop('archive');core.db.save_player('example',payload);w.load()
  assert a.logs==[] and a.play_raw.rows==[] and a.progress_views['userMapList'].rows==[]
  assert '旧快照' in a.history_hint.text()
 finally:w.close();app.processEvents()


def test_history_status_page_sizes_constants_and_detail_fit(tmp_path):
 app=QApplication.instance() or QApplication([]);core=core_with_archive(tmp_path);w=MainWindow(core);w.resize(1320,900);w.show();w.show_page(13);a=w.archives;t=a.history_table
 try:
  app.processEvents()
  assert [t.page_size.itemData(i) for i in range(4)]==[10,20,50,100]
  assert t.columns[3]==('定数','ds') and t.columns[6]==('FC / AP','mark')
  assert {r['mark'] for r in t.rows}=={'—','fc','fcp','ap','app'}
  assert all(r['ds']==r['_source'].get('ds') for r in t.rows)
  t.sort(5);t.sort(5)
  for i,size in enumerate((10,20,50,100)):
   t.page_size.setCurrentIndex(i);app.processEvents()
   assert t.limit==size and t.table.rowCount()==size
   assert t.selected_source(0)['deluxscore']==136
   assert not (t.table.item(0,0).textAlignment() & Qt.AlignmentFlag.AlignHCenter)
   assert all(t.table.item(0,j).textAlignment()==Qt.AlignmentFlag.AlignCenter for j in range(1,len(t.columns)))
   a.show_play(0);app.processEvents()
   assert a.play_title.text()==t.selected_source(0)['title']
   assert a.play_values['fast'].text()==str(t.selected_source(0)['fastCount'])
   assert not hasattr(a,'play_fs')
   jt=a.play_judgements.table
   assert jt.horizontalHeaderItem(0).text()=='音符\\判定'
   assert all(jt.item(0,j).textAlignment()==Qt.AlignmentFlag.AlignCenter for j in range(6))
   assert jt.minimumHeight()>=jt.horizontalHeader().height()+sum(jt.rowHeight(j) for j in range(5))
   for j in range(6):
    assert jt.columnWidth(j)>=jt.fontMetrics().horizontalAdvance(jt.horizontalHeaderItem(j).text())+12
   t.move(1);assert a.play_raw.rows==[] and a.play_accuracy.text()==''
  t.query.setText('no matches');assert t.table.rowCount()==0 and t.page==0
  splitter=a.history_table.parentWidget();w.resize(1000,760);app.processEvents()
  assert splitter.orientation()==Qt.Orientation.Vertical
  w.resize(2560,1440);app.processEvents();assert splitter.orientation()==Qt.Orientation.Horizontal
 finally:w.close();app.processEvents()


def test_calendar_drilldown_daily_series_accuracy_and_tight_tables(tmp_path):
 from app.archive_analysis import filter_accuracy
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));w.resize(2560,1440);w.show_page(13);w.show();a=w.archives
 try:
  app.processEvents()
  assert [p[1] for p in a.day_plot.points]==[50,50,37]
  assert a.calendar_panels.orientation()==Qt.Orientation.Vertical
  assert a.calendar_panels.widget(0)==a.day_plot and a.calendar_panels.widget(1)==a.calendar_bottom
  assert a.calendar_bottom.widget(0)==a.calendar and a.calendar_bottom.widget(1)==a.day_table
  for low,high in [(1.8,91.2),(0,1),(49,51),(0,.3)]:
   lo,hi,ticks=a.day_plot.axis_scale(low,high)
   assert all(isinstance(v,int) for v in ticks) and len(ticks)==len(set(ticks)) and lo<=low and hi>=high
  assert a.rating_plot.integer_ticks and not a.song_plot.integer_ticks and a.song_plot.axis_scale(1.8,91.2)[2][0]==91.2
  assert a.judge_table.page_size.isHidden() and all(button.isHidden() for button in a.judge_table.page_buttons)
  a.day_table.sort(1);a.day_table.sort(1)
  day=a.day_table.selected_source(0)['day'];a.day_table.table.cellDoubleClicked.emit(0,0)
  assert a.history_tabs.currentIndex()==0 and a.date_filter.isChecked()
  assert {r['day'] for r in a.filtered}=={day} and len(a.filtered)==50
  a.reset_filters();before=list(a.filtered)
  a.acc_min.setValue(98.002);a.acc_max.setValue(98.004);a.acc_filter.setChecked(True)
  assert len(a.judgement_rows)==21 and a.filtered==before
  assert sum(p[1] for p in a.day_plot.points)==137
  assert a.judge_table.rows[0]['Great']==sum(r['tapGreat'] for r in a.judgement_rows)
  assert filter_accuracy([{'achievements':None},{'achievements':0},{'achievements':98}],98,98)==[{'achievements':98}]
  a.acc_min.setValue(100);assert a.judgement_rows==[] and '下限' in a.judge_summary.text()
  a.acc_filter.setChecked(False);assert len(a.judgement_rows)==137
  a.show_play(0);app.processEvents()
  jt=a.play_judgements.table
  assert jt.minimumWidth()==jt.maximumWidth() and jt.minimumHeight()==jt.maximumHeight()
  for table in (jt,a.judge_table.table):
   for i in range(table.columnCount()):
    assert table.columnWidth(i)>=table.fontMetrics().horizontalAdvance(table.horizontalHeaderItem(i).text())+12
   assert table.height()>=table.horizontalHeader().height()+sum(table.rowHeight(i) for i in range(5))
  a.judge_table.query.setText('TAP');assert len(a.judge_table.filtered)==1
 finally:w.close();app.processEvents()


def test_rating_scope_acc_range_records_and_hover(tmp_path):
 from PySide6.QtCore import QPointF
 from app.archive_widgets import TimelinePlot
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));w.show();w.show_page(14);a=w.archives
 try:
  app.processEvents();before=list(a.rating_plot.points)
  assert a.trend_song.isHidden() and a.trend_acc_controls.isHidden()
  a.rating_chart_tabs.setCurrentIndex(1);app.processEvents()
  assert a.rating_detail_tabs.currentIndex()==2 and not a.trend_song.isHidden()
  a.trend_acc_min.setValue(98.002);a.trend_acc_max.setValue(98.004);a.trend_acc_filter.setChecked(True)
  assert len(a.song_plot.points)==21 and len(a.song_records.rows)==21 and a.rating_plot.points==before
  assert a.song_plot.axis_decimals==4 and a.rating_plot.integer_ticks
  a.trend_song.setCurrentIndex(1);key=a.trend_song.currentData()
  assert all((r['musicId'],r['level'])==key and 98.002<=r['achievements']<=98.004 for r in a.trend_rows)
  a.trend_acc_min.setValue(100);assert a.song_plot.points==[] and '下限' in a.rating_summary.text()
  a.trend_acc_filter.setChecked(False);assert len(a.trend_rows)>0
  a.rating_chart_tabs.setCurrentIndex(0);assert a.rating_detail_tabs.currentIndex()==0 and a.rating_plot.points==before
  plot=TimelinePlot();plot.hit=[(QPointF(10,10),'first'),(QPointF(10,80),'second')]
  assert plot.nearest_hit(QPointF(11,79))[1]=='second'
  assert plot.nearest_hit(QPointF(10,45)) is None
 finally:w.close();app.processEvents()

def test_trend_date_and_song_drilldown(tmp_path):
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));a=w.archives
 try:
  assert a.trend_acc_min.value()==97 and a.trend_acc_filter.isChecked()
  a.rating_records.sort(1);a.rating_records.move(1)
  source=a.rating_records.selected_source(0)
  a.rating_records.table.cellDoubleClicked.emit(0,1)
  assert a.trend_song.currentData()==(source['musicId'],source['level'])
  assert a.rating_chart_tabs.currentIndex()==1
  a.trend_start.setDate(QDate(2026,1,2));a.trend_end.setDate(QDate(2026,1,2));a.trend_date_filter.setChecked(True)
  assert len(a.rating_plot.points)==50 and {r['day'] for r in a.trend_rows}=={'2026-01-02'}
  a.song_records.table.cellDoubleClicked.emit(0,1)
  assert a.rating_chart_tabs.currentIndex()==1
  a.trend_start.setDate(QDate(2026,1,3));assert not a.rating_plot.points and '开始日期' in a.rating_summary.text()
  a.trend_date_filter.setChecked(False);assert len(a.rating_plot.points)==137
 finally:w.close();app.processEvents()

def test_progress_thumbnails_and_safe_manifest(tmp_path):
 from app.collection_metadata import entity_image
 import json
 root=tmp_path/'images';root.mkdir();(root/'ok.png').write_bytes(b'x')
 (root/'manifest.json').write_text(json.dumps({'entries':{'chara:1':{'file':'ok.png'},'chara:2':{'file':'../outside.png'}}}))
 assert entity_image(root,'chara',1)==str((root/'ok.png').resolve())
 assert entity_image(root,'chara',2) is None
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path/'profile'))
 try:
  view=w.archives.progress_views['userCharacterList']
  assert view.rows[0]['_imagePath'] and not view.table.item(0,0).icon().isNull()
  assert view.table.rowHeight(0)>=64
 finally:w.close();app.processEvents()
