# Reproducible Windows one-file native desktop build; no private snapshots included.
from pathlib import Path
root = Path(SPECPATH)
datas = [(str(root / 'data' / name), 'data') for name in
         ['music_data.json', 'private_music_data.json', 'lxns_song_list.json', 'karen_courses.json']]
datas.append((str(root/'docs/KarenBot-LICENSE.txt'), 'licenses'))
datas.append((str(root/'docs/KarenBot-Resources-LICENSE.txt'), 'licenses'))
datas.append((str(root/'data/report_assets'), 'data/report_assets'))
a = Analysis([str(root/'desktop.py')], pathex=[str(root)], binaries=[], datas=datas,
             hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
             excludes=['PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
                       'PySide6.QtWebEngineQuick', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
                       'pytest', 'tkinter', 'uvicorn'], noarchive=False)
# Qt on Windows uses the OS ICU API. A Poppler directory on the build host's
# PATH has unrelated unversioned ICU DLLs; never ship those in place of Windows.
a.binaries = [entry for entry in a.binaries
              if Path(entry[0]).name.lower() not in {'icuuc.dll', 'icuin.dll', 'icudt.dll'}]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='AquaSync', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False)
