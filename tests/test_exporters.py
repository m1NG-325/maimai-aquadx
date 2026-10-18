import pytest
from app.parser import parse_aquadx
from app.calculations import summarize
from app.database import Database
from app.exporters import export_scores, ExportError
from tests.test_database import song


def test_request_bodies_and_id_mapping(tmp_path):
    db=Database(tmp_path/'a.db'); db.import_catalog([song(10001,'new',True,'DX'),song(1)])
    p=parse_aquadx({'userMusicDetailList':[{'musicId':mid,'level':3,'achievement':1001234,'comboStatus':4,'syncStatus':4,'deluxscoreMax':123} for mid in (1,10001)]})
    s=summarize(p,db.charts())
    fish,_=export_scores(s,'diving-fish'); lxns,_=export_scores(s,'lxns')
    assert isinstance(fish,list) and fish[1]['song_id'] == 10001
    assert fish[1]['achievements'] == 100.1234 and fish[1]['dxScore'] == 123
    assert lxns['scores'][1]['id'] == lxns['scores'][0]['id'] == 1
    assert {r['type'] for r in lxns['scores']} == {'standard','dx'}
    assert lxns['scores'][1]['fs'] == 'fsdp'


def test_default_reject_and_partial_report():
    p=parse_aquadx({'userMusicDetailList':[{'musicId':12051,'level':2,'achievement':980000}]})
    s=summarize(p,[])
    with pytest.raises(ExportError) as e:
        export_scores(s,'lxns')
    assert e.value.rejected[0]['musicId'] == 12051
    body,rejected=export_scores(s,'lxns',True)
    assert body == {'scores': []} and len(rejected) == 1
