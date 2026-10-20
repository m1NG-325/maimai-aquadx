"""Conservative desktop-only exclusions; retain graphics fallback and image codecs in use."""
from pathlib import PurePosixPath
import re

UNUSED_QT = {'qt6virtualkeyboard.dll', 'qt6quick.dll', 'qt6qml.dll', 'qt6qmlmeta.dll',
             'qt6qmlmodels.dll', 'qt6qmlworkerscript.dll', 'qt6opengl.dll', 'qt6pdf.dll'}
UNUSED_PLUGINS = {'qtvirtualkeyboardplugin.dll', 'qpdf.dll', 'qicns.dll', 'qtga.dll', 'qtiff.dll', 'qwbmp.dll'}


def reason(name):
    path = PurePosixPath(name.replace('\\', '/').lower())
    if path.name in UNUSED_QT: return 'unused virtual keyboard / QML or PDF runtime'
    if path.name in UNUSED_PLUGINS: return 'unused virtual keyboard or image format plugin'
    if re.fullmatch(r'icu(?:dt|uc|in)(?:\d+)?\.dll', path.name): return 'external ICU unused by this Windows Qt build'
    if 'translations' in path.parts and not path.name.endswith('_zh_cn.qm'):
        return 'unused Qt translation language'
    return None


def prune(entries):
    return [entry for entry in entries if reason(entry[0]) is None]
