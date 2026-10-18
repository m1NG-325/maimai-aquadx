import json
import time
import httpx
import pytest
from fastapi import HTTPException
from app.lxns import LxnsService, catalog_index
from app.parser import parse_aquadx

TOKEN = 'test-personal-key'


def catalog():
    return {'songs': [{'id': 1, 'title': '测试曲', 'difficulties': {'standard': [], 'dx': [
        {'difficulty': 3, 'level': '14+'}]}}]}


def payload(unknown=False):
    rows = [{'musicId':10001,'level':3,'achievement':1005000,'comboStatus':4,'syncStatus':4,'deluxscoreMax':123}]
    if unknown:
        rows.append({'musicId':12051,'level':2,'achievement':980000})
    return parse_aquadx({'userMusicDetailList':rows})


def service(tmp_path, handler=None):
    path=tmp_path/'lxns.json'; path.write_text(json.dumps(catalog()),encoding='utf8')
    calls=[]
    remote=[]
    def request(r):
        calls.append(r)
        if handler:
            return handler(r)
        if r.url.path.endswith('/song/list'):
            assert 'X-User-Token' not in r.headers
            return httpx.Response(200,json=catalog())
        assert r.headers['X-User-Token'] == TOKEN and 'Authorization' not in r.headers
        if r.url.path.endswith('/player/scores') and r.method == 'GET':
            return httpx.Response(200,json={'success':True,'data':remote})
        if r.method == 'GET':
            return httpx.Response(200,json={'success':True,'data':{'friend_code':123456789,'name':'目标玩家','rating':12345}})
        remote[:] = json.loads(r.content)['scores']
        return httpx.Response(200,json={'success':True,'code':200,'data':None})
    s=LxnsService(path,lambda:httpx.Client(transport=httpx.MockTransport(request)))
    return s,calls


def test_connect_personal_api_token_stays_private(tmp_path):
    s,calls=service(tmp_path)
    sid,account=s.connect(TOKEN)
    assert account['friend_code'] == '123456789'
    assert TOKEN not in json.dumps(account)
    assert calls[0].url.path == '/api/v0/user/maimai/player'
    assert len(sid)>30
    s.disconnect(sid)
    assert s.session(sid) is None


def test_actual_target_catalog_and_best_body(tmp_path):
    s,_=service(tmp_path)
    preview,body=s.preview(payload(True))
    assert preview['total']==2 and preview['exportable']==1 and len(preview['rejected'])==1
    assert body['scores'][0] == {'id':1,'type':'dx','level_index':3,'achievements':100.5,'dx_score':123,'fc':'app','fs':'fsdp'}


def test_upload_requires_confirmation_and_same_preview(tmp_path):
    s,calls=service(tmp_path); sid,_=s.connect(TOKEN)
    preview=s.prepare(payload(),sid,'demo')
    for fingerprint,confirmed in [(preview['fingerprint'],False),('stale',True)]:
        with pytest.raises(HTTPException):
            s.upload(payload(),sid,fingerprint,False,confirmed,preview['plan_id'],[r['key'] for r in preview['rows']])
    assert not any(r.method=='POST' for r in calls)
    result=s.upload(payload(),sid,preview['fingerprint'],False,True,preview['plan_id'],[r['key'] for r in preview['rows']])
    assert result['success'] and result['submitted']==1
    posted=next(r for r in calls if r.method=='POST')
    assert posted.url.path=='/api/v0/user/maimai/player/scores'
    assert json.loads(posted.content)['scores'][0]['id']==1
    assert result['verification']['counts']['exact']==1
    with pytest.raises(HTTPException) as e:
        s.upload(payload(),sid,preview['fingerprint'],False,True,preview['plan_id'],[r['key'] for r in preview['rows']])
    assert e.value.status_code==409 and sum(r.method=='POST' for r in calls)==1


def test_partial_is_explicit_and_credentials_expire(tmp_path):
    s,calls=service(tmp_path); sid,_=s.connect(TOKEN)
    preview=s.prepare(payload(True),sid,'demo')
    with pytest.raises(HTTPException):
        s.upload(payload(True),sid,preview['fingerprint'],False,True,preview['plan_id'],['1:dx:3'])
    assert not any(r.method=='POST' for r in calls)
    assert s.upload(payload(True),sid,preview['fingerprint'],True,True,preview['plan_id'],['1:dx:3'])['skipped']==1
    s.sessions[sid]['expires']=time.monotonic()-1
    with pytest.raises(HTTPException) as e:
        s.upload(payload(),sid,preview['fingerprint'],False,True)
    assert e.value.status_code==401


@pytest.mark.parametrize('status',[401,403,404,429,500])
def test_upstream_errors_do_not_echo_secrets(tmp_path,status):
    s,_=service(tmp_path,lambda r:httpx.Response(status,json={'message':TOKEN}))
    with pytest.raises(HTTPException) as e:
        s.connect(TOKEN)
    assert TOKEN not in str(e.value.detail)


def test_http_200_business_failure_is_not_success(tmp_path):
    s,_=service(tmp_path,lambda r:httpx.Response(200,json={'success':False,'code':401,'message':TOKEN}))
    with pytest.raises(HTTPException) as e:
        s.connect(TOKEN)
    assert e.value.status_code==401


def test_bad_catalog_refresh_preserves_snapshot(tmp_path):
    s,_=service(tmp_path,lambda r:httpx.Response(200,json={'songs':[]}))
    previous=s.catalog_path.read_bytes()
    with pytest.raises(HTTPException):
        s.refresh_catalog()
    assert s.catalog_path.read_bytes()==previous


def test_refresh_has_no_credential_and_new_account_invalidates_preview(tmp_path):
    s,calls=service(tmp_path)
    preview,_=s.preview(payload())
    sid,_=s.connect(TOKEN)
    with pytest.raises(HTTPException):
        s.upload(payload(),sid,preview['fingerprint'],False,True)
    assert s.refresh_catalog()['charts']==1
    assert calls[-1].url.host=='maimai.lxns.net'
