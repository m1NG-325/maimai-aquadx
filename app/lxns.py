"""Lxns personal API integration. Tokens exist only in expiring process memory."""
import hashlib
import json
import secrets
import sqlite3
import threading
import time
from pathlib import Path

import httpx
from fastapi import HTTPException
from decimal import InvalidOperation
from app.score_diff import BackupStore, normalize_scores, differences, verify_scores, digest, score_key
from app.b50_views import source_b50, target_b50, compare_groups, compare_b50

BASE = 'https://maimai.lxns.net/api/v0'
COOKIE = 'aquasync_lxns'
SESSION_SECONDS = 1800


def catalog_index(data):
    if not isinstance(data, dict) or not isinstance(data.get('songs'), list) or not data['songs']:
        raise ValueError('落雪曲库结构不正确')
    index = {}
    for song in data['songs']:
        mid = song['id']
        if not isinstance(mid, int) or mid <= 0 or not isinstance(song['title'], str):
            raise ValueError('落雪曲库曲目字段不正确')
        for kind in ('standard', 'dx'):
            for chart in song['difficulties'].get(kind, []):
                difficulty = chart['difficulty']
                if not isinstance(difficulty, int) or difficulty not in range(5):
                    raise ValueError('落雪曲库难度字段不正确')
                key = (mid, kind, difficulty)
                if key in index:
                    raise ValueError('落雪曲库包含重复谱面')
                index[key] = {'title': song['title'], 'level': chart['level'],
                              'ds': chart.get('level_value'), 'version': chart.get('version', song.get('version')),
                              'disabled': bool(song.get('disabled', False))}
    if not index:
        raise ValueError('落雪曲库没有普通谱面')
    return index


