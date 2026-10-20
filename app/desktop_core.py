"""Desktop data service. All ordinary queries run without a web server."""
import json
import os
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from app.database import Database
from app.parser import parse_aquadx
from app.calculations import summarize, plate_progress
from app.private_catalog import private_view
from app.local_tools import library_rows, filter_library, recommendations
from app.lxns import LxnsService, catalog_index
from app.desktop_storage import default_settings_path,default_profile,configured_directory,copy_profile,save_directory
from app.plate_catalogs import load_plate_catalogs, SCOPE_KEYS, SCOPE_LABELS
from app.recommendation_scopes import private_recommendations, cn_recommendations
from app.unified_catalog import UnifiedCatalog
from app.collection_metadata import load_names,read_xml_names
from app.archive_analysis import enrich_logs

ASSETS = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))


class DesktopCore:
    def __init__(self, directory=None,settings_path=None):
        self.settings_path=Path(settings_path) if settings_path is not None else default_settings_path()
        selected=directory if directory is not None else (configured_directory(self.settings_path) if settings_path is not None else default_profile())
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
        self.plate_catalogs = load_plate_catalogs(ASSETS/'data/plate_catalogs.json')

    def shared_catalog(self):
        # Resolve against live source snapshots; no persistent merged cache to become stale.
        if getattr(self,'_catalog_depth',0) and getattr(self,'_session_catalog',None) is not None:
            return self._session_catalog
        with self.lxns.catalog_guard:
            data=json.loads(self.lxns.catalog_path.read_text(encoding='utf-8'))
        registry=UnifiedCatalog(self.db.charts(),self.db.private_charts(),self.plate_catalogs,catalog_index(data),data.get('versions',[]))
        if getattr(self,'_catalog_depth',0):self._session_catalog=registry
        return registry

    @contextmanager
    def catalog_session(self):
        """Reuse one metadata snapshot during a synchronous UI refresh only."""
        self._catalog_depth=getattr(self,'_catalog_depth',0)+1
        try:yield
        finally:
            self._catalog_depth-=1
            if not self._catalog_depth:self._session_catalog=None

    def catalog(self,scope='private'):
        return self.shared_catalog().charts(scope)

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
        path = Path(path)
        text = path.read_text(encoding='utf-8-sig')
        if path.suffix.lower() == '.csv':
            from app.lxns_import import parse_lxns_csv
            payload = parse_lxns_csv(text)
        else:
            payload = parse_aquadx(json.loads(text))
        self.db.save_player(user_id, payload)
        return payload

    def overview(self, user_id):
        payload = self.db.player(user_id)
        if payload is None:
            raise ValueError('请先导入 AquaDX JSON 或落雪 CSV')
        registry = self.shared_catalog()
        charts = registry.charts('private')
        scopes = self.recommendation_scopes(payload,registry=registry)
        report = summarize(payload, charts,scopes['private']['currentVersion'])
        report['b50']=scopes['private']['b50']
        report['rating']=scopes['private']['rating']
        # Plate coverage uses the complete reference catalog, independently of B50.
        report['analysisPlates'] = summarize(payload,self.db.charts())['plates']
        resolved_scopes=registry.plate_scopes()
        report['plateScopes'] = {}
        for key, label in zip(SCOPE_KEYS, SCOPE_LABELS):
            scope = resolved_scopes[key]
            report['plateScopes'][key] = dict(plateCatalog=scope['charts'], plateRequirements=scope.get('requirements'),
                plateScopeLabel=label, plateDescription=scope['description'],
                plates=plate_progress(payload['best'], scope['charts'], scope.get('requirements')))
        report.update(report['plateScopes']['jp'])
        report['calculation']['plateScope'] = 'JP current / KarenBot CN requirements / JP historical; reference progress only'
        report['privateCatalog'] = private_view(payload['best'], charts, [], registry.cn_index)
        report['privateCatalog']['referenceCharts']=len(charts)
        report['b50Views'] = self.lxns.b50_views(payload, charts)
        report['recommendations'] = recommendations(report['best'])
        report['recommendationScopes'] = scopes
        report['catalogInfo']={'source':'统一曲库','privateCharts':len(charts),'cnCharts':len(registry.charts('cn'))}
        return report

    def recommendation_scopes(self,payload,private_version=None,registry=None):
        registry=registry or self.shared_catalog()
        return {'private':private_recommendations(payload,registry.charts('private'),[],[],private_version),
                'cn':cn_recommendations(payload,registry.cn_index,registry.cn_versions,registry.charts('cn'))}

    def library(self, user_id, scope='all', **filters):
        payload = self.db.player(user_id) or {'best': []}
        return filter_library(library_rows(self.catalog(scope), [], payload['best']), **filters)


    def archive(self,user_id):
        payload=self.db.player(user_id) or {}
        return payload.get('archive',{'schema':1,'available':False,'present':[],'sections':{},'warnings':[]})

    def archive_logs(self,user_id):
        return enrich_logs(self.archive(user_id),self.catalog('private'))

    def collection_names(self):
        return load_names(ASSETS/'data/collection_metadata.json',self.directory/'collection_metadata.json')

    def map_details(self):
        from app.map_metadata import load_map_details
        return load_map_details(ASSETS/'data/map_details.json',self.directory/'map_details.json')

    def activity_details(self):
        from app.activity_metadata import load_activity_details
        return load_activity_details(ASSETS/'data/activity_details.json',self.directory/'activity_details.json')

    def import_collection_names(self,directory):
        data=read_xml_names(directory)
        from app.map_metadata import read_map_details
        maps=read_map_details(directory)
        from app.activity_metadata import read_activity_details
        activity=read_activity_details(directory)
        activity_path=self.directory/'activity_details.json';activity_temp=activity_path.with_suffix('.json.tmp')
        activity_temp.write_text(json.dumps(activity,ensure_ascii=False),encoding='utf-8');activity_temp.replace(activity_path)
        map_path=self.directory/'map_details.json';map_temp=map_path.with_suffix('.json.tmp')
        map_temp.write_text(json.dumps(maps,ensure_ascii=False),encoding='utf-8');map_temp.replace(map_path)
        path=self.directory/'collection_metadata.json';temp=path.with_suffix('.json.tmp')
        temp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');temp.replace(path)
        return data
