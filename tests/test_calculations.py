import pytest
from app.calculations import rating, summarize
from app.database import Database
from app.parser import parse_aquadx
from tests.test_database import song


@pytest.mark.parametrize('a,ds,want,rank', [(100.5,14,315,'sssp'),(101,14,315,'sssp'),(100,14,302,'sss'),
 (97,14,271,'s'),(96.9999,14,239,'aaa'),(100.4999,14,312,'sss'),(0,14,0,'d'),(79.9999,10,102,'bbb')])
def test_rating_boundaries(a, ds, want, rank):
    assert rating(ds,a) == (want,rank)


def test_b50_is_partitioned_by_version_not_sd_dx(tmp_path):
    db = Database(tmp_path / 'a.db')
    songs = [song(i, 'old', kind='SD') for i in range(1,41)] + [song(10000+i,'new',True,'DX') for i in range(1,21)]
    songs.append(song(10099,'old',False,'DX'))
    db.import_catalog(songs)
    p = parse_aquadx({'userMusicDetailList':[{'musicId':int(s['id']),'level':3,'achievement':1005000} for s in songs]})
    s = summarize(p,db.charts())
    assert len(s['b50']['old']) == 35 and len(s['b50']['new']) == 15
    assert s['rating'] == 326 * 50
    assert summarize(p,db.charts(),'old')['b50']['new'][0]['version'] == 'old'
    with pytest.raises(ValueError):
        summarize(p,db.charts(),'missing')


def test_plate_denominator_missing_unplayed_and_remaster(tmp_path):
    db=Database(tmp_path/'a.db')
    a=song(1,'maimai GreeN'); a['ds'].append(15); a['level'].append('15')
    db.import_catalog([a,song(2,'maimai GreeN'),song(70),song(3,'maimai PLUS')])
    p=parse_aquadx({'userMusicDetailList':[{'musicId':1,'level':i,'achievement':1000000,'comboStatus':3,'syncStatus':3} for i in range(4)]})
    s=summarize(p,db.charts())
    assert s['plates']['maimai GreeN']['神']['total'] == 8
    assert s['plates']['maimai GreeN']['神']['completed'] == 4
    assert not s['plates']['maimai GreeN']['神']['achieved']
    assert s['plates']['舞']['神']['total'] == 17
    assert s['plates']['真']['神']['total'] == 4
    assert s['plates']['真']['将']['supported'] is False
    assert s['statistics']['apOrBetter'] == 4 and s['statistics']['fcOrBetter'] == 4


def test_unknown_scores_retained_and_not_guessed():
    p=parse_aquadx({'userMusicDetailList':[{'musicId':12051,'level':2,'achievement':1000000}]})
    s=summarize(p,[])
    assert len(s['records']) == 1 and s['rating'] == 0
    assert not s['calculation']['ratingComplete']
