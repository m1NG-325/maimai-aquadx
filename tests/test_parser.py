import pytest
from app.parser import parse_aquadx, parse_record


def row(**kw):
    return dict(musicId=10001, level=3, achievement=1005000, **kw)


def test_units_dx_zero_and_marks():
    r = parse_record(row(deluxscoreMax=0, dxScore=123, comboStatus=4, syncStatus=4, playCount=8))
    assert (r['achievements'], r['dxScore'], r['fc'], r['ap'], r['fs'], r['playCount']) == (100.5, 0, 'app', 'app', 'fsdp', 8)


def test_flat_nested_and_all_lists():
    p = parse_aquadx({'userMusicDetailList': [row()], 'musicDetailList': [dict(musicId=2, level=0, achievement=0)],
                     'userMusicList': [{'musicId': 3, 'userMusicDetailList': [dict(level=2, achievement=980000)]}]})
    assert len(p['records']) == 3
    assert p['best'][1]['musicId'] == 3


def test_independent_best_and_no_double_count():
    a = row(comboStatus=1, syncStatus=1, playCount=10, deluxscoreMax=80)
    b = dict(a, achievement=990000, comboStatus=3, syncStatus=5, deluxscoreMax=100, playCount=5)
    p = parse_aquadx({'userMusicDetailList': [a, b, a]})
    assert len(p['records']) == 3 and len(p['best']) == 1
    r = p['best'][0]
    assert (r['achievements'], r['fc'], r['fs'], r['dxScore'], r['playCount']) == (100.5, 'ap', 'fs', 100, 10)


@pytest.mark.parametrize('changes', [{'achievement': -1}, {'achievement': 1010001}, {'level': 2.1}, {'comboStatus': 8}, {'musicId': None}, {'syncStatus': 8}])
def test_invalid(changes):
    with pytest.raises(ValueError):
        parse_record(dict(row(), **changes))


def test_empty_is_valid_but_missing_is_not():
    assert parse_aquadx({'userMusicDetailList': []})['records'] == []
    with pytest.raises(ValueError):
        parse_aquadx({})
