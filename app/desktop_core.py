"""Desktop data service. All ordinary queries run without a web server."""
import json
import os
import shutil
import sys
from pathlib import Path
from app.database import Database
from app.parser import parse_aquadx
from app.calculations import summarize, plate_progress
from app.private_catalog import private_view, display_catalog
from app.local_tools import library_rows, filter_library, recommendations
from app.lxns import LxnsService
from app.desktop_storage import default_settings_path,configured_directory,copy_profile,save_directory

ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))


class DesktopCore:
    def __init__(self, directory=None,settings_path=None):
        self.settings_path=Path(settings_path) if settings_path is not None else default_settings_path()
        selected=directory if directory is not None else configured_directory(self.settings_path)
        self.directory = Path(selected or (Path(os.getenv('LOCALAPPDATA', Path.home())) / 'AquaSync')).expanduser().resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.db = Database(self.directory/'aquasync.sqlite3')
        if not self.db.charts():
            self.db.import_catalog(json.loads((ASSETS/'data/music_data.json').read_text(encoding='utf8')), 'bundled public catalog')
        self.db.save_private_catalog(json.loads((ASSETS/'data/private_music_data.json').read_text(encoding='utf8')))
        target = self.directory/'lxns_song_list.json'
        if not target.exists():
            shutil.copyfile(ASSETS/'data/lxns_song_list.json', target)
        self.lxns = LxnsService(target, backup_path=self.db.path)
        self.courses = json.loads((ASSETS/'data/karen_courses.json').read_text(encoding='utf8'))

    def migrate_directory(self,directory):
        target=Path(directory).expanduser().resolve()
        if target==self.directory:return self
        copy_profile(self.directory,target)
        migrated=DesktopCore(target,settings_path=self.settings_path)
        with migrated.db.connect() as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('新目录数据库校验失败')
        if migrated.db.users()!=self.db.users():raise ValueError('玩家数据校验失败，仍使用原目录。')
        for user in self.db.users():
            if migrated.db.player(user['id'])!=self.db.player(user['id']):raise ValueError('成绩内容校验失败，仍使用原目录。')
        save_directory(self.settings_path,target)
        return migrated

    def import_file(self, path, user_id):
        raw = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        payload = parse_aquadx(raw)
        self.db.save_player(user_id, payload)
        return payload

    def overview(self, user_id):
        payload = self.db.player(user_id)
        if payload is None:
            raise ValueError('请先导入 AquaDX JSON')
        charts = self.db.charts()
        report = summarize(payload, charts)
        # Plate coverage uses the complete reference catalog, independently of B50.
        report['analysisPlates'] = report['plates']
        report['plateCatalog'] = display_catalog(charts, self.db.private_charts())
        report['plateScopeLabel'] = '完整私服参考曲库'
        report['plates'] = plate_progress(payload['best'], report['plateCatalog'])
        report['calculation']['plateScope'] = 'merged JP reference catalog; not proof of server-awarded plates'
        report['privateCatalog'] = private_view(payload['best'], charts, self.db.private_charts(), self.lxns.catalog())
        report['b50Views'] = self.lxns.b50_views(payload, display_catalog(charts, self.db.private_charts()))
        report['recommendations'] = recommendations(report['best'])
        return report

    def library(self, user_id, **filters):
        payload = self.db.player(user_id) or {'best': []}
        return filter_library(library_rows(self.db.charts(), self.db.private_charts(), payload['best']), **filters)
