import os,json
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.activity_metadata import read_activity_details
from app.activity_details_ui import bonus_image
from app.map_details_ui import reward_image

def test_activity_xml_preserves_types_and_random_rules(tmp_path):
 xml='<LoginBonusData><name><id>8</id><str>Frame reward</str></name><BonusType>Frame</BonusType><FrameId><id>3</id><str>Frame</str></FrameId><PartnerId><id>1</id><str>Unused</str></PartnerId><maxPoint>10</maxPoint><IsRepeatGet>true</IsRepeatGet></LoginBonusData>'
 (tmp_path/'LoginBonus.xml').write_text(xml,encoding='utf-8')
 (tmp_path/'Course.xml').write_text('<CourseData><name><id>9</id><str>Random</str></name><isRandom>true</isRandom><courseMusicData><CourseMusicData><musicId><id>772</id><str>Placeholder</str></musicId><difficulty><id>2</id></difficulty></CourseMusicData></courseMusicData></CourseData>',encoding='utf-8')
 data=read_activity_details(tmp_path);b=data['bonuses']['8']
 assert b['reward']['kind']=='Frame' and b['reward']['elementId']=='3' and b['maxPoint']=='10' and b['repeat']
 assert data['courses']['9']['random'] and data['courses']['9']['musics'][0]['musicId']==772

def test_all_reference_bonus_images_and_fixed_course_covers():
 root=Path(__file__).resolve().parents[1];assets=root/'data/report_assets/archive';data=json.loads((root/'data/activity_details.json').read_text(encoding='utf-8'))
 assert len(data['bonuses'])==72
 for b in data['bonuses'].values():assert bonus_image(assets,b),b
 for c in data['courses'].values():
  if c['random']:continue
  for m in c['musics']:assert reward_image(assets,{'kind':'MusicNew','elementId':str(m['musicId'])})

def test_course_bonus_details_are_embedded_and_random_has_no_fake_songs(tmp_path):
 from tests.test_archive_ui import core_with_archive
 from app.desktop_ui import MainWindow
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));w.show_page(15);w.show();a=w.archives
 try:
  view=a.progress_views['userCourseList'];assert len(view.rows[0]['_imagePaths'])==4 and not view.table.item(0,0).icon().isNull()
  view.table.cellDoubleClicked.emit(0,0);tabs=a.activity_detail_tabs['userCourseList'];panel=tabs.widget(0)
  assert tabs.count()==1 and not panel.isWindow() and len(panel.song_table.rows)==4
  a.open_activity_detail('userCourseList',0);assert tabs.count()==1
  random_id=next(k for k,c in a.activity_metadata['courses'].items() if c['random'])
  a.sections['userCourseList']=[dict(courseId=int(random_id),playCount=1)];a.render_progress()
  assert a.progress_views['userCourseList'].rows[0]['_imagePaths']==[]
  a.open_activity_detail('userCourseList',0);assert not hasattr(tabs.currentWidget(),'song_table')
  bonus_id=next(k for k,b in a.activity_metadata['bonuses'].items() if b['reward']['kind']=='Frame')
  a.sections['userLoginBonusList']=[dict(bonusId=int(bonus_id),point=9,isCurrent=True,isComplete=True)];a.render_progress()
  view=a.progress_views['userLoginBonusList'];assert view.rows[0]['kindLabel']=='背景框' and view.rows[0]['isComplete'] is True
  assert not view.table.item(0,0).icon().isNull()
  view.table.cellDoubleClicked.emit(0,0);bt=a.activity_detail_tabs['userLoginBonusList'];assert bt.count()==1 and not bt.currentWidget().isWindow()
  a.refresh();assert tabs.count()==0 and bt.count()==0
 finally:w.close();app.processEvents()

def test_fixed_course_is_safe_during_first_window_construction(tmp_path):
 from tests.test_archive_ui import core_with_archive
 from app.desktop_ui import MainWindow
 from app.activity_metadata import load_activity_details
 core=core_with_archive(tmp_path)
 metadata=core.activity_details()
 fixed=next(int(k) for k,v in metadata['courses'].items() if not v.get('random') and v.get('musics'))
 payload=core.db.player('example')
 payload['archive']['sections']['userCourseList']=[dict(courseId=fixed,playCount=1)]
 core.db.save_player('example',payload)
 app=QApplication.instance() or QApplication([])
 w=MainWindow(core)
 try:
  assert w.archives.progress_views['userCourseList'].rows[0]['_imagePaths']
 finally:w.close();app.processEvents()
