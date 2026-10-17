import os
from decimal import Decimal
import pytest
from app.calculations import rating
from app.rating_table import COLUMNS, reference_rows


def test_reference_values_and_minimal_extra_point():
    rows=reference_rows()
    assert len(rows)==31 and rows[0]['ds']==15 and rows[-1]['ds']==12
    row=next(r for r in rows if r['ds']==14)
    assert [row['cells'][i]['ra'] for i in (0,1,3,4,6,8,9,11,13)]==[315,312,302,299,293,288,285,278,271]
    assert row['cells'][2]['achievement']==100.1985 and row['cells'][2]['ra']==303
    for row in reference_rows(.1,20):
        for cell,(_,base,mode) in zip(row['cells'],COLUMNS):
            if cell['achievement'] is None:continue
            assert rating(row['ds'],cell['achievement'])[0]==cell['ra']
            if mode=='step':
                assert cell['ra']==rating(row['ds'],base)[0]+1
                previous=Decimal(str(cell['achievement']))-Decimal('.0001')
                assert rating(row['ds'],previous)[0]==cell['ra']-1
    assert reference_rows(.1,.1)[0]['cells'][2]['achievement'] is None


@pytest.mark.parametrize('low,high',[(15,12),(0,15),(.1,20.1),(12.05,15),(float('nan'),15)])
def test_invalid_range(low,high):
    with pytest.raises(ValueError):reference_rows(low,high)


def test_native_grid_click_range_and_live_calculator(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    from PySide6.QtCore import Qt
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    w=MainWindow(core);w.resize(1400,900);w.nav.setCurrentRow(6);w.show();app.processEvents()
    try:
        grid=w.rating_grid
        assert grid.rowCount()==31 and grid.columnCount()==14
        row=10
        grid.cellClicked.emit(row,2)
        assert w.calc_ds.value()==14 and w.calc_a.value()==100.1985
        assert w.calc_label.text()=='303 · SSS'
        w.calc_a.setValue(100.5);assert w.calc_label.text()=='315 · SSS+'
        w.calc_min.setValue(14);w.calc_max.setValue(14)
        assert grid.rowCount()==1 and grid.item(0,0).data(Qt.ItemDataRole.UserRole)['ra']==315
        w.calc_min.setValue(15);assert '不能' in w.calc_range_hint.text()
        w.calc_min.setValue(12);w.calc_max.setValue(15)
        for width in (1000,2000):
            w.resize(width,900);app.processEvents()
            assert grid.height()>250
            assert grid.horizontalHeader().minimumSectionSize()>=76
    finally:w.close();app.processEvents()
