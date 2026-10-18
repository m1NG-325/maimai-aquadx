import json
import sys
from types import SimpleNamespace
from pathlib import Path
from app import desktop_bootstrap as boot


def test_studio_import_failure_is_reported(tmp_path, monkeypatch):
    result = tmp_path / 'nested' / 'result.json'
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setattr('app.desktop_storage.installation_directory', lambda: tmp_path)
    monkeypatch.setattr(sys, 'argv', ['AquaSync', '--self-test', '--result', str(result)])
    def fail():
        raise RuntimeError('test startup failure')
    monkeypatch.setitem(sys.modules, 'app.studio_theme', SimpleNamespace(install=fail))
    assert boot.run(studio=True) == 1
    assert 'test startup failure' in json.loads(result.read_text(encoding='utf8'))['error']
    assert 'test startup failure' in (tmp_path/'logs/startup.log').read_text(encoding='utf8')


def test_normal_exit_and_icon(tmp_path, monkeypatch):
    monkeypatch.setenv('LOCALAPPDATA', str(tmp_path))
    monkeypatch.setattr('app.desktop_storage.installation_directory', lambda: tmp_path)
    monkeypatch.setattr(sys, 'argv', ['AquaSync'])
    monkeypatch.setitem(sys.modules, 'desktop', SimpleNamespace(main=lambda: 0))
    assert boot.run() == 0
    assert 'Exited normally: 0' in (tmp_path/'logs/startup.log').read_text(encoding='utf8')
    from PIL import Image
    image = Image.open(Path(__file__).resolve().parents[1]/'data/report_assets/aquasync.ico')
    assert {(16,16),(32,32),(48,48),(256,256)} <= image.ico.sizes()
