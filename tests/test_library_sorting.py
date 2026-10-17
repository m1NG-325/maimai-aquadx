import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtCore import Qt,QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from app.desktop_ui import MainWindow,SortHeader
from app.versions import version_order
from tests.synthetic_sample import sample


def test_library_sort_preserves_chart_identity_and_filter_order(tmp_path):
    app=QApplication.instance() or QApplication([])
    core,_=sample(tmp_path);w=MainWindow(core);w.show();w.nav.setCurrentRow(4);app.processEvents()
    rows=[dict(music_id=mid,title=title,type=kind,difficulty=diff,level_index=level,ds=ds,version=version,
               score={'achievements':acc} if acc is not None else None)
          for mid,title,kind,diff,level,ds,version,acc in [
              (772,'Z','SD','MASTER',3,13.8,'maimai ORANGE',99.9),
              (11882,'A','DX','EXPERT',2,9.0,'maimai でらっくす PRiSM',100.2),
              (11663,'M','DX','ADVANCED',1,None,'maimai GreeN',None)]]
    core.library=lambda *args,**kwargs:rows
    w.render_library();t=w.library_table
    keys=[lambda r:r['title'].casefold(),lambda r:(r['type'],r['level_index']),lambda r:r['ds'] if r['ds'] is not None else -1,
          lambda r:version_order(r['version']),lambda r:r['score']['achievements'] if r['score'] else -1]
    for col,key in enumerate(keys):
        for order,reverse in [(Qt.SortOrder.AscendingOrder,False),(Qt.SortOrder.DescendingOrder,True)]:
            t.sortItems(col,order)
            assert [t.item(i,0).data(Qt.ItemDataRole.UserRole) for i in range(3)]==[r['music_id'] for r in sorted(rows,key=key,reverse=reverse)]
    opened=[];w.song_detail=opened.append
    t.cellDoubleClicked.emit(0,1)
    assert opened==[t.item(0,0).data(Qt.ItemDataRole.UserRole)]
    t.sortItems(2,Qt.SortOrder.DescendingOrder);w.render_library()
    assert t.item(0,0).data(Qt.ItemDataRole.UserRole)==772
    for view in [t,w.recommend]:
        header=view.horizontalHeader();assert isinstance(header,SortHeader)
        assert all('排序' in view.horizontalHeaderItem(i).toolTip() for i in range(view.columnCount()))
        QTest.mouseClick(header.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(header.sectionViewportPosition(1)+8,header.height()//2))
        assert header.sortIndicatorSection()==1
        assert not header.grab().isNull()
    w.close();app.processEvents()
