"""Start a loopback-only server and open its browser page once ready."""
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def available_port():
    for port in range(8001, 8012):
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', port))
                return port
            except OSError:
                pass
    raise RuntimeError('8001-8011 ports are busy; close an old AquaSync window and retry')


def main():
    os.chdir(ROOT)
    port = available_port()
    url = f'http://127.0.0.1:{port}/'
    process = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT)
    try:
        for _ in range(100):
            if process.poll() is not None:
                raise RuntimeError('Server failed to start. Read the error above.')
            try:
                with urllib.request.urlopen(url+'health', timeout=.5) as response:
                    if response.status == 200:
                        print('AquaSync: '+url, flush=True)
                        webbrowser.open(url)
                        break
            except (OSError, TimeoutError):
                time.sleep(.1)
        else:
            raise RuntimeError('Server startup timed out.')
        print('Keep this window open. Press Ctrl+C to stop.', flush=True)
        return process.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == '__main__':
    raise SystemExit(main())
