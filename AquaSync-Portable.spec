# Windows directory build; compact assets retain exact pixels and offline coverage.
from pathlib import Path
import os
import runpy
root = Path(SPECPATH)
datas = [(str(root / 'data' / name), 'data') for name in
         ['music_data.json', 'private_music_data.json', 'plate_catalogs.json', 'lxns_song_list.json', 'karen_courses.json', 'collection_metadata.json', 'map_details.json', 'activity_details.json']]
datas.append((str(root/'docs/KarenBot-LICENSE.txt'), 'licenses'))
datas.append((str(root/'docs/KarenBot-Resources-LICENSE.txt'), 'licenses'))
datas.append((str(root/'docs/MaiKit-Assets-LICENSE.txt'), 'licenses'))
if os.environ.get('AQUASYNC_RELEASE_ASSETS'):
    asset_root=Path(os.environ['AQUASYNC_RELEASE_ASSETS'])
else:
    asset_root=root/'.runtime/compact-assets'
    runpy.run_path(str(root/'tools/compact_assets.py'))['ensure_compact'](root/'data/report_assets',asset_root)
datas.append((str(asset_root), 'data/report_assets'))
a = Analysis([str(root/'desktop_studio.py')], pathex=[str(root)], binaries=[], datas=datas,
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
                       'PySide6.QtWebEngineQuick', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
                       'PySide6.QtQuick','PySide6.QtQml','PySide6.QtOpenGL',
                       'PySide6.QtQuickWidgets','PySide6.QtQmlModels',
                       'PIL','pytest', 'tkinter', 'uvicorn'], noarchive=False)
# Qt on Windows uses the OS ICU API. A Poppler directory on the build host's
# PATH has unrelated unversioned ICU DLLs; never ship those in place of Windows.
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.lower() not in {'icuuc.dll', 'icuin.dll', 'icudt.dll'}]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='AquaSync', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False,
          icon=str(root/'data/report_assets/aquasync.ico'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='AquaSync')
