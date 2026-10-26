"""Create a public portable ZIP from executable/runtime files only."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


def package(source, output, version):
    source, output = source.resolve(), output.resolve()
    exe = source / 'AquaSync.exe'
    runtime = source / '_internal'
    if not exe.is_file() or not runtime.is_dir():
        raise ValueError('Expected AquaSync.exe and _internal in the source directory')
    files = [exe] + sorted(p for p in runtime.rglob('*') if p.is_file())
    forbidden = {'user-data', 'logs', '.private-local', '.validation', 'tests', 'fixtures'}
    data_names = {'music_data.json', 'private_music_data.json', 'plate_catalogs.json',
                  'lxns_song_list.json', 'karen_courses.json', 'collection_metadata.json',
                  'map_details.json', 'activity_details.json', 'report_assets'}
    for path in files:
        relative = path.relative_to(source)
        if any(p.is_symlink() or p.is_junction() for p in [path, *path.parents] if p != source.parent):
            raise ValueError(f'Refusing linked release file: {relative}')
        if forbidden.intersection(relative.parts) or path.suffix.lower() in {'.sqlite3', '.sqlite', '.db', '.jsonl', '.log'}:
            raise ValueError(f'Private/runtime state in release: {relative}')
        if path.name == 'AquaSync-desktop.json':
            raise ValueError('Machine-specific configuration in release')
        if len(relative.parts) > 2 and relative.parts[:2] == ('_internal', 'data'):
            if relative.parts[2] not in data_names:
                raise ValueError(f'Unexpected bundled data: {relative}')
        if path.suffix.lower() in {'.json', '.txt', '.md', '.ini', '.cfg'}:
            content = path.read_bytes()
            if re.search(rb'[A-Z]:[\\/]Users[\\/][^\\/]+[\\/]|[A-Z]:[\\/]Codex[\\/]', content, re.I):
                raise ValueError(f'Local machine path in release text: {relative}')
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'AquaSync-{version}-Portable.zip'
    if archive.exists():
        raise FileExistsError(f'Refusing to overwrite an existing release: {archive}')
    prefix = f'AquaSync-{version}'
    instructions = ('AquaSync ' + version + '\n\n'
                    '1. 完整解压文件夹到你选择的位置。\n'
                    '2. 双击 AquaSync.exe，无需安装 Python。\n'
                    '3. 点击“导入 AquaDX JSON”或“导入落雪 CSV”，选择自己的成绩导出文件。\n\n'
                    '请保留 _internal 文件夹，不要在压缩包内直接运行 EXE。\n'
                    '个人数据保存在 user-data；日志在 logs；本包不包含任何玩家成绩或本机配置。\n'
                    '更新时先关闭程序，保留 user-data 和 AquaSync-desktop.json。\n')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in files:
            bundle.write(path, f'{prefix}/{path.relative_to(source).as_posix()}')
        bundle.writestr(f'{prefix}/使用说明.txt', instructions.encode('utf-8-sig'))
    with zipfile.ZipFile(archive) as bundle:
        bad = bundle.testzip()
        if bad:
            raise ValueError(f'ZIP integrity check failed: {bad}')
        assert len(bundle.namelist()) == len(files) + 1
    digest = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
    (output / 'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    return dict(archive=str(archive), files=len(files) + 1, bytes=archive.stat().st_size,
                sha256=digest, privateDataIncluded=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--version', default='2.2')
    args = parser.parse_args()
    print(json.dumps(package(args.source, args.output, args.version), ensure_ascii=False, indent=2))
