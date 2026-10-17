import copy
import json
import os
from pathlib import Path
from app.desktop_core import DesktopCore
from app.parser import parse_aquadx
from app.report_models import b50_report
from app.unified_catalog import UnifiedCatalog


def added_chart(core):
    old={(c['music_id'],c['level_index']) for c in core.db.charts()+core.db.private_charts()}
    return next(c for c in core.catalog('jp') if (c['music_id'],c['level_index']) not in old and c['ds'] is not None)


def synthetic(core,chart):
    p=parse_aquadx({'userMusicDetailList':[dict(musicId=chart['music_id'],level=chart['level_index'],achievement=980000)]})
    record=p['best'][0]
    p['ratingComposition']=dict(available=True,old=[],new=[dict(record)],warnings=[])
    p['sourceRatings']=dict(playerOldRating=0,playerNewRating=123,playerRating=123)
    core.db.save_player('example',p)
    return p


def test_added_metadata_reaches_every_desktop_consumer_and_updates_together(tmp_path):
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    chart=added_chart(core);payload=synthetic(core,chart);before=copy.deepcopy(payload)
    base_before=core.db.charts();private_before=core.db.private_charts()
    for suffix in ['', ' Updated']:
        if suffix:
            for scope in ['jp','jp_history']:
                for c in core.plate_catalogs['scopes'][scope]['charts']:
                    if (c['music_id'],c['level_index'],c['version'])==(chart['music_id'],chart['level_index'],chart['version']):
                        c['title']+=suffix;c['ds']=round(c['ds']+.1,1)
        report=core.overview('example')
        score=report['privateCatalog']['rows'][0]
        library=next(c for c in core.library('example') if c['music_id']==chart['music_id'] and c['level_index']==chart['level_index'])
        view=report['b50Views']['source'];card=b50_report(report,view,core.catalog('private'),'Private')['new'][0]
        plate=next(c for c in report['plateScopes']['jp']['plateCatalog'] if (c['music_id'],c['level_index'])==(chart['music_id'],chart['level_index']))
        recommend=report['recommendationScopes']['private']['rows'][0]
        assert {c['title'] for c in [score,library,card,plate,recommend]}=={chart['title']+suffix}
        assert len({c['ds'] for c in [score,library,card,plate,recommend]})==1
        assert card['ra'] is not None and card['ra']==report['best'][0]['ra']
        assert view['rating']==123 and view['new'][0]['achievement']==980000
        assert (library['score']['musicId'],library['score']['level'])==(chart['music_id'],chart['level_index'])
        assert core.db.player('example')==before
    assert core.db.charts()==base_before and core.db.private_charts()==private_before


def test_region_constants_partial_fields_and_historical_versions_stay_separate():
    def c(ds,version,source):return dict(music_id=1,level_index=3,title='Song',ds=ds,version=version,source=source,type='SD',level='14',is_new=False)
    history=[c(14,'maimai GreeN','old'),c(14.5,'maimai でらっくす MAGiCAL','jp')]
    snapshots={'scopes':{'jp':dict(charts=[c(None,'maimai でらっくす MAGiCAL','official')]),'jp_history':dict(charts=history),'cn':dict(charts=[c(12,'国服','cn')])}}
    index={(1,'standard',3):dict(ds=12.3,title='Song',level='12',version=25500,disabled=False)}
    before=copy.deepcopy((snapshots,index))
    catalog=UnifiedCatalog([],[],snapshots,index,[dict(version=25500,title='国服')])
    assert catalog.charts('private')[0]['ds']==14.5 and catalog.charts('cn')[0]['ds']==12.3
    assert catalog.charts('private')[0]['constantSource']=='jp'
    assert len(catalog.variants['private'])==2
    assert len(catalog.plate_scopes()['jp_history']['charts'])==2
    rows=catalog.charts('all');rows[0]['title']='changed'
    assert catalog.charts('all')[0]['title']=='Song' and (snapshots,index)==before


def test_library_region_switch_and_shared_song_detail(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication,QLabel
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json');chart=added_chart(core);synthetic(core,chart)
    w=MainWindow(core);w.resize(1400,900);w.show();w.nav.setCurrentRow(4);app.processEvents()
    try:
        w.library_query.setText(str(chart['music_id']));w.render_library()
        assert any(c['title']==chart['title'] for c in w.library_display)
        w.song_detail(chart['music_id']);app.processEvents()
        assert w.detail_panels[-1].windowTitle()==chart['title']
        assert any(str(chart['ds']) in label.text() for label in w.detail_panels[-1].findChildren(QLabel))
        w.library_scope.setCurrentIndex(2);app.processEvents()
        assert all(c.get('metadataRegion')=='cn' for c in w.library_display)
    finally:w.close();app.processEvents()
