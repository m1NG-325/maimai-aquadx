import copy
import json
import os
from pathlib import Path

from app.desktop_core import DesktopCore
from app.calculations import summarize
from app.report_models import plate_report
from app.versions import version_order


def reference_player(tmp_path):
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    chart=next(c for c in core.db.private_charts() if c['version'].endswith('MAGiCAL') and c['level_index']==2)
    source=tmp_path/'synthetic.json'
    source.write_text(json.dumps({'userMusicDetailList':[{'musicId':chart['music_id'],'level':2,'achievement':1000000,'comboStatus':1,'syncStatus':0,'playCount':1}]}),encoding='utf-8')
    core.import_file(source,'example')
    return core,chart


def test_full_reference_versions_and_all_report_denominators(tmp_path):
    core,chart=reference_player(tmp_path);payload=copy.deepcopy(core.db.player('example'))
    data=core.overview('example')
    versions=list(data['plates'])
    assert versions==sorted(versions,key=version_order)
    for suffix in ['PLUS','Splash PLUS','UNiVERSE PLUS','FESTiVAL PLUS','BUDDiES PLUS','CiRCLE','CiRCLE PLUS','MAGiCAL']:
        assert 'maimai でらっくす '+suffix in versions
    for version,marks in data['plates'].items():
        for mark,progress in marks.items():
            model=plate_report(data,core.db.charts(),version,mark)
            assert sum(c['total'] for c in model['counts'])==progress['total']
            assert sum(c['completed'] for c in model['counts'])==progress['completed']
            for difficulty in range(5):
                missing=plate_report(data,core.db.charts(),version,mark,difficulty,True)
                assert all(not r['complete'] for g in missing['groups'] for r in g['charts'])
    progress=data['plates'][chart['version']]['极']
    assert progress['completed']==1 and progress['total']>1
    assert data['plates']['真']['将']['supported'] is False
    assert core.db.player('example')==payload
    legacy=summarize(payload,core.db.charts())
    assert data['analysisPlates']==legacy['plates']
    assert data['rating']==legacy['rating'] and data['b50']==legacy['b50']
    assert not data['privateCatalog']['rows'][0]['lxnsSupported']


def test_plate_scope_switch_and_new_version_exports(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([])
    core,chart=reference_player(tmp_path);w=MainWindow(core);w.show();w.nav.setCurrentRow(3);app.processEvents()
    assert w.plate_scope.currentIndex()==0
    new='maimai でらっくす MAGiCAL'
    assert new in w.plate_names
    w.plate_version.setCurrentText(new);w.plate_difficulty.setCurrentIndex(2);w.plate_mark.setCurrentText('极');app.processEvents()
    assert w.plate_canvas.model['completed']==1
    assert w.plate_canvas.model['scopeLabel']=='完整私服参考曲库'
    assert any(r['music_id']==chart['music_id'] and r['complete'] for g in w.plate_canvas.model['groups'] for r in g['charts'])
    assert w.plate_canvas.export_image(tmp_path/'magical.png')
    w.plate_only_missing.setChecked(True)
    assert all(not r['complete'] for g in w.plate_canvas.model['groups'] for r in g['charts'])
    w.plate_scope.setCurrentIndex(1);app.processEvents()
    assert new not in w.plate_names and w.active_plate_data['plates']==w.data['analysisPlates']
    assert w.plate_canvas.model['scopeLabel']=='原分析曲库'
    w.plate_scope.setCurrentIndex(0);app.processEvents()
    assert new in w.plate_names
    w.close();app.processEvents()
