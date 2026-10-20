import json
import sqlite3
import httpx
import pytest
from starlette.exceptions import HTTPException
from app.score_diff import differences, normalize_scores, verify_scores, BackupStore
from tests.test_lxns import catalog, payload, TOKEN
from app.lxns import LxnsService


def score(**changes):
    return dict({'id':1,'type':'dx','level_index':3,'achievements':99.0,'dx_score':100,'fc':'fc','fs':'fs'},**changes)


@pytest.mark.parametrize('edit,kind', [({},'same'),({'achievements':100},'higher'),({'fc':'ap'},'higher'),
 ({'dx_score':90},'lower'),({'fs':'sync'},'lower'),({'achievements':100,'fc':None},'mixed')])
def test_independent_field_changes(edit,kind):
    d=differences([score(**edit)],[score()])[0]
    assert d['category']==kind
    assert d['recommended'] == (kind=='higher')


def test_new_verification_and_null_marks():
    d=differences([score()],[])[0]
    assert d['category']=='new' and d['recommended']
    assert normalize_scores({'success':True,'data':[score(fc='',fs=None)]})[0]['fc'] is None
    r=verify_scores([score()],[score(achievements=100)])
    assert r['counts']['stronger']==1
    assert verify_scores([score()],[])['counts']['missing']==1
    assert verify_scores([score()],[score(dx_score=99)])['counts']['different']==1


def test_full_backup_is_scoped_persistent_and_not_credential_storage(tmp_path):
    store=BackupStore(tmp_path/'backup.db'); raw={'success':True,'data':[dict(score(),play_time='2026-10-14T10:00:00Z')]}
    info=store.save('demo',{'friend_code':'123','name':'账号'},raw,'preview')
    restored=BackupStore(tmp_path/'backup.db').get('demo',info['id'])
    assert restored['response']==raw
    assert store.get('other',info['id']) is None
    assert len(store.list('demo'))==1 and TOKEN not in json.dumps(restored)


def integration(tmp_path):
    path=tmp_path/'catalog.json'; path.write_text(json.dumps(catalog()),encoding='utf8')
    remote=[score(achievements=100.9,fc='app',fs='fsdp',dx_score=150)]
    control={'calls':[],'fail_after':False,'posted':False}
    def handler(request):
        control['calls'].append(request)
        if request.url.path.endswith('/player/scores'):
            if request.method=='POST':
                control['posted']=True
                remote[:]=json.loads(request.content)['scores']
                return httpx.Response(200,json={'success':True})
            if control['fail_after'] and control['posted']:
                return httpx.Response(503,json={})
            return httpx.Response(200,json={'success':True,'data':remote})
        return httpx.Response(200,json={'success':True,'data':{'friend_code':123,'name':'目标账号'}})
    s=LxnsService(path,lambda:httpx.Client(transport=httpx.MockTransport(handler)))
    sid,_=s.connect(TOKEN)
    return s,sid,remote,control


def submit(s,sid,plan,**kwargs):
    return s.upload(payload(),sid,plan['fingerprint'],False,True,plan['plan_id'],['1:dx:3'],**kwargs)


def test_downgrades_require_explicit_confirmation_and_backup_precedes_post(tmp_path):
    s,sid,remote,control=integration(tmp_path)
    plan=s.prepare(payload(),sid,'demo')
    assert plan['rows'][0]['category']=='lower' and not plan['rows'][0]['recommended']
    with pytest.raises(HTTPException):
        submit(s,sid,plan)
    assert not control['posted']
    result=submit(s,sid,plan,allow_lower=True)
    assert result['verification']['counts']['exact']==1
    backup=s.backups.get('demo',result['backup']['id'])
    assert backup['response']['data'][0]['achievements']==100.9
    assert backup['phase']=='pre-upload'


def test_remote_change_blocks_write(tmp_path):
    s,sid,remote,control=integration(tmp_path)
    plan=s.prepare(payload(),sid,'demo'); remote[0]['dx_score']=151
    with pytest.raises(HTTPException) as e:
        submit(s,sid,plan,allow_lower=True)
    assert e.value.status_code==409 and not control['posted']


def test_failed_backup_blocks_write_and_partial_selection_is_respected(tmp_path,monkeypatch):
    s,sid,remote,control=integration(tmp_path)
    plan=s.prepare(payload(),sid,'demo')
    def fail(*args):
        raise sqlite3.OperationalError('disk full')
    monkeypatch.setattr(s.backups,'save',fail)
    with pytest.raises(HTTPException) as e:
        submit(s,sid,plan,allow_lower=True)
    assert e.value.status_code==503 and not control['posted']


def test_readback_failure_is_separate_from_acceptance_and_legacy_write_blocked(tmp_path):
    s,sid,remote,control=integration(tmp_path)
    with pytest.raises(HTTPException):
        s.upload(payload(),sid,s.preview(payload(),sid)[0]['fingerprint'],False,True)
    assert not control['posted']
    plan=s.prepare(payload(),sid,'demo'); control['fail_after']=True
    result=submit(s,sid,plan,allow_lower=True)
    assert result['success'] and not result['verification']['available'] and result['backup']['id']


def test_multiple_rows_only_selected_score_is_posted(tmp_path):
    s,sid,remote,control=integration(tmp_path)
    c=catalog(); c['songs'].append({'id':2,'title':'第二曲','difficulties':{'dx':[{'difficulty':3,'level':'14'}],'standard':[]}})
    s.catalog_path.write_text(json.dumps(c),encoding='utf8')
    p=payload(); p['best'].append(dict(p['best'][0],musicId=10002))
    plan=s.prepare(p,sid,'demo')
    result=s.upload(p,sid,plan['fingerprint'],False,True,plan['plan_id'],['2:dx:3'])
    posted=next(r for r in control['calls'] if r.method=='POST')
    assert [r['id'] for r in json.loads(posted.content)['scores']]==[2]
    assert result['submitted']==1 and result['notSelected']==1


@pytest.mark.parametrize('response',[{'success':True,'data':None},{'success':True,'data':[score(fc='unknown')]},
 {'success':True,'data':[score(),score()]},{'success':True,'data':[score(achievements=float('nan'))]}])
def test_invalid_remote_scores_are_not_silently_skipped(response):
    with pytest.raises(ValueError):
        normalize_scores(response)
