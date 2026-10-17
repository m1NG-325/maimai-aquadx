import copy
import json
import os
from app.parser import parse_aquadx
from app.score_times import parse_play_time
from app.score_sorting import SORT_FIELDS,sort_scores,score_value


def test_best_and_latest_play_are_independent_and_logs_do_not_invent_best_rows():
    raw={'userMusicDetailList':[dict(musicId=1,level=2,achievement=1000000,playCount=8,lastPlayDate='2026-01-01 12:00:00'),dict(musicId=1,level=2,achievement=980000,playCount=9)],
         'userPlaylogList':[dict(musicId=1,level=2,playDate='2026-01-02',userPlayDate='2026-01-02 20:03:04.0'),dict(musicId=1,level=2,userPlayDate='invalid'),dict(musicId=2,level=3,userPlayDate='2026-01-03 00:00:00')]}
    before=copy.deepcopy(raw);p=parse_aquadx(raw)
    assert len(p['best'])==1 and p['best'][0]['achievement']==1000000 and p['best'][0]['playCount']==9
    assert p['best'][0]['lastPlayedAt'].startswith('2026-01-02T20:03:04')
    assert p['best'][0]['lastPlayedSource']=='userPlaylogList.userPlayDate'
    assert raw==before
    first=parse_play_time('2026-01-01T12:00:00+08:00')
    for value in ['2026-01-01T04:00:00Z',str(first['lastPlayedTimestamp']),first['lastPlayedTimestamp']/1000,'20260101120000']:
        assert parse_play_time(value)['lastPlayedTimestamp']==first['lastPlayedTimestamp']
    for value in [None,True,0,'bad','0000-00-00','99999999999999999999999',float('nan')]:assert parse_play_time(value) is None
    p=parse_aquadx({'userMusicDetailList':[dict(musicId=1,level=2,achievement=980000)]})
    assert 'lastPlayedTimestamp' not in p['best'][0]


def test_every_sort_key_both_directions_and_missing_values_last():
    rows=[dict(musicId=i+1,level=2,achievements=98+i/10,ds=ds,dxScore=dx,playCount=count,comboStatus=combo,lastPlayedTimestamp=time)
          for i,(ds,dx,count,combo,time) in enumerate([(14,1000,1,1,200),(None,2000,5,4,None),(12,500,10,3,100),(13,1500,2,2,300)])]
    original=copy.deepcopy(rows)
    for field,_ in SORT_FIELDS:
        for descending in [False,True]:
            ordered=sort_scores(rows,field,descending)
            values=[score_value(r,field) for r in ordered]
            known=[v for v in values if v is not None]
            assert known==sorted(known,reverse=descending)
            assert values==known+[None]*(len(values)-len(known))
    assert [r['comboStatus'] for r in sort_scores(rows,'fc')]==[4,3,2,1]
    assert [r['comboStatus'] for r in sort_scores(rows,'ap')][:2]==[4,3]
    assert rows==original


def test_native_sort_controls_and_old_snapshot_missing_time(tmp_path):
    os.environ['QT_QPA_PLATFORM']='offscreen'
    from PySide6.QtWidgets import QApplication
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    app=QApplication.instance() or QApplication([])
    core=DesktopCore(tmp_path/'profile',settings_path=tmp_path/'settings.json')
    charts=core.catalog('private')[:5]
    raw={'userMusicDetailList':[dict(musicId=c['music_id'],level=c['level_index'],achievement=980000+i*1000,comboStatus=i,playCount=5-i,deluxscoreMax=1000+i*100,lastPlayDate=f'2026-01-0{i+1} 12:00:00' if i<4 else 'invalid') for i,c in enumerate(charts)]}
    source=tmp_path/'synthetic.json';source.write_text(json.dumps(raw),encoding='utf-8');core.import_file(source,'example');before=core.db.player('example')
    w=MainWindow(core);w.nav.setCurrentRow(2);w.show();app.processEvents()
    try:
        assert w.score_sort.count()==8
        for i,(field,_) in enumerate(SORT_FIELDS):
            w.score_sort.setCurrentIndex(i)
            for index,descending in enumerate([True,False]):
                w.score_order.setCurrentIndex(index);app.processEvents()
                assert w.score_rows==sort_scores(w.data['privateCatalog']['rows'],field,descending)
        w.score_sort.setCurrentIndex(1);app.processEvents()
        assert w.scores.property('showPlayTime') and '4 张可用' in w.score_hint.text()
        w.score_mark.setCurrentIndex(2);assert all(r['comboStatus']>=3 for r in w.score_rows)
        assert core.db.player('example')==before
    finally:w.close();app.processEvents()


def test_rank_assets_are_transparent_high_resolution_and_high_dpi_ready():
    from pathlib import Path
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication
    os.environ['QT_QPA_PLATFORM']='offscreen'
    app=QApplication.instance() or QApplication([])
    from app.desktop_ui import crisp_pixmap
    folder=Path(__file__).resolve().parents[1]/'data/report_assets'
    for rank in ['d','c','b','bb','bbb','a','aa','aaa','s','sp','ss','ssp','sss','sssp']:
        image=QImage(str(folder/f'rating-rank_{rank}.png'))
        assert image.width()==256 and image.height()==120 and image.hasAlphaChannel()
    pix=crisp_pixmap(folder/'rating-rank_sssp.png',76,38,2)
    assert pix.width()==152 and pix.devicePixelRatioF()==2
