"""Public jackets only; no scores, accounts or tokens are sent."""
from app.image_assets import image_path
from pathlib import Path
import time
import httpx


def fetch_covers(ids, directory, bundled, client_factory=None):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    saved=skipped=failed=0
    factory=client_factory or (lambda:httpx.Client(timeout=15,follow_redirects=False))
    with factory() as client:
        for mid in sorted(set(ids)):
            if not isinstance(mid,int) or not 0<mid<100000:failed+=1;continue
            resource=mid%10000
            target=directory/f'{resource}.png'
            if target.exists() or image_path(Path(bundled)/f'{resource}.png').exists():skipped+=1;continue
            try:
                response=client.get(f'https://assets2.lxns.net/maimai/jacket/{resource}.png')
                if response.status_code!=200 or not response.content.startswith(b'\x89PNG\r\n\x1a\n') or len(response.content)>2_000_000:
                    failed+=1;continue
                temporary=target.with_suffix('.tmp');temporary.write_bytes(response.content);temporary.replace(target);saved+=1
            except (httpx.HTTPError,OSError):failed+=1
            finally:
                if client_factory is None:time.sleep(.5)
    return dict(saved=saved,skipped=skipped,failed=failed)
