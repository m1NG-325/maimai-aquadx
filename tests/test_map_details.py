import os,json
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.map_metadata import read_map_details
from app.map_details_ui import reward_rows

def test_map_xml_last_plate_by_distance_and_unknown_progress(tmp_path):
 for name,xml in [('Map.xml','<MapData><name><id>9</id><str>Map</str></name><IsInfinity>false</IsInfinity><TreasureExDatas><MapTreasureExData><Distance>30</Distance><TreasureId><id>1</id></TreasureId></MapTreasureExData><MapTreasureExData><Distance>10</Distance><TreasureId><id>2</id></TreasureId></MapTreasureExData></TreasureExDatas></MapData>'),('a/MapTreasure.xml','<MapTreasureData><name><id>1</id><str>A</str></name><TreasureType>NamePlate</TreasureType><NamePlate><id>31</id><str>Last</str></NamePlate></MapTreasureData>'),('b/MapTreasure.xml','<MapTreasureData><name><id>2</id><str>B</str></name><TreasureType>NamePlate</TreasureType><NamePlate><id>11</id><str>First</str></NamePlate></MapTreasureData>')]:
  p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(xml,encoding='utf-8')
 m=read_map_details(tmp_path)['maps']['9'];assert m['lastPlateId']=='31' and m['lastPlateDistance']==30
 assert reward_rows(m,{'distance':20})[0]['state']=='未达到参考距离'
 assert reward_rows(m,{'distance':30})[0]['state']=='达到参考距离'
 assert reward_rows(m,{})[0]['state']=='距离未知'

def test_map_inspector_navigation_courses_and_character_alignment(tmp_path):
 from tests.test_archive_ui import core_with_archive
 from app.desktop_ui import MainWindow
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));w.show();a=w.archives
 try:
  assert w.nav.item(w.nav.count()-1).text()=='功能与数据说明'
  w.nav.setCurrentRow(w.nav.count()-1);assert w.pages.currentIndex()==12
  w.show_page(13);assert w.pages.currentIndex()==13 and w.nav.currentRow()==12
  w.show_page(15);view=a.progress_views['userCharacterList']
  for col in range(1,view.table.columnCount()):assert view.table.item(0,col).textAlignment()&Qt.AlignmentFlag.AlignHCenter
  assert not view.table.item(0,0).textAlignment()&Qt.AlignmentFlag.AlignHCenter
  maps=a.progress_views['userMapList'];maps.table.cellDoubleClicked.emit(0,0)
  assert a.map_detail_tabs.count()==1 and not a.map_detail_tabs.isWindow()
  panel=a.map_detail_tabs.widget(0);assert len(panel.reward_table.rows)==len(a.map_metadata['1']['rewards'])
  a.open_map_detail(0);assert a.map_detail_tabs.count()==1
  a.close_map_detail(0);assert a.map_detail_tabs.count()==0 and a.map_detail_tabs.isHidden()
  assert w.course_table.horizontalHeaderItem(2).text()=='定数'
  course=w.core.courses[w.course_choice.currentIndex()]
  lookup={(c['music_id'],c['level_index']):c for c in w.core.catalog('private')}
  for i,m in enumerate(course['musics']):
   ds=lookup.get((m['id'],m['difficulty']),{}).get('ds')
   assert w.course_table.item(i,2).text()==(str(ds) if ds is not None else '待核实')
 finally:w.close();app.processEvents()

def test_generated_routes_nameplate_images_are_consistent():
 from app.map_details_ui import map_image
 root=Path(__file__).resolve().parents[1];data=json.loads((root/'data/map_details.json').read_text(encoding='utf-8'))
 manifest=json.loads((root/'data/report_assets/archive/manifest.json').read_text(encoding='utf-8'))['entries']
 for mid,m in data['maps'].items():
  plates=[r for r in m['rewards'] if r['kind']=='NamePlate' and r.get('elementId') and r.get('distance') is not None]
  if plates:
   assert m['lastPlateDistance']==max(r['distance'] for r in plates)
   assert manifest['map:'+mid]['plateId']==m['lastPlateId']
   assert map_image(root/'data/report_assets/archive',m)
  else:assert map_image(root/'data/report_assets/archive',m) is None

def test_reward_artwork_and_music_cover_matches_all_known_nodes(tmp_path):
 from app.map_details_ui import reward_image
 from app.archive_widgets import ArchiveTable
 from PySide6.QtCore import QSize
 root=Path(__file__).resolve().parents[1];assets=root/'data/report_assets/archive'
 maps=json.loads((root/'data/map_details.json').read_text(encoding='utf-8'))['maps']
 kinds={'Character','NamePlate','Frame','Icon','MusicNew','MapTaskMusic','Challenge'}
 for m in maps.values():
  for r in m['rewards']:
   if r['kind'] in kinds:assert reward_image(assets,r),r
   if r['kind']=='Challenge':assert str(r.get('musicId','')).isdigit()
 app=QApplication.instance() or QApplication([])
 m=next(m for m in maps.values() if any(r['kind']=='MusicNew' for r in m['rewards']))
 rows=reward_rows(m,{'distance':0},assets)
 table=ArchiveTable([('距离','distance'),('类型','kind'),('名称','name')]);table.set_rows(rows)
 try:
  for i,row in enumerate(rows[:table.limit]):
   assert table.table.item(i,0).icon().isNull()
   assert table.table.item(i,2).icon().isNull()==(not bool(row['_imagePath']))
  table.sort(0)
  assert table.selected_source(0)['distance']==min(r['distance'] for r in rows)
  assert reward_image(assets,{'kind':'Challenge','elementId':'123','musicId':'../../bad'}) is None
 finally:table.close()
