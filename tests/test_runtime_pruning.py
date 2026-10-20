import runpy
from pathlib import Path


def test_pruning_keeps_required_codecs_windows_and_graphics_fallback():
    rules=runpy.run_path(str(Path(__file__).resolve().parents[1]/'tools/runtime_pruning.py'))
    reason=rules['reason']
    for name in ['PySide6/plugins/platforms/qwindows.dll','PySide6/plugins/platforms/qoffscreen.dll',
                 'PySide6/plugins/imageformats/qwebp.dll','PySide6/plugins/imageformats/qsvg.dll',
                 'PySide6/plugins/imageformats/qjpeg.dll','PySide6/plugins/imageformats/qico.dll',
                 'PySide6/opengl32sw.dll','PySide6/Qt6Gui.dll','PySide6/Qt6Widgets.dll',
                 'PySide6/Qt6Network.dll','sqlite3.dll','libcrypto-3-x64.dll',
                 'PySide6/translations/qtbase_zh_CN.qm','data/report_assets/covers/1.webp']:
        assert reason(name) is None, name
    for name in ['icudt78.dll','icuin.dll','PySide6/Qt6Quick.dll','PySide6/Qt6Pdf.dll',
                 'PySide6/plugins/imageformats/qpdf.dll','PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll',
                 'PySide6/translations/qtbase_de.qm']:
        assert reason(name),name
