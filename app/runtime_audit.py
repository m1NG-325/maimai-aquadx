"""Explicit packaged smoke checks; never run in ordinary desktop sessions."""
import json
import ssl
import sys
from pathlib import Path


def check(core, window, output):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage, QImageReader, QImageWriter, QPixmap
    from PySide6.QtWidgets import QApplication
    import httpx
    output.mkdir(parents=True, exist_ok=True)
    pages=[]
    for page in range(window.pages.count()):
        window.show_page(page); QApplication.processEvents()
        assert not window.grab().isNull()
        pages.append(page)
    formats={bytes(x).decode() for x in QImageReader.supportedImageFormats()}
    assert {'png','webp','svg','jpeg','ico'}.issubset(formats), formats
    image=QImage(24,24,QImage.Format.Format_ARGB32); image.fill(Qt.GlobalColor.green)
    roundtrips=[]
    for fmt in ['png','webp','jpeg']:
        target=output/('codec.'+fmt)
        assert image.save(str(target),fmt)
        decoded=QImage(str(target)); assert decoded.size()==image.size()
        if fmt=='png': assert decoded.pixelColor(0,0)==image.pixelColor(0,0)
        roundtrips.append(fmt)
    icon=core.directory.parent  # actual SVG is read from the bundled asset root below
    from app.desktop_core import ASSETS
    svg=next((ASSETS/'data/report_assets/studio').glob('*.svg'))
    assert not QPixmap(str(svg)).isNull()
    assert not QImage(str(ASSETS/'data/report_assets/aquasync.ico')).isNull()
    ssl.create_default_context()
    from app.desktop_dialogs import NoticeDialog, UpdateDialog
    from app.updates import check_latest, RELEASES_URL
    release=check_latest('2.1',transport=httpx.MockTransport(lambda request:httpx.Response(
        200,json={'tag_name':'v2.2','body':'Runtime update check'})))
    assert release['state']=='newer' and release['url']==RELEASES_URL+'/tag/v2.2'
    for dialog in (NoticeDialog(window),UpdateDialog(release,window)):
        dialog.show();QApplication.processEvents()
        assert not dialog.grab().isNull()
        dialog.accept()
    def handler(request):
        assert request.headers['X-User-Token']=='audit-token'
        return httpx.Response(200,json={'success':True,'data':{'name':'audit','friend_code':123}})
    core.lxns.client_factory=lambda:httpx.Client(transport=httpx.MockTransport(handler))
    sid,account=core.lxns.connect('audit-token')
    assert account['name']=='audit'; core.lxns.disconnect(sid)
    assert not any(name in sys.modules for name in ['fastapi','pydantic','pydantic_core'])
    loaded=[]
    if sys.platform=='win32':
        import ctypes
        from ctypes import wintypes
        dll=ctypes.WinDLL('psapi');kernel=ctypes.WinDLL('kernel32')
        kernel.GetCurrentProcess.restype=wintypes.HANDLE
        dll.EnumProcessModules.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.HMODULE),wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
        dll.GetModuleFileNameExW.argtypes=[wintypes.HANDLE,wintypes.HMODULE,wintypes.LPWSTR,wintypes.DWORD]
        modules=(wintypes.HMODULE*2048)();needed=wintypes.DWORD();process=kernel.GetCurrentProcess()
        assert dll.EnumProcessModules(process,modules,ctypes.sizeof(modules),ctypes.byref(needed))
        for module in modules[:needed.value//ctypes.sizeof(wintypes.HMODULE)]:
            buf=ctypes.create_unicode_buffer(32768)
            if dll.GetModuleFileNameExW(process,module,buf,len(buf)):loaded.append(buf.value)
    return dict(pagesChecked=pages,imageReaders=sorted(formats),codecRoundtrips=roundtrips,
                svg=True,ico=True,tlsContext=True,mockLxns=True,updateDialogs=True,mockUpdateCheck=True,
                webFrameworkAbsent=True,loadedModules=loaded)
