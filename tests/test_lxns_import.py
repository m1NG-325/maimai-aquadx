import csv
import io
import os
import pytest
from app.lxns_import import parse_lxns_csv


def sample(**changes):
    row = dict(id='1020', song_name='Endless, Sleepless Night', level='8', level_index='2',
               achievements='100.1234', fc='fcp', fs='sync', dx_score='716', song_type='dx',
               upload_time='2026-10-14 14:14:57', play_time='')
    row.update(changes)
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(row))
    writer.writeheader(); writer.writerow(row)
    return out.getvalue()


def test_units_types_marks_quoted_title_and_missing_time():
    payload = parse_lxns_csv('\ufeff'+sample())
    r = payload['best'][0]
    assert (r['musicId'], r['level'], r['achievement'], r['dxScore']) == (11020, 2, 1001234, 716)
    assert (r['fc'], r['comboStatus'], r['fs'], r['syncStatus']) == ('fcp', 2, 'sync', 5)
    assert 'lastPlayedAt' not in r
    assert not payload['archive']['available'] and not payload['ratingComposition']['available']
    assert payload['importInfo']['rows'][0]['song_name'] == 'Endless, Sleepless Night'
    timed = parse_lxns_csv(sample(song_type='standard', play_time='2026-10-13 18:15:16'))['best'][0]
    assert timed['musicId'] == 1020 and timed['lastPlayedAt'].startswith('2026-10-13T18:15:16')


@pytest.mark.parametrize('change', [dict(id='11020'), dict(song_type='utage'), dict(level_index='5'),
    dict(achievements='NaN'), dict(achievements='Infinity'), dict(achievements='101.0001'),
    dict(achievements='99.12345'), dict(fc='bad'), dict(fs='bad'), dict(dx_score='-1'),
    dict(play_time='invalid'), dict(level_index='1.5')])
def test_invalid_row_is_rejected(change):
    with pytest.raises(ValueError, match='第 2 行'):
        parse_lxns_csv(sample(**change))


def test_invalid_structure_and_empty_file():
    for text in ['', 'id,song_name\n1,a', sample().splitlines()[0], sample()+'1,broken\n', sample().replace('id,song_name', 'id,id')]:
        with pytest.raises(ValueError): parse_lxns_csv(text)


def test_snapshot_atomic_offline_and_export_roundtrip(tmp_path, monkeypatch):
    from app.desktop_core import DesktopCore
    core = DesktopCore(tmp_path/'profile')
    monkeypatch.setattr(core.lxns, 'request', lambda *a, **k: pytest.fail('Unexpected network access'))
    path = tmp_path/'scores.csv'; path.write_text(sample(), encoding='utf-8-sig')
    payload = core.import_file(path, 'lxns')
    preview, body = core.lxns.preview(payload)
    assert body['scores'][0] == dict(id=1020, type='dx', level_index=2, achievements=100.1234,
                                     dx_score=716, fc='fcp', fs='sync')
    report = core.overview('lxns')
    assert report['statistics']['charts'] == 1
    path.write_text(sample(fs='bad'), encoding='utf-8')
    with pytest.raises(ValueError): core.import_file(path, 'lxns')
    assert core.db.player('lxns') == payload
    assert DesktopCore(tmp_path/'profile').db.player('lxns') == payload


def test_desktop_csv_button_imports(tmp_path, monkeypatch):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton
    from app.desktop_core import DesktopCore
    from app.desktop_ui import MainWindow
    app = QApplication.instance() or QApplication([])
    core = DesktopCore(tmp_path/'profile')
    monkeypatch.setattr(core.lxns, 'request', lambda *a, **k: pytest.fail('Unexpected network access'))
    path = tmp_path/'scores.csv'; path.write_text(sample(), encoding='utf-8')
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a: (str(path), 'CSV (*.csv)'))
    monkeypatch.setattr(QMessageBox, 'information', lambda *a: QMessageBox.StandardButton.Ok)
    monkeypatch.setattr(QMessageBox, 'critical', lambda *a: pytest.fail(str(a)))
    window = MainWindow(core); window.user.setCurrentText('lxns')
    button = next(b for b in window.findChildren(QPushButton) if b.text() == '导入落雪 CSV')
    button.click()
    assert core.db.player('lxns')['source'] == 'Lxns CSV'
    assert window.data['statistics']['charts'] == 1
    assert window.b50_mode.currentIndex() == 2
    assert '落雪 CSV' in window.metric_label.text()
    window.close(); app.processEvents()


def test_duplicate_charts_keep_independent_best_fields():
    text = sample(achievements='99', fc='ap', fs='fsd', dx_score='900')
    text += sample(achievements='100', fc='', fs='sync', dx_score='800').split('\n', 1)[1]
    payload = parse_lxns_csv(text)
    assert len(payload['records']) == 2 and len(payload['best']) == 1
    best = payload['best'][0]
    assert (best['achievement'], best['dxScore'], best['fc'], best['fs']) == (1000000, 900, 'ap', 'fsd')