class LxnsService:
    def __init__(self, catalog_path, client_factory=None, backup_path=None):
        self.catalog_path = Path(catalog_path)
        self.client_factory = client_factory or (lambda: httpx.Client(timeout=httpx.Timeout(30, connect=10), follow_redirects=False))
        self.sessions = {}
        self.guard = threading.Lock()
        self.catalog_guard = threading.Lock()
        self.backups = BackupStore(backup_path or self.catalog_path.parent / 'lxns_backups.sqlite3')

    def catalog(self):
        try:
            with self.catalog_guard:
                return catalog_index(json.loads(self.catalog_path.read_text(encoding='utf-8')))
        except (ValueError, KeyError, TypeError, OSError):
            raise HTTPException(503, '落雪曲库未就绪，请先点击“更新落雪曲库”') from None

    def request(self, method, path, token=None, body=None):
        headers = {'X-User-Token': token} if token else {}
        try:
            with self.client_factory() as client:
                response = client.request(method, BASE + path, headers=headers, json=body)
        except httpx.HTTPError:
            raise HTTPException(502, '无法连接落雪；若提交时发生网络错误，结果可能不确定，请先到落雪检查成绩后再重试') from None
        errors = {400: '落雪拒绝了请求，请检查成绩或账号状态', 401: '落雪个人 API 密钥无效或已过期',
                  403: '落雪账号权限不足', 404: '落雪中没有对应的舞萌玩家，请先在落雪绑定玩家',
                  429: '落雪请求过于频繁，请稍后重试'}
        if response.status_code not in range(200, 300):
            raise HTTPException(response.status_code if response.status_code in errors else 502,
                                errors.get(response.status_code, '落雪服务异常，请稍后检查账号数据'))
        try:
            data = response.json()
        except ValueError:
            raise HTTPException(502, '落雪响应不是有效 JSON，请检查账号数据后再重试') from None
        if not isinstance(data, dict):
            raise HTTPException(502, '落雪响应结构不正确')
        if data.get('success') is False:
            code = data.get('code')
            raise HTTPException(code if code in errors else 502, errors.get(code, '落雪未确认请求成功，请检查账号数据'))
        return data

    def refresh_catalog(self):
        data = self.request('GET', '/maimai/song/list')
        try:
            index = catalog_index(data)
        except (ValueError, TypeError, KeyError):
            raise HTTPException(502, '下载的落雪曲库结构不正确，已保留原曲库') from None
        with self.catalog_guard:
            self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.catalog_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            tmp.replace(self.catalog_path)
        return {'songs': len(data['songs']), 'charts': len(index)}

    def _prune(self):
        now = time.monotonic()
        for sid in list(self.sessions):
            if self.sessions[sid]['expires'] <= now:
                self.sessions.pop(sid, None)

    def session(self, sid, required=False):
        with self.guard:
            self._prune()
            value = self.sessions.get(sid)
        if required and value is None:
            raise HTTPException(401, '请先连接落雪账号；连接在 30 分钟后或服务重启后失效')
        return value

    def connect(self, token, previous_sid=None):
        token = token.strip()
        if not 8 <= len(token) <= 1024 or any(ord(c) < 33 or ord(c) > 126 for c in token):
            raise HTTPException(422, '请输入有效的落雪个人 API 密钥')
        response = self.request('GET', '/user/maimai/player', token)
        data = response.get('data')
        if response.get('success') is not True or not isinstance(data, dict) or not data.get('friend_code'):
            raise HTTPException(502, '落雪没有返回有效的玩家信息')
        account = {'name': data.get('name', ''), 'friend_code': str(data['friend_code']), 'rating': data.get('rating')}
        sid = secrets.token_urlsafe(32)
        with self.guard:
            self._prune()
            if len(self.sessions) >= 16:
                raise HTTPException(429, '连接数量已达上限，请断开旧连接或稍后重试')
            self.sessions.pop(previous_sid, None)
            self.sessions[sid] = {'token': token, 'account': account, 'expires': time.monotonic() + SESSION_SECONDS,
                                  'lock': threading.Lock(), 'submitted': set(), 'plans': {}}
        return sid, account

    def disconnect(self, sid):
        with self.guard:
            self.sessions.pop(sid, None)

    def preview(self, payload, sid=None):
        index = self.catalog()
        session = self.session(sid)
        account = session['account'] if session else None
        scores, display, rejected = [], [], []
        for r in payload['best']:
            mid, level = r['musicId'], r['level']
            kind = 'dx' if mid >= 10000 else 'standard'
            chart = index.get((mid % 10000, kind, level)) if mid < 100000 and level < 5 else None
            if chart is None:
                rejected.append({'musicId': mid, 'level': level, 'difficulty': r['difficulty'],
                                 'reason': '落雪曲库没有该普通谱面' if mid < 100000 and level < 5 else '暂不支持宴会场或特殊谱面'})
                continue
            score = {'id': mid % 10000, 'type': kind, 'level_index': level, 'achievements': r['achievements'],
                     'dx_score': r['dxScore'], 'fc': r['fc'] or None, 'fs': r['fs'] or None}
            scores.append(score)
            display.append(dict(score, musicId=mid, title=chart['title'], difficulty=r['difficulty']))
        body = {'scores': scores}
        fingerprint = hashlib.sha256(json.dumps({'body': body, 'rejected': rejected,
            'account': account, 'player': payload['player']}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        return {'account': account, 'player': payload['player'], 'total': len(payload['best']),
                'exportable': len(scores), 'rejected': rejected, 'scores': display, 'fingerprint': fingerprint,
                'catalogCharts': len(index)}, body

    def b50_views(self, payload, charts, remote=None):
        with self.catalog_guard:
            data = json.loads(self.catalog_path.read_text(encoding='utf-8'))
        index = catalog_index(data)
        versions = [v['version'] for v in data.get('versions', []) if isinstance(v.get('version'), int)]
        versions += [c['version'] // 1000 * 1000 for c in index.values() if isinstance(c.get('version'), int)] if not versions else []
        current = max(versions) if versions else 0
        _, body = self.preview(payload)
        source = source_b50(payload, charts)
        target = target_b50(body['scores'] if remote is None else remote, index, current, remote is not None)
        target['versionTitle'] = next((v.get('title') for v in data.get('versions', []) if v.get('version') == current), str(current))
        target['basis'] = '落雪已有成绩；按当前落雪曲库估算分组' if remote is not None else '本次导入成绩；按落雪曲库估算，未包含账号其他成绩'
        return {'source': source, 'target': target, 'differences': compare_groups(source, target),
                'comparison': compare_b50(source, target)}

    def read_scores(self, session):
        response = self.request('GET', '/user/maimai/player/scores', session['token'])
        try:
            scores = normalize_scores(response)
        except (ValueError, KeyError, TypeError, InvalidOperation):
            raise HTTPException(502, '落雪成绩列表结构异常，无法可靠备份或比较；未提交成绩') from None
        return response, scores

    def verify_account(self, session):
        response = self.request('GET', '/user/maimai/player', session['token'])
        player = response.get('data')
        if response.get('success') is not True or not isinstance(player, dict) or str(player.get('friend_code')) != session['account']['friend_code']:
            raise HTTPException(409, '落雪目标账号发生变化，请重新连接后核对')

    def save_backup(self, user_id, account, response, phase):
        try:
            return self.backups.save(user_id, account, response, phase)
        except (OSError, sqlite3.Error):
            raise HTTPException(503, '本地备份保存失败，未提交成绩；请检查磁盘空间或数据库权限') from None

    def prepare(self, payload, sid, user_id):
        session = self.session(sid, required=True)
        if not session['lock'].acquire(blocking=False):
            raise HTTPException(409, '该账号有操作进行中，请稍后再试')
        try:
            self.verify_account(session)
            response, remote = self.read_scores(session)
            preview, body = self.preview(payload, sid)
            backup = self.save_backup(user_id, session['account'], response, 'preview')
            rows = differences(body['scores'], remote)
            display = {score_key(s): s for s in preview['scores']}
            for row in rows:
                row.update(title=display[row['key']]['title'], difficulty=display[row['key']]['difficulty'],
                           musicId=display[row['key']]['musicId'])
            plan_id = secrets.token_urlsafe(24)
            now = time.monotonic()
            session['plans'] = {k: v for k, v in session['plans'].items() if v['expires'] > now}
            if len(session['plans']) >= 8:
                session['plans'].pop(next(iter(session['plans'])))
            session['plans'][plan_id] = {'expires': now + 600, 'user_id': user_id, 'fingerprint': preview['fingerprint'],
                                        'remote_hash': digest(remote), 'rows': rows, 'used': False, 'backup': backup}
            return dict(preview, plan_id=plan_id, rows=rows, backup=backup, remoteCount=len(remote),
                        counts={kind: sum(r['category'] == kind for r in rows) for kind in ('new', 'higher', 'lower', 'mixed', 'same')})
        finally:
            session['lock'].release()

    def upload(self, payload, sid, fingerprint, allow_partial, confirmed, plan_id=None,
               selected_keys=None, allow_lower=False, user_id='demo'):
        session = self.session(sid, required=True)
        if not confirmed:
            raise HTTPException(422, '请先确认目标账号和上传成绩数量')
        plan = session['plans'].get(plan_id)
        if not plan or plan['expires'] <= time.monotonic() or plan['user_id'] != user_id:
            raise HTTPException(409, '请先读取落雪成绩并备份、预览差异；预览有效期为 10 分钟')
        preview, body = self.preview(payload, sid)
        if fingerprint != preview['fingerprint'] or fingerprint != plan['fingerprint']:
            raise HTTPException(409, '成绩、曲库或目标账号已变化，请重新预览后确认')
        if preview['rejected'] and not allow_partial:
            raise HTTPException(409, '有落雪未收录的谱面，请明确允许只上传已匹配成绩')
        selected_keys = selected_keys or []
        lookup = {r['key']: r for r in plan['rows']}
        if not selected_keys or len(set(selected_keys)) != len(selected_keys) or any(k not in lookup for k in selected_keys):
            raise HTTPException(422, '请选择有效且不重复的差异成绩')
        selected = [lookup[k] for k in selected_keys]
        if any(r['category'] == 'same' for r in selected):
            raise HTTPException(422, '完全相同的成绩无需重复上传')
        if any(r['hasLower'] for r in selected) and not allow_lower:
            raise HTTPException(409, '所选成绩包含降低字段，请明确确认允许提交降低的达成率、DX 分或标记')
        body = {'scores': [r['after'] for r in selected]}
        if not session['lock'].acquire(blocking=False):
            raise HTTPException(409, '正在提交，请勿重复点击')
        try:
            if plan['used']:
                raise HTTPException(409, '此差异预览已经提交过，请重新读取和备份后再操作')
            self.verify_account(session)
            response, remote = self.read_scores(session)
            if digest(remote) != plan['remote_hash']:
                raise HTTPException(409, '落雪已有成绩已变化，未提交；请重新读取备份并预览差异')
            backup = self.save_backup(user_id, session['account'], response, 'pre-upload')
            plan['used'] = True
            result = self.request('POST', '/user/maimai/player/scores', session['token'], body)
            if result.get('success') is not True:
                raise HTTPException(502, '落雪未明确确认成功，请到落雪检查成绩后再决定是否重试')
            try:
                after_response, observed = self.read_scores(session)
                verification = verify_scores(body['scores'], observed)
                verification['snapshot'] = self.backups.save(user_id, session['account'], after_response, 'post-upload')
            except (HTTPException, OSError, sqlite3.Error):
                verification = {'available': False, 'message': '请求已被落雪确认，但回读核对未完成；请到落雪检查，勿直接重复提交'}
            return {'success': True, 'submitted': len(body['scores']), 'skipped': len(preview['rejected']),
                    'notSelected': len(preview['scores']) - len(body['scores']), 'backup': backup,
                    'verification': verification, 'account': session['account'],
                    'message': '落雪已确认请求，回读核对结果见下方' if verification['available'] else verification['message']}
        finally:
            session['lock'].release()
