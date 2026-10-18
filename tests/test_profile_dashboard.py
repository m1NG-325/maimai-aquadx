import os
os.environ['QT_QPA_PLATFORM']='offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.profile_dashboard import ProfileHero


def test_missing_profile_values_are_not_fabricated(tmp_path):
    app=QApplication.instance() or QApplication([]);hero=ProfileHero()
    hero.set_data({'sections':{'userData':{'userName':'<b>Player</b>','playerRating':0}}},tmp_path)
    assert hero.name.textFormat()==Qt.TextFormat.PlainText
    assert [v.text() for v in hero.values]==['0','—','—','—']
    hero.close();app.processEvents()


def test_profile_details_filters_and_collection_preview(tmp_path):
    from tests.test_archive_ui import core_with_archive
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([]);core=core_with_archive(tmp_path);before=core.db.player('example');w=MainWindow(core);w.show_page(16);w.resize(1320,900);w.show();a=w.archives
    try:
        app.processEvents()
        assert a.profile_hero.values[1].text()=='15,000' and a.profile_hero.values[3].text()=='2'
        for view in (a.profile_table,a.option_table,a.extend_table,a.udemae):assert view.table.isColumnHidden(2)
        a.profile_raw.setChecked(True)
        for view in (a.profile_table,a.option_table,a.extend_table,a.udemae):assert not view.table.isColumnHidden(2)
        a.profile_tabs.setCurrentIndex(3);app.processEvents()
        assert not a.collection_table.table.item(0,0).icon().isNull()
        row=a.collection_table.selected_source(0);assert a.collection_preview.name.text()==row['name']
        a.collection_table.query.setText('no-matching-item');assert a.collection_table.table.rowCount()==0
        assert '暂无' in a.collection_preview.name.text()
        a.collection_table.query.clear();a.collection_mode.setCurrentIndex(2)
        assert not a.collection_kind.isEnabled() and not a.valid_items.isEnabled()
        assert len(a.collection_table.rows)==2
        a.collection_table.sort(2);assert a.collection_preview.name.text()==a.collection_table.selected_source(0)['name']
        w.resize(1000,800);app.processEvents();assert not a.collection_preview.isVisible()
        assert core.db.player('example')==before
    finally:w.close();app.processEvents()
