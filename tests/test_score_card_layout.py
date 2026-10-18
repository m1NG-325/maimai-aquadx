import json
import os


def test_responsive_rows_and_single_card_selection_preserve_scores(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication,QTableWidget
    from PySide6.QtCore import Qt
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    charts=core.catalog('private')[:20]
    source=tmp_path/'synthetic.json'
    source.write_text(json.dumps({'userMusicDetailList':[dict(musicId=c['music_id'],level=c['level_index'],achievement=980000+i,playCount=1) for i,c in enumerate(charts)]}),encoding='utf-8')
    core.import_file(source,'example');before=core.db.player('example')
    w=MainWindow(core);w.nav.setCurrentRow(2);w.show()
    try:
        w.resize(2560,1440);app.processEvents();app.processEvents()
        wide=w.scores.rowHeight(0)
        w.resize(1000,760);app.processEvents();app.processEvents()
        narrow=w.scores.rowHeight(0)
        assert wide==112 and narrow==132
        assert w.scores.columnCount()==2 and w.scores.rowCount()==10
        assert w.scores.selectionBehavior()==QTableWidget.SelectionBehavior.SelectItems
        w.scores.setCurrentCell(0,1)
        assert [(i.row(),i.column()) for i in w.scores.selectedIndexes()]==[(0,1)]
        assert [w.scores.item(i//2,i%2).data(Qt.ItemDataRole.UserRole)['achievement'] for i in range(20)]==list(range(980019,979999,-1))
        assert core.db.player('example')==before
    finally:w.close();app.processEvents()
