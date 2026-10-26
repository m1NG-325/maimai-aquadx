"""Read public GitHub releases; never download or replace application files."""
import re
from urllib.parse import quote

import httpx

REPOSITORY_URL = 'https://github.com/m1NG-325/maimai-aquadx'
RELEASES_URL = REPOSITORY_URL + '/releases'
LATEST_API = 'https://api.github.com/repos/m1NG-325/maimai-aquadx/releases/latest'


class UpdateCheckError(ValueError):
    pass


def version_tuple(value):
    match = re.fullmatch(r'[vV]?(\d+)\.(\d+)(?:\.(\d+))?', str(value).strip())
    if not match:
        raise UpdateCheckError('无法识别版本号，请到仓库 Releases 页面查看。')
    return tuple(int(part or 0) for part in match.groups())


def check_latest(current_version, *, transport=None):
    current = version_tuple(current_version)
    try:
        with httpx.Client(timeout=12, transport=transport, headers={
            'Accept': 'application/vnd.github+json',
            'User-Agent': f'AquaSync/{current_version}',
        }) as client:
            response = client.get(LATEST_API)
        if response.status_code == 404:
            raise UpdateCheckError('仓库暂时没有可获取的正式版本，请到 Releases 页面查看。')
        if response.status_code in (403, 429):
            raise UpdateCheckError('GitHub 暂时限制了请求，请稍后再试，或直接打开 Releases 页面。')
        response.raise_for_status()
        release = response.json()
    except httpx.HTTPError as exc:
        raise UpdateCheckError('无法连接 GitHub，请检查网络或代理设置后重试。') from exc
    except ValueError as exc:
        if isinstance(exc, UpdateCheckError):
            raise
        raise UpdateCheckError('GitHub 返回的数据无法读取，请稍后重试。') from exc
    if not isinstance(release, dict) or release.get('draft') or release.get('prerelease'):
        raise UpdateCheckError('未获取到有效的正式版本，请到 Releases 页面查看。')
    tag = release.get('tag_name', '')
    latest = version_tuple(tag)
    return {
        'current': current_version, 'latest': tag,
        'state': 'newer' if latest > current else ('current' if latest == current else 'ahead'),
        'url': RELEASES_URL + '/tag/' + quote(tag, safe=''),
        'notes': str(release.get('body') or '该版本未提供更新日志。')[:30000],
    }
