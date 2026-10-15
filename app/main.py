import json
import os
from pathlib import Path
from fastapi import Body, FastAPI, HTTPException, Request, Response, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, SecretStr, Field
from app.database import Database
from app.parser import parse_aquadx
from app.calculations import summarize
from app.exporters import export_scores, ExportError
from app.lxns import LxnsService, COOKIE, SESSION_SECONDS
from app.private_catalog import display_catalog, private_view
from app.local_tools import library_rows, filter_library, recommendations
from app.calculations import rating

ROOT = Path(__file__).resolve().parent.parent


class ConnectRequest(BaseModel):
    token: SecretStr


class UploadRequest(BaseModel):
    fingerprint: str = Field(max_length=64)
    allow_partial: bool = False
    confirmed: bool = False
    plan_id: str | None = Field(default=None, max_length=100)
    selected_keys: list[str] = Field(default_factory=list, max_length=5000)
    allow_lower: bool = False


def create_app(db_path=None, catalog_path=None, lxns_catalog_path=None, lxns_client_factory=None):
    db = Database(db_path or os.getenv('AQUASYNC_DB', str(ROOT / 'data/aquasync.sqlite3')))
    if not db.charts():
        catalog = Path(catalog_path or ROOT / 'data/music_data.json')
        if catalog.exists():
            db.import_catalog(json.loads(catalog.read_text(encoding='utf-8-sig')), str(catalog))
    api = FastAPI(title='AquaSync', version='0.7.0', description='Local AquaDX score conversion and Lxns synchronization')
    private_path = ROOT / 'data/private_music_data.json'
    if private_path.exists():
        db.save_private_catalog(json.loads(private_path.read_text(encoding='utf-8')))
    api.state.db = db
    lxns = LxnsService(lxns_catalog_path or ROOT / 'data/lxns_song_list.json', lxns_client_factory, db.path)
    api.state.lxns = lxns
    api.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]', 'testserver'])

    @api.middleware('http')
    async def local_action_guard(request: Request, call_next):
        if request.url.path.startswith('/api/') and request.method == 'POST':
            origin = request.headers.get('origin')
            if request.headers.get('x-aquasync-action') != '1' or (origin and origin != str(request.base_url).rstrip('/')):
                return JSONResponse({'detail': '请从本机 AquaSync 页面执行该操作'}, status_code=403)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" if request.url.path in ('/', '/ui', '/sync') or request.url.path.startswith('/static/') else "frame-ancestors 'none'"
        return response

    api.mount('/static', StaticFiles(directory=ROOT / 'app/static'), name='static')

    @api.get('/', include_in_schema=False)
    @api.get('/sync', include_in_schema=False)
    @api.get('/ui', include_in_schema=False)
    def home():
        return FileResponse(ROOT / 'app/static/index.html')

    @api.get('/tools', include_in_schema=False)
    def local_home():
        return FileResponse(ROOT / 'app/static/local.html')

    @api.get('/api/local/users')
    def local_users():
        return {'users': db.users()}

    @api.get('/api/user/{user_id}/local')
    def local_overview(user_id: str):
        data = dashboard(user_id)
        data['plates'] = report(user_id, None)['plates']
        data['recommendations'] = recommendations(data['best'])
        return data

    @api.get('/api/user/{user_id}/library')
    def local_library(user_id: str, q: str = Query(default='', max_length=100), kind: str = '',
                      difficulty: int | None = Query(default=None, ge=0, le=4),
                      minimum: float = Query(default=0, ge=0, le=20), maximum: float = Query(default=20, ge=0, le=20),
                      status: str = 'all', offset: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=200)):
        if kind not in ('', 'SD', 'DX') or status not in ('all', 'played', 'unplayed', 'fc', 'ap') or minimum > maximum:
            raise HTTPException(422, 'invalid library filter')
        rows = filter_library(library_rows(db.charts(), db.private_charts(), player_payload(user_id)['best']),
                              q, kind, difficulty, minimum, maximum, status)
        return {'total': len(rows), 'rows': rows[offset:offset+limit], 'offset': offset,
                'scope': 'public and JP reference metadata; not a verified private-server installed catalog'}

    @api.get('/api/local/rating')
    def local_rating(ds: float = Query(ge=.1, le=20), achievements: float = Query(ge=0, le=101)):
        value, rank = rating(ds, achievements)
        return {'rating': value, 'rank': rank}

    def player_payload(user_id):
        value = db.player(user_id)
        if value is None:
            raise HTTPException(404, 'user not found; import an AquaDX export first')
        return value

    def report(user_id, current_version):
        payload = player_payload(user_id)
        try:
            result = summarize(payload, db.charts(), current_version)
            result['calculation']['catalogSource'] = db.catalog_source()
            return result
        except ValueError as e:
            raise HTTPException(422, str(e)) from e

    @api.get('/health')
    def health():
        return {'status': 'ok', 'catalogCharts': len(db.charts())}

    @api.get('/api/user/{user_id}/dashboard')
    def dashboard(user_id: str):
        data = report(user_id, None)
        data.pop('records')
        for group in data['plates'].values():
            for progress in group.values():
                progress.pop('missing')
        try:
            data['b50Views'] = lxns.b50_views(player_payload(user_id), display_catalog(db.charts(), db.private_charts()))
        except (OSError, ValueError, KeyError, HTTPException):
            from app.b50_views import source_b50
            data['b50Views'] = {'source': source_b50(player_payload(user_id), db.charts()),
                                'target': {'available': False, 'old': [], 'new': [], 'basis': '落雪曲库不可用'}, 'differences': []}
        try:
            target_catalog = lxns.catalog()
        except HTTPException:
            target_catalog = {}
        data['privateCatalog'] = private_view(player_payload(user_id)['best'], db.charts(), db.private_charts(), target_catalog)
        return data

    @api.get('/api/user/{user_id}/lxns/preview')
    def preview_lxns(user_id: str, request: Request):
        preview, _ = lxns.preview(player_payload(user_id), request.cookies.get(COOKIE))
        return preview

    @api.get('/api/user/{user_id}/private/download')
    def download_private(user_id: str):
        view = private_view(player_payload(user_id)['best'], db.charts(), db.private_charts(), lxns.catalog())
        return JSONResponse(view, headers={'Content-Disposition': 'attachment; filename="aquasync-private-all.json"'})

    @api.post('/api/user/{user_id}/lxns/prepare')
    def prepare_lxns(user_id: str, request: Request):
        plan = lxns.prepare(player_payload(user_id), request.cookies.get(COOKIE), user_id)
        # Reuse the validated remote snapshot to show the account's B50 estimate.
        snapshot = lxns.backups.get(user_id, plan['backup']['id'])
        from app.score_diff import normalize_scores
        views = lxns.b50_views(player_payload(user_id), display_catalog(db.charts(), db.private_charts()), normalize_scores(snapshot['response']))
        plan['remoteB50'] = views['target']
        plan['remoteComparison'] = views['comparison']
        return plan

    @api.get('/api/user/{user_id}/lxns/backups')
    def list_lxns_backups(user_id: str):
        player_payload(user_id)
        return {'backups': lxns.backups.list(user_id)}

    @api.get('/api/user/{user_id}/lxns/backups/{backup_id}')
    def download_lxns_backup(user_id: str, backup_id: str):
        snapshot = lxns.backups.get(user_id, backup_id)
        if snapshot is None:
            raise HTTPException(404, 'backup not found')
        return JSONResponse(snapshot, headers={'Content-Disposition': 'attachment; filename="lxns-backup.json"'})

    @api.post('/api/lxns/connect')
    def connect_lxns(body: ConnectRequest, request: Request, response: Response):
        sid, account = lxns.connect(body.token.get_secret_value(), request.cookies.get(COOKIE))
        response.set_cookie(COOKIE, sid, httponly=True, samesite='strict', max_age=SESSION_SECONDS, path='/api/')
        return {'connected': True, 'account': account}

    @api.get('/api/lxns/session')
    def lxns_session(request: Request):
        session = lxns.session(request.cookies.get(COOKIE))
        return {'connected': session is not None, 'account': session['account'] if session else None}

    @api.post('/api/lxns/disconnect')
    def disconnect_lxns(request: Request, response: Response):
        lxns.disconnect(request.cookies.get(COOKIE))
        response.delete_cookie(COOKIE, path='/api/')
        return {'connected': False}

    @api.post('/api/lxns/catalog/refresh')
    def refresh_lxns_catalog():
        return lxns.refresh_catalog()

    @api.get('/api/user/{user_id}/lxns/download')
    def download_lxns(user_id: str):
        preview, body = lxns.preview(player_payload(user_id))
        return JSONResponse(body, headers={'Content-Disposition': 'attachment; filename="aquasync-lxns.json"',
                                          'X-AquaSync-Rejected-Count': str(len(preview['rejected']))})

    @api.post('/api/user/{user_id}/lxns/upload')
    def upload_lxns(user_id: str, body: UploadRequest, request: Request):
        return lxns.upload(player_payload(user_id), request.cookies.get(COOKIE), body.fingerprint, body.allow_partial,
                           body.confirmed, body.plan_id, body.selected_keys, body.allow_lower, user_id)

    @api.post('/user/{user_id}/import')
    def import_user(user_id: str, data: dict = Body(...)):
        try:
            payload = parse_aquadx(data)
        except (ValueError, TypeError, KeyError) as e:
            raise HTTPException(422, str(e)) from e
        db.save_player(user_id, payload)
        return {'id': user_id, 'records': len(payload['records']), 'bestCharts': len(payload['best'])}

    @api.get('/user/{user_id}')
    def get_user(user_id: str, current_version: str | None = None):
        return report(user_id, current_version)

    @api.get('/user/{user_id}/export/{target}')
    def export_user(user_id: str, target: str, allow_partial: bool = False, current_version: str | None = None):
        try:
            payload, rejected = export_scores(report(user_id, current_version), target, allow_partial)
        except ExportError as e:
            raise HTTPException(409, {'message': str(e), 'rejected': e.rejected}) from e
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        return JSONResponse(payload, headers={'X-AquaSync-Rejected-Count': str(len(rejected))})

    @api.get('/user/{user_id}/export-check/{target}')
    def export_check(user_id: str, target: str):
        try:
            payload, rejected = export_scores(report(user_id, None), target, True)
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        return {'target': target, 'exportable': len(payload if isinstance(payload, list) else payload['scores']), 'rejected': rejected}

    return api


app = create_app()
