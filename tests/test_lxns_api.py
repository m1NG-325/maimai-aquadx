import httpx
from fastapi.testclient import TestClient
from app.main import create_app
from tests.test_lxns import catalog, payload, TOKEN
import json

ACTION={'X-AquaSync-Action':'1'}


def client(tmp_path):
    path=tmp_path/'lxns.json'; path.write_text(json.dumps(catalog()),encoding='utf8')
    calls=[]
    remote=[]
    def handler(r):
        calls.append(r)
        if r.url.path.endswith('/player/scores') and r.method=='GET':
            return httpx.Response(200,json={'success':True,'data':remote})
        if r.method=='GET':
            return httpx.Response(200,json={'success':True,'data':{'name':'目标','friend_code':123}})
        remote[:]=json.loads(r.content)['scores']
        return httpx.Response(200,json={'success':True})
    app=create_app(tmp_path/'a.db',tmp_path/'none.json',path,lambda:httpx.Client(transport=httpx.MockTransport(handler)))
    app.state.db.save_player('demo',payload(True))
    return TestClient(app), calls


def test_page_static_files_and_legacy_endpoint(tmp_path):
    c,_=client(tmp_path)
    assert c.get('/tools').status_code == 200 and '本地舞萌查分' in c.get('/tools').text
    page=c.get('/sync')
    assert page.status_code==200 and '把你的成绩' in page.text
    assert '把你的成绩' in c.get('/ui').text
    assert "script-src 'self'" in page.headers['Content-Security-Policy']
    assert c.get('/static/app.js').status_code==200
    assert c.get('/static/style.css').status_code==200
    assert c.get('/user/demo').json()['records'][0]['musicId']==10001
    assert 'records' not in c.get('/api/user/demo/dashboard').json()


def test_connect_cookie_session_and_disconnect(tmp_path):
    c,calls=client(tmp_path)
    r=c.post('/api/lxns/connect',json={'token':TOKEN},headers=ACTION)
    assert r.status_code==200 and TOKEN not in r.text
    assert 'httponly' in r.headers['set-cookie'].lower() and 'samesite=strict' in r.headers['set-cookie'].lower()
    assert c.get('/api/lxns/session').json()['connected']
    assert c.get('/api/user/demo/lxns/preview').json()['account']['friend_code']=='123'
    assert c.post('/api/lxns/disconnect',json={},headers=ACTION).status_code==200
    assert not c.get('/api/lxns/session').json()['connected']


def test_upload_checks_user_confirmation_partial_and_no_duplicates(tmp_path):
    c,calls=client(tmp_path)
    c.post('/api/lxns/connect',json={'token':TOKEN},headers=ACTION)
    plan=c.post('/api/user/demo/lxns/prepare',json={},headers=ACTION).json()
    body={'fingerprint':plan['fingerprint'],'confirmed':True,'allow_partial':True,'plan_id':plan['plan_id'],'selected_keys':['1:dx:3']}
    assert c.post('/api/user/demo/lxns/upload',json=dict(body,confirmed=False),headers=ACTION).status_code==422
    assert c.post('/api/user/demo/lxns/upload',json=dict(body,allow_partial=False),headers=ACTION).status_code==409
    assert not any(r.method=='POST' for r in calls)
    result=c.post('/api/user/demo/lxns/upload',json=body,headers=ACTION)
    assert result.status_code==200 and result.json()['submitted']==1 and result.json()['skipped']==1
    assert c.post('/api/user/demo/lxns/upload',json=body,headers=ACTION).status_code==409
    assert sum(r.method=='POST' for r in calls)==1
    assert result.json()['verification']['counts']['exact']==1


def test_cross_site_and_host_guard_prevents_network_calls(tmp_path):
    c,calls=client(tmp_path)
    assert c.post('/api/lxns/connect',json={'token':TOKEN}).status_code==403
    assert c.post('/api/lxns/connect',json={'token':TOKEN},headers=dict(ACTION,Origin='https://evil.example')).status_code==403
    assert c.get('/',headers={'Host':'evil.example'}).status_code==400
    assert calls==[]


def test_no_connection_no_upload_and_download_uses_target_catalog(tmp_path):
    c,calls=client(tmp_path)
    plan=c.get('/api/user/demo/lxns/preview').json()
    assert plan['exportable']==1
    assert c.post('/api/user/demo/lxns/upload',json={'fingerprint':plan['fingerprint'],'confirmed':True},headers=ACTION).status_code==401
    download=c.get('/api/user/demo/lxns/download')
    assert len(download.json()['scores'])==1
    assert 'attachment' in download.headers['Content-Disposition']
    assert download.headers['X-AquaSync-Rejected-Count']=='1'
    assert calls==[]


def test_backup_downloads_scoping_and_legacy_request_blocked(tmp_path):
    c,calls=client(tmp_path)
    c.post('/api/lxns/connect',json={'token':TOKEN},headers=ACTION)
    p=c.get('/api/user/demo/lxns/preview').json()
    old={'fingerprint':p['fingerprint'],'confirmed':True,'allow_partial':True}
    assert c.post('/api/user/demo/lxns/upload',json=old,headers=ACTION).status_code==409
    plan=c.post('/api/user/demo/lxns/prepare',json={},headers=ACTION).json()
    backup_id=plan['backup']['id']
    download=c.get('/api/user/demo/lxns/backups/'+backup_id)
    assert download.status_code==200 and download.json()['response']=={'success':True,'data':[]}
    assert TOKEN not in download.text
    assert c.get('/api/user/other/lxns/backups/'+backup_id).status_code==404
    assert c.get('/api/user/demo/lxns/backups').json()['backups'][0]['id']==backup_id
    assert not any(r.method=='POST' for r in calls)
