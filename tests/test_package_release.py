import hashlib
import zipfile
import pytest
from tools.package_release import package


def test_only_program_files_are_published(tmp_path):
    source=tmp_path/'local';source.mkdir()
    (source/'AquaSync.exe').write_bytes(b'program')
    runtime=source/'_internal';runtime.mkdir();(runtime/'python.dll').write_bytes(b'runtime')
    (source/'user-data').mkdir();(source/'user-data/personal.sqlite3').write_bytes(b'private')
    (source/'logs').mkdir();(source/'logs/startup.log').write_text('private')
    (source/'AquaSync-desktop.json').write_text('private machine config')
    output=tmp_path/'release';result=package(source,output,'2.0')
    archive=output/'AquaSync-2.0-Portable.zip'
    with zipfile.ZipFile(archive) as bundle:
        assert sorted(bundle.namelist())==sorted(['AquaSync-2.0/AquaSync.exe','AquaSync-2.0/_internal/python.dll','AquaSync-2.0/使用说明.txt'])
        assert bundle.testzip() is None
    assert result['sha256']==hashlib.sha256(archive.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):package(source,output,'2.0')


@pytest.mark.parametrize('filename,content', [('personal.sqlite3',b'private'),('config.txt',b'C:\\Users\\sample_user\\private')])
def test_private_files_inside_runtime_are_rejected(tmp_path,filename,content):
    source=tmp_path/'local';source.mkdir();(source/'AquaSync.exe').write_bytes(b'program')
    runtime=source/'_internal';runtime.mkdir();(runtime/filename).write_bytes(content)
    with pytest.raises(ValueError):package(source,tmp_path/'release','2.0')
