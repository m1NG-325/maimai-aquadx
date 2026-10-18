from fastapi.testclient import TestClient
from app.main import create_app
from tests.test_database import song
from aquasync import convert, main
import json


def client(tmp_path):
    api=create_app(tmp_path/'a.db',tmp_path/'missing.json')
    api.state.db.import_catalog([song()])
    return TestClient(api)


def test_import_get_export_and_notfound(tmp_path):
    c=client(tmp_path)
    assert c.get('/user/1').status_code == 404
    data={'userData':{'userName':'测试','playerRating':1},'userMusicDetailList':[{'musicId':1,'level':3,'achievement':1005000,'deluxscoreMax':0}]}
    assert c.post('/user/1/import',json=data).json()['records'] == 1
    s=c.get('/user/1').json()
    assert s['rating'] == 326 and s['player']['rating'] == 1
    assert c.get('/user/1/export/lxns').json()['scores'][0]['fc'] is None
    assert isinstance(c.get('/user/1/export/diving-fish').json(),list)
    assert c.get('/user/1?current_version=missing').status_code == 422
    assert c.get('/user/1/export/unknown').status_code == 422


def test_invalid_import_preserves_snapshot_and_export_conflict(tmp_path):
    c=client(tmp_path)
    c.post('/user/1/import',json={'userMusicDetailList':[{'musicId':9999,'level':3,'achievement':1000000}]})
    assert c.post('/user/1/import',json={}).status_code == 422
    assert c.get('/user/1').json()['best'][0]['musicId'] == 9999
    assert c.get('/user/1/export/lxns').status_code == 409
    response=c.get('/user/1/export/lxns?allow_partial=true')
    assert response.json() == {'scores': []} and response.headers['X-AquaSync-Rejected-Count'] == '1'
    assert c.get('/user/1/export-check/lxns').json()['rejected'][0]['musicId'] == 9999


def test_legacy_cli_and_player_persistence(tmp_path):
    c=client(tmp_path)
    src=tmp_path/'输入.json'; dst=tmp_path/'输出.json'
    src.write_text(json.dumps({'userMusicDetailList':[{'musicId':1,'level':3,'achievement':1005000}]}),encoding='utf-8-sig')
    convert(src,dst,db_path=tmp_path/'a.db',user_id='demo')
    assert json.loads(dst.read_text(encoding='utf-8'))['records'][0]['achievement'] == 1005000
    assert c.get('/user/demo').status_code == 200
    main([str(src),str(dst),'--db',str(tmp_path/'a.db'),'--format','lxns'])
    assert json.loads(dst.read_text(encoding='utf-8'))['scores'][0]['id'] == 1
