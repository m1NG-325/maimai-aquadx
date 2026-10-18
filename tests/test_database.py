import pytest
from app.database import Database


def song(mid=1, version='maimai', new=False, kind='SD'):
    return {'id': str(mid), 'title': '测试曲目', 'type': kind, 'ds': [1, 5, 10, 14.5],
            'level': ['1', '5', '10', '14+'], 'basic_info': {'from': version, 'is_new': new}}


def test_persistence_and_atomic_catalog(tmp_path):
    path = tmp_path / 'a.db'
    db = Database(path)
    assert db.import_catalog([song()]) == 4
    db.save_player('用户', {'records': [1]})
    assert Database(path).player('用户') == {'records': [1]}
    with pytest.raises(ValueError):
        db.import_catalog([song(), song()])
    assert len(db.charts()) == 4
    assert db.player("' OR 1=1 --") is None


@pytest.mark.parametrize('edit', [{'type': 'other'}, {'ds': [1]}, {'ds': [1, 5, float('nan'), 14]}, {'title': '\ufffd'}])
def test_bad_catalog(tmp_path, edit):
    with pytest.raises(ValueError):
        Database(tmp_path / 'a.db').import_catalog([dict(song(), **edit)])
