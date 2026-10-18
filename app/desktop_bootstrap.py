"""Shared desktop startup diagnostics, including failures before Qt is imported."""
import faulthandler
import json
import os
from pathlib import Path
import sys
import traceback
from datetime import datetime

_log = None


def milestone(message):
    if _log:
        _log.write(f'{datetime.now().isoformat(timespec="seconds")} {message}\n')


def run(studio=False):
    global _log
    log = None
    try:
        from app.desktop_storage import installation_directory
        directory = installation_directory() / 'logs'
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / 'startup.log'
        if path.exists() and path.stat().st_size > 2 * 1024 * 1024:
            os.replace(path, directory / 'startup.previous.log')
        log = path.open('a', encoding='utf8', buffering=1)
        _log = log
        log.write(f'\n{datetime.now().isoformat(timespec="seconds")} Starting AquaSync; studio={studio}\n')
        faulthandler.enable(file=log)
    except OSError:
        pass  # An unavailable diagnostics directory must not prevent startup.
    try:
        if '--self-test' in sys.argv:
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        if studio:
            from app.studio_theme import install
            install()
        from desktop import main
        code = main()
        if log:
            log.write(f'Exited normally: {code}\n')
        return code
    except Exception:
        error = traceback.format_exc()
        if log:
            log.write(error)
        if '--self-test' in sys.argv and '--result' in sys.argv:
            result = Path(sys.argv[sys.argv.index('--result') + 1])
            result.parent.mkdir(parents=True, exist_ok=True)
            result.write_text(json.dumps({'ok': False, 'error': error}, ensure_ascii=False), encoding='utf8')
        elif sys.platform == 'win32':
            import ctypes
            message = 'AquaSync 启动失败，个人数据不会被自动清除。\n'
            message += f'请查看启动日志：\n{path}' if log else '无法写入启动日志，请检查磁盘和目录权限。'
            ctypes.windll.user32.MessageBoxW(None, message, 'AquaSync 启动失败', 0x10)
        return 1
    finally:
        if log:
            faulthandler.disable()
            log.close()
        _log = None
