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
    assert w.plate_canvas.model['scopeLabel']=='私服曲库'
    assert any(r['music_id']==chart['music_id'] and r['complete'] for g in w.plate_canvas.model['groups'] for r in g['charts'])
    assert w.plate_canvas.export_image(tmp_path/'magical.png')
    w.plate_only_missing.setChecked(True)
    assert all(not r['complete'] for g in w.plate_canvas.model['groups'] for r in g['charts'])
    w.plate_scope.setCurrentIndex(1);app.processEvents()
    assert new not in w.plate_names and w.active_plate_data['plates']==w.data['plateScopes']['cn']['plates']
    assert w.plate_canvas.model['scopeLabel']=='国服曲库'
    w.plate_scope.setCurrentIndex(2);app.processEvents()
    assert w.plate_canvas.model['scopeLabel']=='私服曲库（含删除曲目）'
    assert w.plate_canvas.export_image(tmp_path/'historical.png')
    w.song_detail(790);app.processEvents()
    assert w.detail_panels[-1].windowTitle()=='only my railgun'
    w.plate_scope.setCurrentIndex(0);app.processEvents()
    assert new in w.plate_names
    w.close();app.processEvents()


def test_region_membership_latest_and_historical_revived_charts(tmp_path):
    core,_=reference_player(tmp_path);data=core.overview('example')
    jp=data['plateScopes']['jp'];cn=data['plateScopes']['cn'];history=data['plateScopes']['jp_history']
    keys=lambda scope:{(c['music_id'],c['level_index']) for c in scope['plateCatalog']}
    assert (790,3) not in keys(jp) and (790,3) in keys(history)
    assert (11321,3) not in keys(jp) and (11321,3) in keys(history)
    assert (12072,3) in keys(jp) and (12072,3) in keys(history)  # RE!NCARN4T10N, verified jacket ID.
    assert (11639,3) not in keys(jp) and (11639,3) in keys(history)
    assert (12055,3) not in keys(jp) and (12055,3) not in keys(history)  # Never officially released.
    assert (525,3) not in keys(jp) and (525,3) in keys(history)  # Archived song absent from local restoration pack.
    assert (854,3) not in keys(history)  # Old utage must not become a normal chart through a private ID.
    assert all(c['music_id'] not in (19,19919,902,903,904,906,907) for c in history['plateCatalog'])
    revived=[c for c in history['plateCatalog'] if c['music_id']==397 and c['level_index']==3]
    assert {c['version'] for c in revived}=={'maimai ORANGE PLUS','maimai でらっくす MAGiCAL'}
    assert jp['plates']['maimai でらっくす UNiVERSE']['极']['total'] != cn['plates']['maimai でらっくす UNiVERSE']['极']['total']
    for scope in (jp,cn,history):
        for version,marks in scope['plates'].items():
            for mark,progress in marks.items():
                model=plate_report(scope,[],version,mark)
                assert sum(c['total'] for c in model['counts'])==progress['total']
                assert sum(c['completed'] for c in model['counts'])==progress['completed']


def test_cn_uses_exact_karen_requirements_and_remaster_exceptions(tmp_path):
    core,_=reference_player(tmp_path);cn=core.overview('example')['plateScopes']['cn']
    for version,marks in cn['plateRequirements'].items():
        for mark,required in marks.items():
            assert cn['plates'][version][mark]['total']==len(required)
    assert not cn['plates']['真']['将']['supported']
    assert cn['plates']['真']['极']['total']==85*4
    assert cn['plates']['舞']['极']['total']==516*4+59
    assert 'maimai でらっくす CiRCLE' not in cn['plates']


def test_milk_plus_name_legacy_catalog_compatibility_and_true_audit(tmp_path):
    from app.versions import canonical_version
    from app.calculations import plate_progress
    assert canonical_version('MiLK PLUS')==canonical_version('maimai MiLK PLUS')=='maimai MiLK PLUS'
    core,_=reference_player(tmp_path);data=core.overview('example')
    for scope in data['plateScopes'].values():
        assert 'maimai MiLK PLUS' in scope['plates']
        assert 'MiLK PLUS' not in scope['plates']
        assert scope['plates']['maimai MiLK PLUS']['极']['total']>0
    # Both aliases still participate in old-era 舞 when old standalone callers pass raw charts.
    chart=dict(music_id=1,level_index=3,title='Synthetic',version='MiLK PLUS')
    assert plate_progress([], [chart])['舞']['极']['total']==1
    chart['version']='maimai MiLK PLUS'
    assert plate_progress([], [chart])['舞']['极']['total']==1
    from app.calculations import enrich
    assert enrich([], [chart], current_version='MiLK PLUS')==[]
    history=data['plateScopes']['jp_history']
    assert history['plates']['真']['极']['total']==106*4
    current=data['plateScopes']['jp']
    assert current['plates']['真']['极']['total']==88*4
    masters={c['music_id'] for c in history['plateCatalog'] if c['level_index']==3 and c['version'] in ('maimai','maimai PLUS')}
    assert 70 in masters  # Retained in catalog, intentionally not in 真.
    assert not masters.intersection({902,903,904,906,907})  # Old mainland-only songs are outside the Japanese scope.
