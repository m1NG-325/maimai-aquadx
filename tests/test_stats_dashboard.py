import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from app.stats_dashboard import summarize,StatsDashboard

def test_statistics_buckets_and_unknown_values():
 rows=[dict(musicId=i,level=i%5,achievements=a,comboStatus=i%5,fs='',fc='') for i,a in enumerate([100.5,100,99.5,99,98,97,96.9999])]
 rows.append(dict(musicId=100001,level=5,achievements=None,fc='app',fs='fsd'))
 s=summarize(rows)
 assert s['total']==8 and sum(s['ranks'].values())==8 and sum(s['marks'].values())==8
 assert all(s['ranks'][name]==1 for name in ['SSS+','SSS','SS+','SS','S+','S','AAA 及以下','达成率未知'])
 assert s['kinds']['宴 / 特殊']==1 and s['known']==7
 assert s['difficulties'][5]['acc']==[] and s['marks']['app']==2
 assert summarize([])['average'] is None

def test_statistics_dashboard_resize_and_totals(tmp_path):
 from tests.test_archive_ui import core_with_archive
 from app.desktop_ui import MainWindow
 app=QApplication.instance() or QApplication([]);w=MainWindow(core_with_archive(tmp_path));w.nav.setCurrentRow(7);w.show()
 try:
  dashboard=w.stats;s=dashboard.summary
  assert s['total']==len(w.data['privateCatalog']['rows'])
  assert dashboard.metric_values[1].text()==f"{w.data['statistics']['chartPlayCount']:,}"
  for size in [(2560,1440),(1320,900),(1000,760)]:
   w.resize(*size);app.processEvents()
   assert dashboard.wide==(dashboard.viewport().width()>=1000)
   assert dashboard.difficulty.horizontalScrollBar().maximum()==0
  dashboard.set_data({'privateCatalog':{'rows':[]},'statistics':{}})
  assert dashboard.metric_values[0].text()=='0' and dashboard.difficulty.rowCount()==5
 finally:w.close();app.processEvents()
